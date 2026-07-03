# Deep-Research Prompt dr_L3-10 — MIXED-USE TOWER ENERGY REPORTING + NOVELTY POSITIONING (who did this before, and how did they report it?)

> SCOPE GUARD — READ FIRST. This is the **reporting-format and positioning** task of the Leg-3 set.
> Its two jobs: (a) how published mixed-use tall-building energy studies **attribute and report
> per-use energy** (so our Step-8/9 outputs use a recognizable format), and (b) a **novelty matrix** —
> who has driven multiple building uses from one harmonized, longitudinal occupancy source, so the
> 3rd-Journal paper's contribution claim is calibrated, not guessed. Do NOT re-survey mixed-use
> occupancy failure modes in general (foundational Prompt-10 report covers it), do NOT produce EUI
> bands (`dr_L3-02`/`dr_L3-03`), and do NOT evaluate the lunch-coupling decision (`dr_L3-07`). See
> `00_deep_research_prompts_Leg3.md` for shared facts and conventions.

---

## What this document is

A reporting-and-positioning brief. Our Step 8 produces, for geometry-identical PNNL Tall / SuperTall
prototypes in Montreal (NECB17 Z6) and Calgary (Z7A), an EUI table per **scenario × climate ×
channel** (Residential / Office / Retail / Hotel), plus load-shape and peak-timing metrics per channel,
with a floor-area sanity gate (per-channel EUI shares vs parsed occupiable shares within ±2 pp). Before
freezing that reporting format we want to know how the field slices mixed-use tower results — per-use
EUI on what area basis, how shared systems and service/MEP area (~52 % of gross here) are attributed,
and which figures reviewers expect. In parallel, the paper needs an honest novelty sentence: "first to
X" claims die in review when X was done in 2019.

## Role

UBEM / building-energy publications analyst. Ground the reporting side in published energy studies of
vertically mixed-use towers and of the DOE/PNNL prototype families (how multi-use prototype results are
tabulated; how EnergyPlus zone-level results get aggregated to use-level); ground the positioning side
in the occupancy-modelling literature that drives *multiple* building uses (time-use-survey-driven,
mobility-data-driven, sensor-driven), especially anything longitudinal (multi-decade or multi-wave) or
Canadian. Cast a wide net on (b): the claim to calibrate is specifically "national time-use diaries →
four use-specific channels → one mixed-use building, 2005–2030".

## Why this matters (so you scope correctly)

Two concrete consumers. First, the Step-8/9 output schema: if the field reports per-use EUI on
*conditioned area of that use* while we report on *occupiable share of gross*, every cross-study
comparison in the paper needs a conversion — better to adopt the convention now than to re-run
aggregation later. How studies handle **shared-system attribution** (one plant serving four uses) and
**service/MEP area** decides whether our channel EUIs are even comparable to published ones. Second,
the introduction: the contribution sentence and the related-work table come straight from the novelty
matrix; getting it sourced now prevents both under-claiming (missing that nobody has the longitudinal
piece) and over-claiming (missing a prior multi-use TUS-driven study).

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Mixed-use tall-building energy studies (the reporting survey)

| Study | Uses in one building | Occupancy source | Per-use energy reported? On what area basis? | Shared systems / core area attribution | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### Table 2 — Per-use attribution mechanics (how zone results become use-level results)

| Question | Field practice | Citation |
|---|---|---|
| Area basis for per-use EUI (use's conditioned area / use's gross share / whole-building) |  |  |
| Attribution of central-plant energy to uses (area-weighted, load-weighted, left unattributed) |  |  |
| Treatment of service/MEP/circulation area in per-use EUI (excluded, prorated, own category) |  |  |
| Reporting of per-use load shapes / peak timing (common figure types) |  |  |

### Table 3 — NOVELTY MATRIX (the positioning deliverable)

One row per prior study that drives ≥2 building uses with a data-derived occupancy signal. Columns are
the components of our claim — mark each YES/NO/partial.

| Study | ≥2 uses, one framework? | Time-use-survey-driven? | Longitudinal (multi-wave/decades)? | Forecast horizon? | Mixed-use single building? | Canadian? | Citation |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |

### Table 4 — Reviewer expectations (what mixed-use energy papers get criticized for)

| Criticism observed in reviews / literature | How our current design is exposed to it | Citation |
|---|---|---|
|  |  |  |
|  |  |  |
|  |  |  |

---

## Part C — Synthesis (format + positioning)

Give: (1) a recommended **Step-8/9 reporting specification**: area basis for per-channel EUI,
central-plant attribution rule, service/MEP treatment, and the 2–3 figure types the field expects for
per-use results — each choice with its precedent citation; (2) an explicit statement of whether our
planned "per-channel EUI share vs floor-area share, ±2 pp" sanity gate matches any published practice
or is project-novel (either is fine — we must label it correctly); (3) the **positioning verdict**
from Table 3: which components of "national time-use diaries → four channels → one mixed-use tower,
2005–2030" are genuinely unclaimed in the literature, and a draft one-sentence contribution statement
that survives the matrix; (4) the three closest prior works the related-work section must cite and
differentiate from.

## Output format (follow exactly)

1. **Lead with Tables 1–4 fully populated.**
2. Then Part C synthesis.
3. Inline citations; reporting-practice sources vs positioning sources kept distinct.
4. **"Confidence and caveats":** where the literature search is most likely incomplete.
5. **Reference list** — full citations, dates, URLs/DOIs.

## Hard requirements

- **The novelty matrix must include the closest-competitor studies even if they weaken our claim** —
  an over-claiming matrix is worse than none.
- **Every reporting-format recommendation needs a precedent citation** (or an explicit "no convention
  exists — project choice" label).
- **No fabricated precision;** flag GAPs. **Stay on topic** — reporting format and positioning only.
