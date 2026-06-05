# Step 8 — Results Figures: the 2022 → 2030 time-series load-shape shift
### Plot catalogue for the 2nd journal paper

---

## Purpose & framing

The novelty of this paper is **predicted occupancy *time-series* → energy *load shape* and *peak
timing***, not annual kWh. Every figure must therefore answer **"*when* does energy use change,
and by how much, as occupancy shifts from 2022 to 2030?"** — and contrast that with the flat
pre-COVID baseline (2005–2015).

**Design principles (apply to all figures):**
- **Time-of-day / time-of-year on the x-axis** wherever possible — the contribution is *shape*.
- **2022 vs 2030 is the headline contrast.** Pre-COVID years are context (flat baseline).
- **Monte-Carlo bands** (shaded 5–95% or ±1σ across the 50 HH) on every ensemble curve — the
  occupant diversity *is* the result.
- **Paired Δ** (within-household 2030 − 2022) is the statistical backbone — it cancels building +
  weather, so the change is *purely occupancy*.
- **Consistent colour key:** 2005/2010/2015 = greys (flat baseline) · **2022 = amber** ·
  **2030 = red/bold** (the break + its persistence). Heating = warm, Cooling = cool/blue.

**Data sources (what each figure is computed from):**
| Source | Produced by | Content |
|---|---|---|
| `BEM_Setup/SimResults_Step8/<arch>__<city>/<sample>/<year>/hourly_meters.csv` | 8C runner | 8760×meters (J): Electricity:Facility, InteriorLights, InteriorEquipment, Fan, Heating:EnergyTransfer, Cooling:EnergyTransfer, WaterSystems:EnergyTransfer |
| `cell_manifest.csv` (per cell) | 8C runner | sampled `SIM_HH_ID`s, hhsize, dtype, pr |
| `BEM_Schedules_{year}.csv` | Step 7 / 8A | the **occupancy + metabolic driver** (hourly, per HH) |
| 8E aggregation tables | 8E (to build) | per-cell mean/CI diurnal, peak metrics, paired Δ, stock-weighted ensemble |
| Stock weights | dwelling shares | SingleD 52.9% · MidRise 21.3% · OtherDwelling 13.0% · HighRise 12.8% |

---

## CORE figures (the novelty — these carry the paper)

### Fig 1 — The occupancy driver: diurnal AT_HOME shift
- **Type:** line plot, 24 h (00–23) on x, AT_HOME fraction on y; weekday panel + weekend panel.
- **Series:** 2005/2010/2015 (grey), 2022 (amber), 2030 (red).
- **Source:** `BEM_Schedules_{year}.csv` occupancy, averaged over households.
- **Message:** the *input* story — pre-COVID weekday curves overlap (flat); 2022 lifts the
  **mid-day** at-home fraction (WFH); 2030 persists/extends it. Motivates every energy figure.
  Annotate the mid-day (09–17h) band.

### Fig 2 — Diurnal electricity load shape, 2022 vs 2030 (HEADLINE)
- **Type:** mean 24-h electricity demand (W or kW) with **MC band**, 2022 vs 2030 overlaid.
- **Series:** 2022 (amber, band) vs 2030 (red, band); one representative archetype × CZ
  (e.g. SingleD × Montreal 6A), with a 2×2 small-multiple for the 4 archetypes.
- **Source:** `Electricity:Facility` hourly, diurnal-averaged across the 50 HH (mean ± 5–95%).
- **Message:** the money figure — the daily curve **reshapes**: higher/flatter mid-day plateau,
  changed evening ramp. Shade the area between the two curves.

### Fig 3 — Peak timing: hour-of-peak shift
- **Type:** distribution (violin or kernel density) of the **hour at which the daily peak occurs**,
  2022 vs 2030; plus a clock/polar inset of the mean peak hour.
- **Source:** per-HH per-day argmax hour of `Electricity:Facility` → distribution.
- **Message:** grid/DR relevance — does the peak **move** (earlier mid-day) or **flatten/spread**?
  This is the "*when*" claim made concrete. (Val §6.3.)

### Fig 4 — Paired Δ load by hour-of-day (the within-HH effect)
- **Type:** Δ-profile — mean of (2030 − 2022) per hour across the 50 paired HH, with a CI ribbon
  that should **exclude zero** in the mid-day hours; box/violin of Δ at peak hour.
- **Source:** per-HH paired difference of diurnal `Electricity:Facility` (same `SIM_HH_ID`).
- **Message:** the paired design's payoff — the change is statistically separable from 0 and
  **localised in time** (mid-day), with building + weather differenced out. (Val §6.1–6.2.)

---

## SUPPORTING figures (depth, robustness, context)

### Fig 5 — Diurnal-by-season small multiples
- **Type:** 2×3 grid: {heating season, shoulder, cooling season} × {electricity, heating load,
  cooling load}; 2022 vs 2030 curves with bands.
- **Source:** hourly meters split by season (Heating/Cooling:EnergyTransfer + Electricity:Facility).
- **Message:** the shape change is not uniform — separate the lighting/equipment (occupancy-driven)
  signal from the thermal (weather-driven) one.

### Fig 6 — Representative annual / weekly 8760-h trace
- **Type:** full-resolution time series — one representative week per season (or the full 8760 as a
  carpet/heatmap, hour-of-day × day-of-year), 2022 vs 2030.
- **Source:** raw `hourly_meters.csv` (single representative HH or cell mean).
- **Message:** demonstrates true 8760-h resolution (vs the conference/J1 annual scalar).

### Fig 7 — Δ modulated by climate zone
- **Type:** heatmap or grouped bars — paired Δ (peak / daytime energy) for the 6 cities
  (Toronto 5A → Winnipeg 7A), per archetype.
- **Source:** per-cell paired Δ from 8E.
- **Message:** the occupancy effect is larger in heating-dominated zones — the same behaviour
  costs more energy where the climate is harsher. (Val §6.4.)

### Fig 8 — Stock-weighted ensemble load shape + coincidence factor
- **Type:** stock-level diurnal load (weighting the 4 archetypes by 52.9/21.3/13.0/12.8%),
  2022 vs 2030, with the **coincidence/diversity factor** curve on a secondary axis.
- **Source:** stock-weighted aggregation across all cells (8E).
- **Message:** scales the single-building result to the **dwelling stock**; shows how occupant
  diversity smooths the aggregate peak (inherently stock-scale + time-series). (Val §5.4.)

### Fig 9 — Longitudinal trajectory 2005 → 2030 with the COVID break
- **Type:** trend lines of load-shape metrics (load factor, peak-to-average ratio, mid-day energy
  share, peak hour) across the 5 cycles; vertical marker at 2015→2022.
- **Source:** per-year metrics from 8E.
- **Message:** flat pre-COVID → **break at 2022** → **persistence to 2030**. Ties the load-shape
  story to the occupancy trajectory (WD 0.690/0.683/0.671/0.737/0.776). (Val §7.)

### Fig 10 — Annual EUI by archetype × CZ (SECONDARY / benchmark)
- **Type:** grouped bars, EUI (kWh/m²·yr) per archetype × city, 2022 vs 2030, with NRCan SHEU
  benchmark bands.
- **Source:** annual totals from hourly meters, normalised by floor area.
- **Message:** secondary "*how much*" check + plausibility vs published Canadian residential EUI.

---

## Figure → claim map (quick reference)

| Fig | Claim it supports | Val § |
|---|---|---|
| 1 | Occupancy *input* shifts mid-day (WFH persistence) | — |
| 2 | Daily **load shape** reshapes 2022→2030 (HEADLINE) | 5.1–5.2 |
| 3 | **Peak hour** shifts/flattens (grid relevance) | 6.3 |
| 4 | The shift is real, paired, and time-localised | 6.1–6.2 |
| 5 | Occupancy vs weather signals separated by season | 5 |
| 6 | True 8760-h resolution (the methodological leap) | 5 |
| 7 | Effect modulated by climate severity | 6.4 |
| 8 | Stock-scale ensemble + coincidence factor | 5.4 |
| 9 | Flat → COVID break → 2030 persistence | 7 |
| 10 | EUI plausibility (secondary) | 4.1 |

---

## Graphical abstract

Two layouts: **(A)** a tight headline composite for the journal's graphical-abstract slot, and
**(B)** a comprehensive *montage* that lays out a representative example of **every** candidate
plot — the **method** pipeline plus **all 10 result figures** — so the whole visual story and all
options are visible at a glance. Both prompts produce **representative/illustrative mockups with
synthetic data**, NOT real campaign results (those arrive after 8D); use them for a draft abstract
and figure-style alignment.

### A. Headline composite (3-panel flow)

```
[ 1. OCCUPANCY ]        →        [ 2. LOAD SHAPE ]        →        [ 3. PEAK ]
diurnal AT_HOME                  reshaped 24-h electricity         peak-hour shift +
2022 (amber) vs                  curve, 2022 vs 2030               flatter stock peak
2030 (red), midday               with MC band, midday              (clock dial / bar)
bump highlighted                 plateau shaded
```
Top banner: **"Predicted occupancy time-series → residential energy load-shape shift, 2022 → 2030."**
Bottom strip: the 5-cycle trajectory sparkline (2005→2030) with the COVID break marked.

### B. Full montage (method + all results)

```
TITLE: Predicting occupancy TIME-SERIES -> residential LOAD SHAPE & PEAK TIMING (2005 -> 2030)

METHOD ribbon ▸  GSS time-use diaries → ML calibration (J3 + Phase-8B raking) → 2030 forecast
                 → paired Monte-Carlo EnergyPlus (4 archetypes × 6 climate zones × 5 years,
                   frozen household frame) → 8760-h energy load shape

RESULTS grid (representative mini-plots):
  R1 Occupancy driver     R2 Diurnal load (HEADLINE)  R3 Peak-hour shift   R4 Paired Δ by hour
  R5 Diurnal by season    R6 8760-h carpet            R7 Δ by climate zone R8 Stock ensemble + CF
  R9 Longitudinal 2005→2030 (+ COVID break)           R10 Annual EUI (secondary)

TAKEAWAY: occupancy that stays home mid-day (WFH persistence) reshapes the daily load curve and
shifts/flattens the peak — quantified as a within-household Δ across climate zones.
```

---

## Graphical-abstract prompts (for a web-based image-generation LLM)

> **Note:** these produce **representative / illustrative mockups with synthetic, plausible data** —
> NOT the real simulation results. Use for a draft abstract and figure-style alignment only.
> Shared color key: **pre-COVID 2005–2015 = grey** (dashed), **2022 = amber**, **2030 = red**;
> heating = warm/red, cooling = blue. Clean sans-serif, white background, thin lines, no 3D.

### B-prompt — FULL MONTAGE (all plot examples: method + results)

Paste into a web LLM with image generation (ChatGPT-4o, Gemini, or an image model):

```
Create a clean, publication-quality scientific FIGURE MONTAGE / graphical abstract (large poster,
~16:11, white background, minimalist sans-serif, muted academic palette) for a building-energy
journal paper. It must lay out, as small labelled sub-panels, a representative example of EVERY
plot below. Use synthetic but realistic data. Color key everywhere: pre-COVID 2005-2015 = grey
dashed, 2022 = amber, 2030 = red; heating = warm red, cooling = blue. Thin clean lines, no 3D.

TITLE (top): "Predicting occupancy TIME-SERIES -> residential LOAD SHAPE & PEAK TIMING, 2005 -> 2030".

TOP "METHOD" RIBBON (left-to-right, 5 boxes joined by arrows, each a tiny icon + mini-chart):
  M1 "GSS time-use diaries" (clock + people icon; a tiny 24-h activity strip).
  M2 "ML calibration (occupancy model + raking)" (small neural-net icon; a mini 24-h occupancy
     curve shown corrected upward to match an observed marker).
  M3 "Forecast to 2030" (trend-arrow icon; a mini line extending past 2022 to 2030).
  M4 "Paired Monte-Carlo EnergyPlus" (house icon; a small 4x6 grid labelled "4 archetypes x
     6 climate zones", note "same households across all years = frozen frame").
  M5 "8760-h energy load shape" (a tiny annual load-curve icon).

RESULTS GRID below the ribbon (2 rows x 5 small panels), each a tiny titled chart with axes:
  R1 "Occupancy driver": 24-h at-home fraction (%); grey dashed pre-COVID low mid-day, amber 2022
     lifted, red 2030 highest mid-day; shade 09:00-17:00 "work-from-home".
  R2 "Diurnal electricity (HEADLINE)": 24-h demand (kW); amber 2022 and red 2030 each with a light
     Monte-Carlo uncertainty band; 2030 has a higher, flatter mid-day plateau; shade the gap.
  R3 "Peak-hour shift": a 24-h polar clock with two arrows (amber 2022, red 2030) at slightly
     different hours + a small histogram of the daily peak hour.
  R4 "Paired within-household Δ": Δ electricity (kW) vs hour around a zero line, with a shaded 95%
     CI ribbon that rises clearly above zero in the mid-day hours.
  R5 "Diurnal by season": a 3x3 micro-grid of tiny curves; rows = electricity / heating / cooling,
     columns = heating season / shoulder / cooling season; amber 2022 vs red 2030 in each cell.
  R6 "Annual 8760-h carpet": two side-by-side heatmaps (x = day of year 1-365, y = hour 0-23,
     color = kW), labelled 2022 and 2030, showing seasonal bands and a mid-day intensification in 2030.
  R7 "Δ by climate zone": a small heatmap, rows = 4 dwelling archetypes (SingleD, MidRise, HighRise,
     Other), columns = 6 zones (5A 5B 5C 6A 6B 7A), diverging red-blue cells = Δ peak kW (2030-2022).
  R8 "Stock-weighted ensemble + coincidence": a 24-h aggregate load curve (amber 2022 vs red 2030)
     weighted by the dwelling mix (SingleD 53%, MidRise 21%, Other 13%, HighRise 13%), with a small
     "coincidence factor < 1" annotation showing diversity flattening the stock peak.
  R9 "Longitudinal 2005->2030": a trend line of a load-shape metric over 5 year points - flat for
     2005-2015, a step up at 2022 (vertical dashed "COVID break" marker), staying elevated at 2030.
  R10 "Annual EUI (secondary)": grouped bars per dwelling archetype, amber 2022 vs red 2030,
     y = EUI (kWh/m2.yr).

BOTTOM takeaway strip: "Occupancy that stays home mid-day reshapes the daily load curve and
shifts/flattens the peak - quantified as a within-household change across climate zones."

Keep every sub-panel small but legible with a short title and axis labels; one shared legend
(2005-2015 grey, 2022 amber, 2030 red). Data is illustrative/representative.
```

### A-prompt — HEADLINE COMPOSITE (concise 3-panel)

For the tight journal graphical-abstract slot:

```
Create a clean, publication-quality scientific GRAPHICAL ABSTRACT (wide 16:6 banner, white
background, minimalist sans-serif, muted academic palette) for a building-energy journal paper.

TITLE across the top: "Predicted occupancy time-series -> residential energy load-shape shift,
2022 -> 2030".

Three panels left-to-right, connected by bold right-pointing arrows:

PANEL 1 - "Occupancy shift": a 24-hour line chart (x 0-24 h, y "At-home fraction" 0.5-0.9). A 2022
curve (amber) and a 2030 curve (red) slightly above it, both with a raised mid-day plateau
(09:00-17:00) versus a dipped pre-COVID grey dashed baseline. Shade/label 09-17h "work-from-home".

PANEL 2 - "Load shape reshapes": a 24-hour residential electricity demand curve (x 0-24 h,
y "Electricity demand (kW)"). Amber 2022 and red 2030 curves, each with a light Monte-Carlo band;
2030 has a higher, flatter mid-day plateau and a slightly softened evening peak; shade the gap.

PANEL 3 - "Peak timing": a small clock/dial OR compact bar chart showing the daily peak hour moving
and the stock peak flattening from 2022 to 2030 - label "peak flattens & shifts".

Bottom strip: a thin sparkline of five points (2005, 2010, 2015, 2022, 2030) flat for 2005-2015 then
stepping up at 2022 and staying elevated at 2030, with a vertical marker "COVID break".

Style: thin clean lines, no 3D, no clutter, legible axis labels, small legend
(2022 amber, 2030 red, pre-COVID grey). Data is illustrative/representative.
```

**Single panels:** to mock any one figure standalone, lift its `R#` line (or PANEL paragraph) and
ask for "a single labelled chart with axis ticks and a legend."

---

## Progress Log

| Date | Item | Result | Notes |
|---|---|---|---|
| 2026-06-02 | Plot catalogue drafted | ✅ DESIGN | 10 figures (4 core + 6 supporting) mapped to persisted `hourly_meters.csv` / `BEM_Schedules` / 8E tables + the val-doc claims; graphical-abstract composite + a representative-mockup LLM prompt. Built while the 8D-pilot runs. Real figures produced in 8E once the campaign data exists. |
| 2026-06-02 | Graphical abstract expanded → full montage | ✅ | Per request, the graphical-abstract section now offers (A) the tight 3-panel headline AND (B) a **full montage** prompt showing every plot example that conveys the novelty: a 5-step METHOD ribbon (GSS diaries → ML calibration → 2030 forecast → paired MC EnergyPlus → 8760-h load) + representative mini-panels for all 10 result figures (R1–R10). Single-panel reuse note added. Representative/synthetic data; for draft + figure-style alignment. |
| 2026-06-02 | **8E generator built + pilot-validated** | ✅ DONE | `Step8_docs/08_simulation_plots.py` implements the catalogue: two-pass summarize-on-read aggregation (→ `outputs_step8/agg/{agg_diurnal,agg_peak,agg_peak_hours,agg_annual,agg_meta}.csv`) + 10 figure fns + CLI (`--results-dir/--out/--figs/--rebuild-agg/--rep-cell`). Reuses `reporting.py` (`is_weekend` Jan1=Sun, diurnal/peak logic) + `plotting.py` (`calculate_eui`, `get_hourly_meter_data`, colors); Step-8 palette greys/amber/red; guards all 7 correctness rules (meter-by-name, no Facility double-count, EnergyTransfer=thermal label, circular peak hour, paired inner-join). **Validated on the in-progress N=3 pilot (105 runs, all ok):** agg sane (facility kWh/yr med ~10,006; peak hour 11–19; `is_weekend` 1/2/7 = T/F/T), **pairing exact** (Montreal SingleD ids {4434,82199,130999} in both 2022 & 2030, symmetric diff 0), correct-signed midday signal (12h Δ +3% vs 3h +1%). All 10 figs render PNG+PDF; Fig 1 (occupancy driver) + Fig 2 (headline diurnal) tell the WFH story cleanly; N=3 CIs wide as expected (tighten at N=50). Re-run on the full campaign with `--rebuild-agg`. **Open flag:** EUI median ~205 kWh/m²·yr is high — benchmark vs NRCan SHEU in 8F. |
