# An Occupancy-Aware Surrogate for EnergyPlus
### Learning the occupancy effect, not only the load, from paired runs on European time-use data — Paper 5 of the series
#### Full Pipeline Overview — one simulation campaign, one learned surrogate, three countries

Written 2026-09-28, the day the subject was ruled (D-5J-6 = form B4). This file is the one-page
picture; the step-by-step checklist is `5thJ_00_Occupancy_Surrogate_Pipeline.md` and the visual board
is `5thJ_CHECKLIST.html`. The history of how B4 was chosen (every idea kept, none deleted) lives in
`..\0_New_Ideas\` (the old `5J_docs_occ` folder, renamed 2026-09-28). Edit in place; never fork a copy.

---

## AIM

Time-use diaries say who is at home and what they do, and every household is different. To carry
that spread into a building or stock energy model you need thousands of EnergyPlus runs per building,
one per occupancy draw. That is too slow for a district, so most studies run one average schedule and
lose the spread.

Train a model on **paired EnergyPlus runs** (building and weather frozen, only the occupancy varied)
that predicts **hourly heating, cooling and electricity** from an occupancy sequence, a short building
description and the weather, and runs thousands of times faster than EnergyPlus.

The hard part, and the claim of the paper: a surrogate can match the total load very well while
**ignoring occupancy**, because occupancy moves the load only a little. So the surrogate is scored on
the **occupancy effect itself** (the difference between two households in the same building), and a
control model that is not allowed to see occupancy must fail that test.

> **Series position.** Paper 1 (CENTUS) = Italy, ML occupancy. 2J = Canada residential. 3J = four
> channels, mixed-use tower. 4J = HETUS, one language model, three countries (sole author).
> **Paper 5 (this doc) keeps the series spine (paired EnergyPlus, occupancy effect isolated) and turns
> the campaign itself into training data: a fast, checked stand-in for EnergyPlus.**

> **Authorship and data.** Sole author. Uses only material the author holds alone: the HETUS
> diaries for Spain, the UK and Italy (from 4J, under national agreements), the 4J activity-to-load
> tools, TABULA building parameters, ERA5 weather and OpenUBEM (the author's own repository). It does
> **not** use the 2J generator, the 1J to 3J runs, the CENTUS model or anything co-authored.

> **Time limit (decisive).** Speed GPU access ends with the Concordia postdoc, about **late October
> 2026**. The campaign and all training must finish before then; writing can follow.

> **Status convention.** ✅ DONE = artefact on disk and reviewed. 🟡 PARTIAL = artefact exists, part
> void or unreviewed. ⬜ NOT STARTED. 🔴 = must be read before acting. Status as of **2026-09-28**.

---

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  WP0 — LICENCE, NOVELTY, INVENTORY                        ⬜ next  (week 1) ║
║  HETUS licences ES / UK / IT allow a new paper?   <- O-1, blocks everything ║
║  He 2015, Dabirian, Li 2021 read: did anyone train this surrogate? (O-2)    ║
║  4J tools inventoried: diary -> schedules, TABULA IDFs, ERA5, chaining      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP1 — CAMPAIGN DESIGN AND PILOT                          ⬜        (week 1) ║
║  3 countries x ~3 climates x ~40 building variants x ~60 households         ║
║  = ~21,600 paired annual runs (DRAFT, sized by the pilot's measured time)   ║
║  pilot: 50 runs timed on Speed; CPU share agreed with 1J                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP2 — FULL CAMPAIGN ON SPEED (CPU)                       ⬜        (week 2) ║
║  sbatch arrays, 7-day walltime, every run checked (G5J.1)                   ║
║  splits SEALED by checksum: new households / new buildings / new country    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FREEZE section-7 gates by checksum; each gate SEEN FAILING first           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP3 — BASELINES AND SURROGATE (GPU)                      ⬜        (week 3) ║
║  B0 average schedule · B1 boosted trees (CPU) · S sequence model (A100)     ║
║  C  = same sequence model with occupancy shuffled (must FAIL G5J.3)         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP4 — ONE SCORING OF THE SEALED TEST SETS (RQ1-RQ3)      ⬜        (week 4) ║
║  load accuracy · occupancy effect · peaks and thermal-mass lag · country    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WP5 — WHAT THE SPEED BUYS (RQ4)                          ⬜        (week 4) ║
║  one European district, 100,000 occupancy draws by surrogate                ║
║  checked against EnergyPlus on a random subsample                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
   buffer to ~31 Oct 2026; GPU access ends; writing (no GPU needed) follows
```

---

## RESEARCH QUESTIONS

| RQ | Question in plain words | Work package |
|---|---|---|
| RQ1 | How close is the surrogate to EnergyPlus on hourly heating, cooling and electricity, for new households, new buildings and a country it never saw? | WP4 |
| RQ2 | Does it get the **occupancy effect** right: the difference between two households in the same building and weather, hour by hour and over the year? | WP4 |
| RQ3 | Where does it fail: peaks, the delay that thermal mass puts between presence and heating, cooling in mild climates? | WP4 |
| RQ4 | What does the speed buy: the spread of district demand under occupancy uncertainty, from 100,000 draws, and what it would have cost in EnergyPlus runs? | WP5 |

## SCOPE, DECIDED (working choices; confirm at WP0)

| Item | Decision |
|---|---|
| Subject | Form B4, occupancy-aware simulation surrogate (D-5J-6, ruled by the author 2026-09-28) |
| Authorship | Sole author |
| Occupancy data | HETUS diaries, one wave each: Spain 2009-10, UK 2014-15, Italy 2013-14 (held from 4J); France excluded as in 4J |
| Diary to schedule | 4J tools: presence, activity-driven equipment, lighting and hot water; day-to-year chaining as ruled in 4J |
| Buildings | TABULA residential archetypes per country, with sampled variants (insulation, glazing share, air-tightness, floor area, orientation) |
| Weather | ERA5 actual years, about three climates per country (DRAFT list at WP1) |
| Engine | EnergyPlus 23.1 through OpenUBEM, on Speed, `sbatch` only |
| Targets | Hourly heating, cooling and electricity per dwelling, one year |
| Truth | Held-out EnergyPlus runs; no measured data, no people in the scoring |
| Not in scope | Canada, the 2J generator, harsh events, power failure, language models, measured meter data |

## VALIDATION GATES (DRAFT; frozen by checksum at the end of WP2)

| Gate | What | DRAFT threshold |
|---|---|---|
| G5J.1 | Campaign integrity | every planned run present, "EnergyPlus Completed Successfully", 0 severe errors; run count = plan; a resume check that moves outputs away sees the plan count drop |
| G5J.2 | Load accuracy (new households, new buildings) | hourly CV(RMSE) ≤ 30 % and absolute NMBE ≤ 10 % per target (ASHRAE Guideline 14 hourly bands, used as a reference) |
| G5J.3 | Occupancy effect | on paired differences between two households in one building and weather, per end use and per dwelling class: R² ≥ 0.5 on hourly differences, annual difference sign right in ≥ 80 % of pairs above the noise floor (set from replicate runs of identical input), and the surrogate beats B1 with a cluster-bootstrap interval that excludes 0; an end use below the floor is NOT_EVALUABLE |
| G5J.4 | Occupancy-blind control | control C (occupancy shuffled across runs) must FAIL G5J.3; if it passes, G5J.3 measures nothing and is withdrawn |
| G5J.5 | Peaks | daily electricity peak hour within ±1 h on ≥ 70 % of days |
| G5J.6 | New country | leave-one-country-out scores reported, not gated |
| G5J.7 | Speed | time per dwelling-year against EnergyPlus on the same node, reported, not gated |

A gate that cannot be computed is NOT_EVALUABLE, never PASS. A crashed section is NOT_EVALUABLE in the
SUMMARY too. Each gate must be seen failing under one named perturbation before it is trusted.

## WHAT MAKES IT NEW (to be confirmed at WP0, O-2)

A learned stand-in for EnergyPlus that takes a **stochastic occupancy and activity sequence** as input,
trained on a **paired frozen-frame campaign**, and scored on the **occupancy effect** with an
occupancy-blind control that must fail. Known neighbours (read at source 2026-09-28, table in
`Resources/nearest_work/NEAREST_WORK.md`): He et al. 2015 and Dabirian et al. 2024 couple stochastic
occupancy to EnergyPlus and **do not train a surrogate**; Li, Bae and Im 2021 (ORNL) train an EnergyPlus
surrogate for one test building to study sensor faults (abstract read: 107 inputs, not listed; full text
still unreachable); Park and Park 2023 score surrogates on the savings between design changes (**the
precedent for our difference score**; our claim is its occupancy version, with a blind control); Pan et al.
2024 and Govindarajan et al. 2025 are hourly stock-scale surrogates with no occupancy input; Yoo, Clayton
and Yan 2023 (urban surface temperature, abstract only, from RT43). Not claimed: "first building energy
surrogate", "first hourly residential stock surrogate", "first to score a surrogate on differences".

## KEY DESIGN DECISIONS SUMMARY

| Decision | Rationale |
|---|---|
| Score the occupancy effect, not only the load | A surrogate can match total load while ignoring occupancy; 4J found the occupancy effect on heating small |
| An occupancy-blind control must fail | A gate that the blind model passes proves nothing |
| Paired frozen-frame campaign | Isolates the occupancy effect, the series spine since 1J |
| Test sets sealed before any training | No threshold or model choice is tuned after seeing test rows |
| Model family chosen on the development split only | Winner pinned (code hash, seed) before the test is opened |
| Boosted trees as the honest baseline | If the sequence model does not beat trees, the GPU adds nothing, and that is reported |
| European data, sole author | No co-authored input anywhere in the chain |
| Campaign size set by measured pilot time | Not by a report's estimate |
| Replicate runs set a truth noise floor | 4J saw identical EnergyPlus input give different heating values |
| Lessons from 1J to 4J applied | 16 lessons listed in the checklist, section "Lessons carried" |

## OPEN DECISIONS AND ITEMS

* **O-1 🔴** Do the HETUS agreements for Spain, the UK and Italy allow use in a new paper? Read each
  agreement. A country whose terms do not allow it is dropped; the design runs on two.
* **O-2** Novelty: He et al. 2015 and Dabirian et al. 2024 read at source (no surrogate); outside search
  RT45 checked 2026-09-28 (`Prompts/deepResearch/VETTING_RT45.md`): mixed, both controls pass, Park and
  Park 2023 kept as the difference-score precedent, all its "nobody has" verdicts unsupported (no queries
  logged). Li 2021 read at abstract level only (low risk). ✅ CLOSED 2026-09-28 by the author on that
  abstract; full-text re-check and one logged search for P1 and P4 at Step 8.
* **O-3** Campaign size and time per run: set by the WP1 pilot.
* **O-4** Surrogate input window and output horizon (DRAFT: 7-day history in, next 24 hours out, rolled
  over the year).
* **O-5** CPU share on Speed while 1J draws finish.
* **O-6** Venue, decided when RQ1 and RQ2 results exist.
* **O-7** How UK aggregate gate results reach the manager, since the assistant never opens UK-derived
  files (UKDS licence clause 5). Until the author rules: the author reads the UK SUMMARY lines.
  Recommend: the author asks UKDS for written permission for aggregate results only.
* **D2-1** (from the Step 1 inventory, 2026-09-28 night) Climates: only one ERA5 city per country exists
  (Madrid, London, Bologna). Recommend making two more ERA5 files per country with the existing OpenUBEM
  path; fallback one city per country. Detail: `Step2_docs/5thJ_02_campaignDesignPilot.md`, 2F.
  Checked 2026-09-28 late night: the path works for any city (small 5J copy of two scripts; 8 h to 2
  days of download). Recommended cities: Valencia + Seville, Birmingham + Manchester, Turin + Milan
  (4J best-fit station plus one large city per country; all inside the building regions).

## LIMITATIONS — pointer, not a copy

Written as they arise in the checklist Progress Log. Already known: the truth is EnergyPlus, so the
surrogate is only as good as the archetypes and the engine; no measured data; one wave per country;
archetype boxes, not real geometry, except the WP5 district; no Canadian case.

## COMPANION DOCUMENTS

* `5thJ_00_Occupancy_Surrogate_Pipeline.md` — the build checklist and Progress Log (the state).
* `5thJ_CHECKLIST.html` — the board.
* `Step1_docs/` to `Step8_docs/` — one spec (`5thJ_0N_<name>.md`) and one validation plan (`_val.md`)
  per step, written 2026-09-28.
* `Prompts/manager/5J_manager_prompt_RESUME.md` — the handover prompt for a new manager session.
* `..\0_New_Ideas\PROMPTS\New_ideas_Manager_Prompt.md` — how B4 was chosen; RT43, RT44 and their vetting.
* `..\4J_docs_occ\` — the HETUS files, the diary-to-schedule tools and the TABULA IDF builder reused here.
