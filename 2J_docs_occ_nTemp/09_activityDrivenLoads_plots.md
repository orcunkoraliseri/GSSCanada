# Step 9 — Results Figures: activity-driven, end-use-resolved load shape
### Plot catalogue for the supplementary (SI/Appendix) section of the 2nd journal paper

> **Companion to `08_simulation_plots.md`.** Step 8 carries the headline story (*predicted occupancy
> time-series → load shape & peak timing, 2022→2030*). Step 9 is the **supplementary** deepening:
> *predicted **activity** time-series → **end-use-resolved** load shape*. These figures must always
> show what the **activity** signal adds **on top of** the presence-only Step-8 baseline — so the
> defining contrast here is **activity-driven vs presence-only**, paired on the same households.
>
> **Output target:** all figures render to `2J_docs_occ_nTemp/outputs_step9/figures/`, aggregates to
> `2J_docs_occ_nTemp/outputs_step9/agg/` (mirrors the Step-8 `outputs_step8/{figures,agg}` layout).

---

## Purpose & framing

Step 8 already answers *"when does energy use change as occupancy shifts 2022→2030?"* Step 9 answers a
sharper question: **"*which* end uses move, and *why* — because of *what people are doing*, not just
*whether they're home*?"** Every figure must therefore make the **activity bend visible** against the
presence-only baseline, and keep the yearly totals **honest** against the NRCan SHEU 2019 anchors.

**Design principles (apply to all figures):**
- **Headline contrast = activity-driven vs presence-only**, paired on the **same households** (the
  Step-8 frozen frame). This cancels building + weather → the difference is *purely behaviour*.
- **Secondary contrast = 2022 vs 2030.** The prototype's key claim is that the longitudinal
  differential is **far sharper in the activity model** (+35.4% vs +0.4% presence-only) — show both.
- **Time-of-day on the x-axis** wherever possible — the contribution is *shape* and *peak timing*.
- **Monte-Carlo bands** (5–95% or ±1σ across the n=20 / n=50 HH) on every ensemble curve.
- **SHEU honesty:** any annual-total figure carries the SHEU anchor line + the **±10%** gate band.
- **Consistent keys:**
  - *Treatment* — **activity-driven = solid bold colour**, **presence-only baseline = grey dashed**.
  - *Year* — **2022 = amber**, **2030 = red** (same key as Step 8).
  - *End use* — cooking = warm orange · dishwasher = teal · washer/dryer = blue · TV/entertainment =
    purple · PC/office = green · care+DHW = pink · lighting = yellow · **baseload = neutral grey band**.

**Important — where end-use resolution lives.** EnergyPlus aggregates the bent plug loads into a
**single** `InteriorEquipment` meter, so per-appliance curves (cooking vs dishwasher vs TV …) are **not**
recoverable from the meters. The end-use-resolved figures (Fig 1, 7) are therefore computed from the
**activity-driven schedule decomposition** — the `Equipment_Fraction` end-use components emitted by
`activity_loads.py` / `07_aug_to_bem.py` (§9.2 crosswalk) — i.e. the *input* side. The **meter** figures
(Fig 2, 4, 5, 6) validate the **realized total** equipment + lighting load that E+ actually produced.
State this split in the SI so the end-use breakdown is read as model-structure, not a measured meter.

**Data sources (what each figure is computed from):**
| Source | Produced by | Content |
|---|---|---|
| `SimResults_Step9/<arch>__<city>/<treatment>/<sample>/<year>/hourly_meters.csv` | Step-9 cluster run | 8760×meters (J): `Electricity:Facility`, `InteriorLights`, `InteriorEquipment`, Fan, Heating/Cooling:EnergyTransfer, WaterSystems — for **both** `treatment ∈ {baseline, activity}` |
| `cell_manifest.csv` (per cell) | cluster run | sampled `SIM_HH_ID`s (identical across treatments + years), hhsize, dtype, pr — the **paired key** |
| `BEM_Schedules_{year}.csv` (activity) | Step 7 / `07_aug_to_bem.py` | the **activity driver**: `Equipment_Fraction`, `Lighting_Fraction` (+ end-use components), hourly per HH |
| Activity diary (`act30`, 14 codes) | Step 4 aug | the behaviour shape behind the bend (for Fig 1/7/8 decomposition + the sleep/away zero-check) |
| SHEU 2019 anchors (region × dwelling) | NRCan / §9.4 | calibration targets + ±10% gate (Fig 6); SingleD equip ≈3,700 / lighting 1,262 kWh·yr |
| 9-fig aggregation tables | Step-9 plot generator | per-cell mean/CI diurnal, peak-hour dists, paired Δ (activity−baseline AND 2030−2022), SHEU calibration table |
| Stock weights | dwelling shares | SingleD 52.9% · MidRise 21.3% · OtherDwelling 13.0% · HighRise 12.8% |

**Sample:** first pass = the **3-cell / n=20** frozen bigger-test sample (incl. SingleD Winnipeg_7A,
HighRise Montreal_6A) on Speed; full pass = **24-cell / n=50** after Step 8 finishes. Figures marked
**[full-grid]** below are meaningful only on the 24-cell refresh.

---

## CORE figures (the Step 9 novelty — these carry the supplementary section)

### Fig 1 — The activity driver: end-use fraction stack (the input story)
- **Type:** stacked-area, 24 h on x, normalized load fraction on y; weekday + weekend panels.
- **Series:** the activity-driven end-use components (cooking, dishwasher, washer/dryer, TV/ent,
  PC/office, care+DHW, lighting) stacked above the flat **baseload** band.
- **Source:** `Equipment_Fraction` end-use decomposition (`activity_loads.py` / §9.2), averaged over HH.
- **Message:** the *input* story — "what people are doing" maps to *which* load and *when* (morning
  cooking + telework PC, evening cooking + TV). Motivates every meter figure. **Activity model only**
  (the presence-only baseline has no end-use structure — that's the point).

### Fig 2 — Equipment load shape: activity vs presence-only (HEADLINE)
- **Type:** mean 24-h `InteriorEquipment` demand (kW) with **MC band**, activity (solid) vs baseline
  (grey dashed), overlaid; one representative cell (SingleD × Winnipeg 7A), 2×2 small-multiple for cells.
- **Source:** `InteriorEquipment` hourly, diurnal-averaged across the HH (mean ± 5–95%).
- **Message:** the money figure — behaviour **reshapes** the plug-load curve and **moves the peak**
  (prototype: equipment peak shifts ~11 h earlier, **baseline h18 → activity h7** = breakfast cook +
  dishwasher + morning telework). Shade the gap; annotate the morning peak.

### Fig 3 — Equipment peak-hour shift (activity vs baseline)
- **Type:** distribution (violin/KDE) of the **hour of daily equipment peak**, activity vs baseline;
  polar-clock inset of the mean peak hour for each.
- **Source:** per-HH per-day argmax hour of `InteriorEquipment` → distribution, by treatment.
- **Message:** the peak-timing claim made concrete (the h18→h7 move). **Guard:** the h7 morning peak
  must be a *real* behavioural signal after the RF1 dishwasher de-bounce — if it persists, it is the
  finding; if it collapses, it was the queue artifact. Label which, per the validation gate.

### Fig 4 — 2022→2030 differential: activity vs presence-only (THE NOVELTY)
- **Type:** paired Δ-by-hour — mean (2030 − 2022) per hour across paired HH, **two panels/overlays**:
  activity model vs presence-only baseline; plus a single bar of the **annual Δ%** for each.
- **Source:** per-HH paired diurnal difference of `InteriorEquipment`, computed within each treatment.
- **Message:** the core supplementary claim — the activity time-series makes the longitudinal change
  **visible** where presence-only nearly **flattens** it (prototype **+35.4% vs +0.4%**, ~88× sharper).
  This is *why* Step 9 sharpens the paper's novelty. CI ribbon should exclude zero for activity, hug
  zero for baseline.

### Fig 5 — Lighting load shape: SHEU-calibrated activity vs IDF daylight-only
- **Type:** mean 24-h `InteriorLights` demand (kW) with MC band — activity-driven SHEU-calibrated
  (solid) vs the IDF daylight-only default (grey dashed).
- **Source:** `InteriorLights` hourly (Step-9 run) vs the Step-8 daylight-gated default.
- **Message:** the daylight-only default **badly under-counts** (prototype ≈151 kWh vs the 1,262 kWh
  SHEU anchor, ~8.3×); activity × daylight × SHEU-scale fixes both the **level** and the **evening
  shape** (active-occupancy peak ≈ h16–20). Shows the SHEU scale is essential, not cosmetic.

---

## SUPPORTING figures (calibration honesty, robustness, sanity)

### Fig 6 — SHEU calibration benchmark (the ±10% gate)
- **Type:** grouped bars — simulated **annual** equipment & lighting per cell (region × dwelling)
  against the SHEU anchor, with the **±10%** acceptance band shaded.
- **Source:** annual totals from `InteriorEquipment`/`InteriorLights`; anchors from §9.4.
- **Message:** the honesty check — shape comes from behaviour, **totals come from SHEU**. Every cell
  must land in-band (prototype hit <0.5%). This is the gate the validation step enforces.

### Fig 7 — End-use-resolved diurnal stack, 2022 vs 2030 [decomposition]
- **Type:** two stacked-area panels (2022 | 2030) of the end-use components, or a Δ-stack of (2030−2022).
- **Source:** the `Equipment_Fraction` end-use decomposition per year.
- **Message:** *which* end uses drive the 2022→2030 shift (e.g. more mid-day cooking + PC/office from
  WFH persistence) — the behavioural mechanism behind Fig 4's sharper differential.

### Fig 8 — Sleep/away zero-check (validation, not a result)
- **Type:** diurnal overlay — mean activity-driven equipment fraction vs mean presence and mean sleep
  fraction; shade sleep (code 5) and away (codes 4/12/13) windows.
- **Source:** `Equipment_Fraction` + `act30` diary.
- **Message:** confirms the bent load drops to **baseload-only** during sleep/away (no plug load when
  nobody is doing anything) — the physical-sanity gate. Baseload band stays flat 24/7 (never zeroed).

### Fig 9 — Co-presence scaling effect (robustness)
- **Type:** per-capita equipment energy vs household size (1→≥5), shared vs personal devices.
- **Source:** annual `InteriorEquipment` per HH, grouped by hhsize; EFF curve (1.0/1.4/1.7/1.9/2.0).
- **Message:** confirms the **sub-linear** shared-device assumption is active (multi-person homes don't
  linearly multiply the TV/oven), so the model doesn't over-predict large households (§9.3).

### Fig 10 — Stock-weighted activity-vs-presence load shape [full-grid]
- **Type:** stock-level diurnal equipment+lighting load (weight the 4 archetypes 52.9/21.3/13.0/12.8%),
  activity vs baseline, 2022 vs 2030.
- **Source:** stock-weighted aggregation across all cells (24-cell refresh).
- **Message:** scales the single-building activity effect to the **dwelling stock** — mirrors Step-8
  Fig 8. **Meaningful only on the full 24-cell / n=50 grid** (after Step 8); the 3-cell pass is a draft.

---

## Figure → claim map (quick reference)

| Fig | Claim it supports | Side | Sample |
|---|---|---|---|
| 1 | Activities map to *which* end use, *when* (the input) | schedule | 3-cell |
| 2 | Behaviour reshapes the plug-load curve + moves the peak (HEADLINE) | meter | 3-cell |
| 3 | Equipment peak shifts h18→h7 (peak timing) | meter | 3-cell |
| 4 | 2022→2030 differential **sharper** in activity than presence-only (NOVELTY) | meter | 3-cell |
| 5 | Lighting level + evening shape fixed vs daylight-only default | meter | 3-cell |
| 6 | Annual totals stay within ±10% of SHEU (honesty gate) | meter | 3-cell |
| 7 | *Which* end uses drive the 2022→2030 shift | schedule | 3-cell |
| 8 | Zero plug load during sleep/away; baseload never zeroed (sanity) | schedule | 3-cell |
| 9 | Sub-linear co-presence — no over-prediction in large homes | meter | 3-cell |
| 10 | Stock-scale activity-vs-presence effect | meter | **full-grid** |

---

## Mockup composite (for a draft SI figure)

```
[ 1. WHAT THEY DO ]      →      [ 2. PLUG-LOAD RESHAPES ]      →      [ 4. SHARPER 2022→2030 ]
end-use fraction stack          activity (solid) vs presence-           paired Δ-by-hour: activity
(cook/dish/TV/PC/light)         only (grey dashed) 24-h kW;             ribbon lifts off zero,
over 24 h + baseload            peak moves h18 -> h7                    baseline hugs zero (+35% vs +0.4%)
```
Banner: **"Predicted activity time-series → end-use-resolved load shape (supplementary to the
occupancy→load result)."** Bottom strip: SHEU ±10% calibration tick (Fig 6) so the totals read honest.

> Reuse the Step-8 graphical-abstract LLM prompt style from `08_simulation_plots.md` if a synthetic
> mockup is wanted; data here is illustrative until the cluster run lands.

---

## Generator notes (for the plot-build employee, later)

- Build a `09_activityDrivenLoads_plots.py` modelled on `Step8_docs/08_simulation_plots.py`: two-pass
  summarize-on-read aggregation → `outputs_step9/agg/`, one fn per figure, CLI
  (`--results-dir/--out/--figs/--rebuild-agg/--rep-cell/--treatment`). **Reuse** `reporting.py` +
  `plotting.py` (don't re-implement `is_weekend`, diurnal/peak, EUI, colours).
- **Pairing is the backbone:** inner-join on `SIM_HH_ID` across {baseline,activity} and across
  {2022,2030}; assert the id sets match (symmetric diff = 0) before any Δ.
- **No double-count:** never sum `Electricity:Facility` with its components; metabolic (people heat)
  is separate from `InteriorEquipment` — don't conflate.
- Figures + claim map above are the spec; honour the design principles (treatment/year/end-use keys).

---

## Progress Log

| Date | Item | Result | Notes |
|---|---|---|---|
| 2026-06-03 | Step-9 plot catalogue drafted | ✅ DESIGN | 10 figures (5 core + 5 supporting) for the supplementary section, mapped to the cluster-run `hourly_meters.csv` (per treatment/year) + the activity `Equipment_Fraction` decomposition + SHEU §9.4 anchors. Headline contrast = **activity vs presence-only** (paired), secondary = 2022 vs 2030 (sharper differential = the novelty). Outputs → `outputs_step9/{figures,agg}`. Companion to `08_simulation_plots.md`. Generator (`09_activityDrivenLoads_plots.py`) built later, after the cluster run produces data. |
