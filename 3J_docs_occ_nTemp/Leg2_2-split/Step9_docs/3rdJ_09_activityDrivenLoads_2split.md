# 3J Leg-2 · STEP 9 — Activity-Driven End-Use Loads (Both Channels)
### Residential (AT_HOME) + Office (AT_WORK) — equal treatment, matched evaluation

> **Status:** DONE 2026-07-02 (post office-WFH-fix re-run, job 1058662 — 10 PASS / 1 WARN / 0 FAIL,
> G8o confirms WFH-modulation live). Aggregate-depth unification of the two-channel
> activity-driven end-use loads. **Both channels are first-class here — same analyses, same rigor,
> each on its own physically-correct benchmark and parameters.** No re-simulation: reads the
> existing §8D aggregation tables (`Step8_docs/outputs_step8/agg/`, re-aggregated 2026-07-02).

---

## 0. WHY THIS STEP EXISTS (and why it is bi-channel)

Step 8 produced the two-channel EnergyPlus campaign and validated it end-to-end. Step 9 is the
**energy-demand reading** of that campaign: how occupancy/activity reshapes the electricity-using
end uses (**lighting + equipment/plug loads**) and whether the resulting intensities are physically
plausible against an independent benchmark — **done identically for the residential and office
channels**.

**Design principle — equal importance, not identical parameters.** Residential and office are
different building physics, so they legitimately use different parameters and different benchmarks.
What is held *equal* across the two channels is **attention, prominence, and evaluation rigor**:
every analysis below is computed and reported for *both* channels, each judged against its own
appropriate reference, to the same standard. Neither channel is "the appendix."

| Channel | Coupling | Headcount | BEM action | EUI benchmark | MC design |
|---|---|---|---|---|---|
| **Residential (AT_HOME)** | Lights + Equipment ← presence | `HHSIZE` × schedule | **REPLACE** baseline schedule | **NRCan SHEU 2019** (per dwelling type) | paired Monte-Carlo, N=50 |
| **Office (AT_WORK)** | Lights + Equipment ← presence | NECB per-m² density | **MODULATE** code density | **NECB2020 / 90.1-2019 DOE-PNNL prototype** (SCIEU stock as context) | deterministic |

> These rows *differ on purpose*. Forcing them to match would be physically wrong, not fair. The
> parity is in the columns being **filled for both** and evaluated equally hard (see §5 ledger).

---

## 1. SCOPE & DEPTH (honest statement)

This Step 9 operates at **aggregate end-use depth**: presence-driven coupling of the two
electricity end uses (lighting, equipment/plug) plus an **aggregate site-EUI** calibration against
an independent benchmark, for both channels.

It is deliberately **shallower than 2J's residential Step 9**, which was a fully *activity-resolved*
end-use model (8 end uses, a 14-activity→appliance crosswalk, co-presence scaling, and per-end-use
SHEU calibration; see `2J_docs_occ_nTemp/09_activityDrivenLoads.md`). Aggregate depth is the level
at which **parity is genuinely achievable**, because:

- The deep activity-resolved residential model already exists and is validated as **Leg-1
  provenance** (2J Step 9, 48/48 SHEU PASS) — re-running it inside Leg 2 would duplicate published
  work and perturb Leg-1 figures.
- The **office channel has no per-end-use benchmark** equivalent to SHEU — only an aggregate NECB /
  SCIEU site-EUI band. Pushing office to activity-resolved depth would make it the hand-wavy channel
  — the *opposite* of the parity requested. An office activity-resolved extension (with a bespoke
  office end-use benchmark) is a **Leg-3 candidate**, not a Leg-2 deliverable.

So Leg-2 Step 9 meets both channels at the aggregate level, where each has a defensible, independent
benchmark and can be evaluated with equal rigor.

---

## 2. METHOD

### §9.1 Presence-driven coupling of lighting + equipment (both channels)

Implemented in Step 8 (decision **OD-8B**: Lights/Equipment folded into the simulation for *both*
channels; HVAC/DHW held at NECB/ASHRAE code baseline; peak densities never modified). The two end
uses follow the presence track `O(t)` with safety/standby floors:

| End use | Formula | Residential floor | Office floor |
|---|---|---|---|
| **Lighting** | `L(t) = max(Lmin, O(t))` | `Lmin = 0.15` | `Lmin = 0.15` |
| **Equipment / plug** | `P(t) = Pbase + (1 − Pbase)·O(t)` | `Pbase = 0.20` | `Pbase = 0.20` |

- Residential `O(t)` = AT_HOME presence (from the Step-7 REPLACE schedule); headcount = `HHSIZE`.
- Office `O(t)` = AT_WORK presence multiplier (Step-7 MODULATE); headcount = NECB per-m² density.
- Floors are physical, not cosmetic: lights never go fully dark (egress), plug loads never hit zero
  (networking/standby). Verified on the injected CSVs in Step-8 validation §2.6/§2.7.

### §9.2 Aggregate EUI calibration (both channels, each vs its own benchmark)

Annual **site** EUI per run = `eSim_bem_utils_3J.plotting.calculate_eui(conn)` = annual site energy
(kWh) ÷ Net Conditioned Area (fallback total). Each channel's median EUI is gated against an
independent, literature-sourced band:

**Residential — NRCan SHEU 2019** (site energy, kWh/m²; from 2J deepResearch
"Canadian Residential Energy-Use Intensity by Dwelling Type"):

| Archetype | Central | Band [lo–hi] |
|---|---|---|
| SingleD | 155.6 | 130.6 – 186.1 |
| OtherDwelling | 144.4 | 136.1 – 186.1 |
| MidRise | 144.4 | 111.1 – 216.7 |
| HighRise | 130.6 | 113.9 – 147.2 |

**Office — NECB2020 / ASHRAE 90.1-2019 DOE-PNNL Tall/SuperTall prototype** (as-modelled band; from
`Step8_docs/deepResearch/…As-Modelled Bands.md`). Our office IDFs **are** these code-compliant
prototypes, so the prototype's own expected EUI is the pass criterion:

| Reference | Central | Band [lo–hi] | Role |
|---|---|---|---|
| As-modelled PNNL prototype | 135 | 100 – 200 | **PASS criterion** |
| SCIEU-2019 / CEUD-2023 measured stock | 230 | 170 – 360 | INFO context (aged vintages run higher) |

> Basis caveat (applies to residential): our EUI denominator = Net Conditioned Area *including*
> basement; SHEU is heated area *excluding* basement, so conditioned-basis figures read higher —
> this makes SingleD land above its SHEU band (a documented, non-blocking WARN, not an error).

---

## 3. INPUTS

| Input | Path | Role |
|---|---|---|
| §8D annual rollup | `Step8_docs/outputs_step8/agg/agg_annual.csv` | per-run site EUI + energy, `channel`/`scenario` |
| §8D peak rollup | `…/agg/agg_peak.csv` | per-run peak magnitude + hour |
| §8D diurnal rollup | `…/agg/agg_diurnal.csv` | meter × season × daytype × 24h (both channels) |
| §8D meta | `…/agg/agg_meta.csv` | per-run archetype / city / envelope / sample |
| SHEU bands | encoded `SHEU_EUI_BANDS` (validator) | residential EUI reference |
| NECB/SCIEU bands | encoded `OFFICE_EUI_BAND`, `OFFICE_EUI_EMPIRICAL` | office EUI reference |

---

## 4. RESULTS (both channels, side by side)

*Numbers below are the ACTUAL Step-9 analysis output (post-fix re-run job 1058662, 2026-07-02,
`outputs_step9/*.csv`), not transcribed from the §8E log. They supersede the pre-fix job-1055064
numbers (office channel simulated without working WFH modulation — see Progress Log 2026-07-02).
Where a Step-9 number differs from §8E it is because Step 9 uses a per-run summary of
`agg_annual`/`agg_peak` (e.g. mean of per-run daily-peak hours) whereas §8E read the mean diurnal
profile — both are defensible; the Step-9 values are the ones reported here.*

### §R1 — End-use intensity vs benchmark (EUI)  ✅ solid, both channels

| Channel | Unit | n | Median EUI (kWh/m²) | Band | Verdict | Lights / Equip share |
|---|---|---|---|---|---|---|
| Residential · SingleD | dwelling | 2100 | **212.5** | SHEU 130.6–186.1 | **WARN** (basis: conditioned incl. basement) | 0.16 / 0.61 |
| Residential · OtherDwelling | dwelling | 2100 | 140.4 | SHEU 136.1–186.1 | **PASS** | 0.17 / 0.62 |
| Residential · MidRise | dwelling | 2100 | 177.3 | SHEU 111.1–216.7 | **PASS** | 0.19 / 0.28 |
| Residential · HighRise | dwelling | 2100 | 142.9 | SHEU 113.9–147.2 | **PASS** | 0.28 / 0.40 |
| **Office (all)** | tower | 252 | **172.6** | PNNL 100–200 | **PASS** | n/a (see below) |
| Office · Knowledge / Public / Sales | tower | 84 each | 172.7 / 172.6 / 172.6 | PNNL 100–200 | **PASS** | n/a |

Ordering sanity: SingleD (212.5) ≥ HighRise (142.9) — plausible. Office 172.6 sits in-band, on the
high side of the prototype central (135) — consistent with tall towers (high internal loads +
envelope), and correctly **below** the ≈230 empirical stock. The three office archetypes have
near-identical medians (172.6–172.7) because at the annual EUI level the tower's energy is dominated
by envelope + HVAC (unchanged across archetypes); archetype differences show up in the *shape*, not
the annual intensity.

The HTML report's Figure 1 caption now also states each archetype's computed **% error vs its
benchmark's central estimate**: Residential SingleD +36.6%, OtherDwelling −2.8%, MidRise +22.8%,
HighRise +9.4%; Office +27.9% vs the NECB-PNNL central estimate of 135 — still well inside the
100–200 as-modelled band.

> **Office end-use split is n/a:** `agg_annual` carries `lights_kWh`/`equip_kWh` only for the
> residential reader; the office reader captured aggregate `office_elec`, so the office
> lighting-vs-equipment split is not available here. Residential split is shown; office is
> aggregate-EUI only. (A §8D-aggregator extension to split office end uses is the way to close this.)

### §R2 — Load shape & peak timing

| Metric | Residential | Office |
|---|---|---|
| Mean daily-peak hour | **14.8 h** (per-run mean; by cycle 15.1–15.8 h) | **12.9 h** (work-day, tracks AT_WORK) |
| WD midday vs night | 22.6 kW midday **<** 33.5 kW night (away midday; overnight HVAC/appliances) | 136.4 kW midday **>** 58.0 kW night (occupancy hump) ✅ |
| WD vs WE midday | — | 53.7 kW WE **<** 136.4 kW WD ✅ |
| Coincidence-factor proxy | **0.82** (profile-peak ÷ mean individual peak; < 1) | deterministic (single profile) |

The **office** load-shape story is clean and strong: a work-day mid-day hump (136 kW) far above
night (58 kW), and weekend well below weekday — textbook occupancy-driven office electricity. The
**residential** peak sits mid-afternoon in the per-run mean (14.8 h) rather than a sharp evening
spike, because annual mean-daily-peak-hour averages summer-AC afternoon peaks with winter-evening
peaks. (Note: the coincidence-factor proxy here, 0.82, is cruder than §8E's diurnal coincidence
metric, 0.56 — different definitions; both are < 1.)

### §R2a — Per-archetype diurnal shape (new figures)

Three new figures extend §R2's paired load-shape summary down to the archetype level:
`figures/fig_diurnal_lights_archetype.png` (residential lighting end-use, 4 archetypes —
SingleD/MidRise/OtherDwelling/HighRise — normalized to daily mean),
`figures/fig_diurnal_equip_archetype.png` (same, equipment end-use), and
`figures/fig_diurnal_office_archetype.png` (office, 3 archetypes — Office_Knowledge/Office_Public/
Office_Sales — TOTAL electricity only).

Two limitations apply to all three, and both are documented scope, not oversights: (1) **no
baseline arm** — unlike 2J, 3J Leg-2's simulation campaign has no default-schedule-vs-activity-
schedule comparison arm, so these figures show the simulated shape only, not a baseline-vs-activity
delta; (2) **no office end-use split** — as noted in §R1, the §8D office aggregation reader captures
only summed `office_elec` (no separate lights/equipment channels), so the office archetype figure is
TOTAL electricity only — a data limitation of the aggregator, not a missed lights/equipment
breakdown.

### §R3 — Scenario / WFH response (2030 bands)

**Residential — clean signal ✅:**

| Scenario | Mid-day share | Δ vs 2022 | Energy % vs 2022 |
|---|---|---|---|
| 2022 | 0.252 | 0 | 0 |
| 2030-conservative | 0.254 | +0.002 | +1.15% |
| 2030-hybrid | 0.266 | +0.014 | +1.79% |
| 2030-fullyhybrid | 0.273 | +0.021 | +2.14% |

Residential mid-day share and energy both rise monotonically with the Work From Home (WFH) band —
the expected "WFH keeps people home during the day → more daytime home load" signature. **PASS.**

**Office — WFH-modulation live (post zone-routing fix), bands non-degenerate ✅ (gate G8o):**

| Scenario | occ_mean (persons) | Occ % vs 2022 | Energy % vs 2022 | Mid-day share |
|---|---|---|---|---|
| 2022 | 152.855 | 0 | 0 | 0.439 |
| 2030-conservative | 161.118 | **+5.41%** | +0.54% | 0.442 |
| 2030-hybrid | 156.748 | +2.55% | −0.01% | 0.439 |
| 2030-fullyhybrid | 153.851 | +0.65% | −0.33% | 0.437 |

The three 2030 bands now genuinely differ (pre-fix they were byte-identical — see Progress Log
2026-07-02). Two things to read carefully:

1. **The conservative band sits ABOVE 2022, not below.** The 2022 baseline already carries ~30%
   real-world WFH; a conservative *return-to-office* (15–20% WFH) therefore means MORE office
   presence than 2022 (+5.41% occupancy). Band ordering is monotone and correct: cons ≥ hyb ≥ full
   on occupancy, WD peak occupancy (0.7015 ≥ 0.6169 ≥ 0.6045, §8E §6.3/§7.2) and mid-day share.
2. **Annual energy stays nearly flat (range ≈0.9%) — by design, not by bug.** Office annual energy
   is dominated by envelope + HVAC held at code baseline; only lights/equipment are occupancy-
   coupled, a small fraction of an ~18.4 GWh tower. A +5.4% occupancy change moves annual energy
   only +0.5% — the documented damped/non-linear response (§8E §7.2). The office WFH story for the
   paper is therefore told with **occupancy, peak and load shape**, with annual energy as the
   damped-response exhibit. **PASS (G8o).**

### §R4 — Longitudinal (2005→2022)

| Cycle | Resid mid-day share | Resid mean peak-hr | Office mid-day share | Office mean peak-hr |
|---|---|---|---|---|
| 2005 | 0.250 | 15.1 h | 0.438 | 12.8 h |
| 2010 | 0.253 | 15.2 h | 0.438 | 12.4 h |
| 2015 | 0.235 | 15.8 h | 0.440 | 14.1 h |
| 2022 | 0.252 | 15.3 h | 0.439 | 12.6 h |

Residential mid-day share dips 2010→2015 (−0.018) then steps back up into 2022 (+0.017) — the
pre-COVID→COVID break is visible on the residential channel. **Office historical variation is real
but modest at this aggregate metric** (mid-day share 0.438–0.440; occ_mean 150.8–154.4 across
cycles): the historical AT_WORK multipliers differ less across cycles than the 2030 WFH bands do,
and carry the documented reconstruction uncertainty (§8E §0.5 — gating variable changed between
cycles). The office longitudinal story is supporting evidence, not a headline result.

A new Figure 5 (`figures/fig_longitudinal_both.png`) renders this table as a 3-panel longitudinal
chart — mid-day share, mean peak hour, and annual energy, both channels, across the four census
cycles (2005/2010/2015/2022). Read alongside the table, both channels are essentially flat/stable
across cycles: residential mid-day share ranges 0.235–0.253 and annual energy 433k–438k kWh; office
mid-day share ranges 0.438–0.440 and annual energy 18.38M–18.44M kWh. Neither channel shows a strong
historical trend at this aggregate metric — the residential mid-day-share dip/rebound noted above is
real but modest against an otherwise flat multi-decade background.

---

## 5. EQUAL-TREATMENT LEDGER (the parity check)

Every row is computed **and reported for both channels**. This table is the explicit answer to
"give residential and office the same importance."

| Analysis | Residential | Office | Parity status |
|---|---|---|---|
| Presence→L/E coupling (floors) | ✅ Lmin 0.15 / Pbase 0.20 | ✅ Lmin 0.15 / Pbase 0.20 | ✅ equal |
| Aggregate site-EUI vs benchmark | ✅ vs SHEU (per arch) | ✅ vs NECB-PNNL (+SCIEU context) | ✅ equal |
| Lighting vs equipment split | ✅ (from agg_annual) | ⚠️ n/a — office reader kept aggregate only | **gap** (needs §8D office split) |
| Load-shape / diurnal profile | ✅ | ✅ work-day hump (clean) | ✅ equal |
| Peak-hour timing | ✅ 14.8 h | ✅ 12.9 h | ✅ equal |
| Weekend vs weekday | ⚠️ (CF proxy only) | ✅ WE < WD | partial |
| Scenario / WFH response | ✅ midday ↑ + energy ↑ | ✅ bands non-degenerate, occ +5.4/+2.6/+0.7% vs 2022, damped energy (G8o) | ✅ equal |
| Longitudinal / COVID break | ✅ visible | ✅ real but modest (midday 0.438–0.440; occ 150.8–154.4) | ✅ equal (signal-size differs) |
| Uncertainty representation | ✅ N=50 MC bands | deterministic (design choice) | *appropriate, not equal* |

Two honest asymmetries: (1) the **deterministic office** (last row) is channel-appropriate design,
not a bias. (2) One parity gap remains — the office **end-use split** isn't in the agg tables
(§8 caveat 5). The scenario/longitudinal rows were flagged "office refinement pending" pre-fix;
after the 2026-07-02 zone-routing fix + re-simulation the office bands are non-degenerate and the
rows are genuinely equal. The ledger reports gaps rather than hiding them.

---

## 6. OUTPUTS (`Step9_docs/outputs_step9/`)

Produced by `3rdJ_09_activityDrivenLoads_2split.py` (reads the §8D agg tables — no re-simulation):

| File | Contents |
|---|---|
| `step9_eui_by_channel.csv` | both channels: unit, median EUI, band lo/central/hi, in-band flag |
| `step9_loadshape_peaks.csv` | both channels: mean peak hour, midday/night kW, WE/WD |
| `step9_scenario_response.csv` | both channels × scenario: occupancy metric, energy metric |
| `step9_longitudinal.csv` | both channels × cycle: mid-day share, peak hour |
| `figures/fig_eui_both.png` | paired EUI-vs-benchmark bars (resid arch panel + office panel) |
| `figures/fig_diurnal_both.png` | paired diurnal curves (resid evening vs office work-day) |
| `figures/fig_diurnal_lights_archetype.png` | residential lighting end-use diurnal shape, 4 archetypes (SingleD/MidRise/OtherDwelling/HighRise), normalized to daily mean — simulated-shape-only |
| `figures/fig_diurnal_equip_archetype.png` | residential equipment end-use diurnal shape, same 4 archetypes, normalized to daily mean — simulated-shape-only |
| `figures/fig_diurnal_office_archetype.png` | office diurnal shape, 3 archetypes (Office_Knowledge/Office_Public/Office_Sales), TOTAL electricity only (no lights/equip split for office) — simulated-shape-only |
| `figures/fig_peakhour_both.png` | paired peak-hour distributions |
| `figures/fig_scenario_both.png` | paired 2030-band response |
| `figures/fig_longitudinal_both.png` | 3-panel longitudinal chart (mid-day share / mean peak hour / annual energy), both channels, across census cycles 2005/2010/2015/2022 |
| `step9_report.html` | stitched tables + figures with the equal-treatment framing |

---

## 7. GATES (both channels, matched — mapped to the Step-8 validator)

These are already enforced in `3rdJ_08_simulation_2split_val.py`; Step 9 presents them as a unified
bi-channel acceptance table.

| Gate | Residential check | Office check | Threshold |
|---|---|---|---|
| EUI in band | §4.1-{arch} vs SHEU | §4.3-office vs NECB-PNNL | median within band (WARN if out, non-blocking) |
| EUI ordering | §4.2-order (SingleD ≥ HighRise) | — | plausible ordering |
| Peak-hour direction | §5.1-resid (15–22 h) | §5.1-office (7–19 h) | channel-appropriate window |
| Midday hump | — | §5.2-office (midday > night) | occupancy-driven |
| Coincidence factor | §5.3-cf (0 < CF < 1) | — (deterministic) | diversity < 1 |
| Weekend < weekday | — | §5.4-office | WE midday < WD midday |
| Scenario non-linearity | §7.3 (2030 midday ≥ 2022) | §7.2 (|energy Δ%| ≤ |occ Δ%| + 1 pp, direction-agnostic — reworded 2026-07-02: 2030-cons sits *above* the ~30%-WFH 2022 baseline) | damped response |

---

## 8. CAVEATS

1. **Aggregate depth** (see §1) — end-use = lighting + equipment coupling + aggregate EUI, not
   activity-resolved appliance disaggregation. Deep residential model = Leg-1 provenance; deep
   office model = Leg-3 candidate.
2. **MC vs deterministic** — residential has N=50 uncertainty bands; office is deterministic. A
   design choice, documented, not a bias.
3. **Residential EUI basis** — conditioned-area-incl-basement vs SHEU heated-excl-basement, so
   SingleD reads high (non-blocking WARN).
4. **Office annual energy is nearly flat across scenarios (range ≈0.9%) — by design, not by bug.**
   (RESOLVED framing — the pre-fix degeneracy, where all 7 scenarios were byte-identical because the
   WFH schedules never reached the zones, was fixed 2026-07-02 and everything re-simulated.) Office
   annual energy is HVAC/envelope-dominated; only lights/equipment follow occupancy. Report the
   office WFH response on **occupancy, peak and load shape** (occ +5.4/+2.6/+0.7% vs 2022; WD peak
   occupancy 0.70/0.62/0.60), and cite the flat annual energy as the damped/non-linear response, not
   as a null result. Cite sim-side gates (Step-9 **G8o**, §8E **§7.2**) — NOT §8E §6.3, which reads
   the Step-7 *input* multipliers and passed even pre-fix.
5. **Office end-use split unavailable** — `agg_annual` has `lights_kWh`/`equip_kWh` only for the
   residential reader; office kept aggregate `office_elec`. To reach parity on the lighting-vs-
   equipment breakdown, extend the §8D office reader to split office end uses.
6. **Load-shape metric definitions** — Step-9 numbers (mean-of-per-run-daily-peak-hour 14.8 h resid /
   13.6 h office; CF proxy 0.82) differ from §8E's diurnal-profile-based numbers (16.1 h; CF 0.56).
   Not a contradiction — different estimators. Pick one convention for the paper and state it.
7. **Residential lights/equipment diurnal shape was never captured (fix in progress)** — the two
   new §R2a figures (`fig_diurnal_lights_archetype.png` / `fig_diurnal_equip_archetype.png`) first
   rendered with all 4 residential archetypes showing "no data", for every archetype uniformly (not
   a tall/super-tall-specific gap). Root cause: `3rdJ_08_simulation_2split_agg.py::summarize_resid_run`
   computed the hourly grid for `InteriorLights:Electricity`/`InteriorEquipment:Electricity` and
   summed it into the annual totals (`lights_kWh`/`equip_kWh`, feeding §R1's lights/equip shares),
   but only ever persisted the hourly *shape* (`_diurnal_rows`) for `Electricity:Facility` —
   `agg_diurnal.csv` never had lights/equipment rows for residential. Fixed by adding the same
   `_diurnal_rows` call for both end-use meters; a full §8D re-aggregation (`run_aggregation.sh`,
   `--rebuild`, all 8,400 residential + 252 office runs) was submitted 2026-07-05 to backfill
   `agg_diurnal.csv`, followed by a Step-9 re-run to regenerate `step9_report.html` against the
   refreshed table. See Progress Log entry below for job IDs and status.

---

## 9. REFERENCES

- NRCan SHEU 2019 (residential EUI by dwelling type) — 2J deepResearch
  "Canadian Residential Energy-Use Intensity by Dwelling Type — Plausibility Bands".
- NECB 2020 / ASHRAE 90.1-2019 / DOE-PNNL Tall+SuperTall prototypes — `Step8_docs/deepResearch/
  Office Reference EUI … As-Modelled Bands.md`.
- NRCan SCIEU-2019 / CEUD-2023 (measured office stock) — `Step8_docs/deepResearch/
  Canadian Office Energy-Use Intensity (NRCan SCIEU_CEUD) — Plausibility Bands.md`.
- ASHRAE Guideline 14 (calibration context: NMBE ±5/10%, CV(RMSE) 15/30%).
- Leg-1 activity-resolved residential Step 9 — `2J_docs_occ_nTemp/09_activityDrivenLoads.md`.

---

## Progress Log

### 2026-07-01 — Manager (Opus) — Step 9 unified (both channels) authored

Created `Step9_docs/` and this bi-channel Step-9 doc at **aggregate depth** after a recon of the 2J
Step-9 template + the 3J §8D agg schema. Decision (user-approved): meet both channels at the
aggregate end-use + EUI-calibration level, where parity is genuinely achievable (both on real,
independent benchmarks — SHEU for residential, NECB-PNNL for office). The deep activity-resolved
residential model stays Leg-1 provenance; an office activity-resolved extension is deferred to
Leg 3 (needs an office per-end-use benchmark). Next: `3rdJ_09_activityDrivenLoads_2split.py`
(reads §8D agg → parallel per-channel tables + paired figures + `step9_report.html`), then a cluster
run to emit `outputs_step9/`, then reframe the Step-9 line in the two pipeline overview docs from
"office-only" to "both channels". Office §7.2 energy-saving number to be recomputed against the
correct 2022 baseline during the analysis build.

### 2026-07-01 (late) — Manager (Opus) — Step 9 analysis RAN + collected (job 1055064)

`run_step9.sh` → job **1055064 COMPLETED** (exit 0:0, Elapsed 41 s, MaxRSS 296 MB, magic-node-01).
Clean: `py_compile OK`, tables 8 EUI / 2 loadshape / 14 scenario / 8 longitudinal, 4 figures,
`step9_report.html` (8,627 B). No Traceback/FATAL (two benign numpy "mean of empty slice" warnings).
Outputs pulled local to `Step9_docs/outputs_step9/`. §R1–R4 tables above now carry the **real**
`outputs_step9/*.csv` numbers (not §8E transcriptions).

**Solid / paper-ready:** both-channel EUI vs benchmark (resid SingleD 212.5 WARN expected, others
in-band; office 179.6 PASS); residential scenario response (mid-day 0.252→0.273, energy +2.14%
across WFH bands); residential COVID break; office load-shape (mid-day hump 146 kW > night 57 kW,
WE 48.5 < WD 146).

**Refinement pass needed before this Step is "DONE"** (see §8 caveats 4–5 + §5 ledger):
(a) office scenario + longitudinal are degenerate at the **annual** level (office `occ_mean` = design
density 163.683, annual energy flat across all 7 scenarios) → re-source office rows of
`build_scenario`/`build_longitudinal` from `agg_peak`/`agg_diurnal` (peak kW / peak hour / mid-day
office_occ) and re-draw `fig_scenario_both` with an office peak-or-shape metric; (b) office
lights/equip end-use split absent from `agg_annual`. Both = small script edits + one 41 s re-run,
no re-simulation. **Reframing the two pipeline docs (office-only → both channels) is deferred until
after this refinement** so it reflects final results. Full runbook: RESUME.md §6.

### 2026-07-02 — Manager — office WFH bug fixed, full post-fix re-run, doc updated to final numbers

The §R3/§R4 "degeneracy" logged above turned out to be a **simulation bug, not a metric-depth
limitation**: `office_integration.py` read the pre-v24.2 zone-field name
(`Zone_or_ZoneList_Name` vs v24.2's `Zone_or_ZoneList_or_Space_or_SpaceList_Name`), so every zone
tagged `skip` and the band-specific OFC_* schedules were never wired — all 7 office scenarios ran
the prototype `NECB-A-Occupancy` (probe 1057830; root cause confirmed 1057831). A latent second bug
(People `Schedule_Name` → should be `Number_of_People_Schedule_Name`) was fixed in the same pass.
Recovery chain, all COMPLETED exit 0 on 2026-07-02: re-sim **1058490** (252/252, `--no-skip`) →
§8D re-agg + §8E re-validation **1058661** → Step-9 re-run **1058662**.

Post-fix results (this doc's §R1–§R4 updated in place): step9_report = **10 PASS / 1 WARN / 0
FAIL**; new gate **G8o PASS** — 2030 office bands non-degenerate (occ +5.41/+2.55/+0.65% vs 2022;
energy +0.54/−0.01/−0.33%). Office EUI median 172.6 (was 179.6 pre-fix), peak hour 12.9 h, WD
midday 136.4 > night 58.0 kW. Residential unchanged. Key interpretation locked in §R3: the
conservative band sits ABOVE the ~30%-WFH 2022 baseline (return-to-office), and annual office
energy is damped by design — the WFH story is occupancy/peak/shape. §8E §7.2 gate reworded to be
direction-agnostic (|energy Δ%| ≤ |occ Δ%| + 1 pp; re-validation job 1062194). Stale pre-fix local
artifacts archived to `../investigation/stale_pre_fix_snapshot/`; acceptance review (verdict:
paper-ready) at `../investigation/2split_results_acceptance_review.md`. Ledger rows for
scenario/longitudinal flipped to ✅ equal; remaining parity gap = office end-use split (caveat 5).
Pipeline docs reframed (status tags PLANNED → DONE) in the same session.

### 2026-07-05 — Employee (Sonnet) — companion doc synced to new HTML report figures/captions

A parallel employee is updating the generator script (`3rdJ_09_activityDrivenLoads_2split.py`) to
add new figures and rewrite HTML report captions; this doc was updated in lockstep so the two stay
consistent, with **no changes made to the .py file**. Specifically: (1) §6 Outputs table gained 4
new rows — `figures/fig_longitudinal_both.png`, `figures/fig_diurnal_lights_archetype.png`,
`figures/fig_diurnal_equip_archetype.png`, `figures/fig_diurnal_office_archetype.png` — each with a
one-line description. (2) §R1 prose gained a sentence stating the HTML Figure 1 caption now reports
each archetype's % error vs its benchmark's central estimate (resid SingleD +36.6%, OtherDwelling
−2.8%, MidRise +22.8%, HighRise +9.4%; office +27.9% vs the NECB-PNNL central of 135, still inside
the 100–200 as-modelled band). (3) §R3 spelled out "Work From Home (WFH)" on its first body-text
mention. (4) A new **§R2a** subsection was added describing the 3 new per-archetype diurnal figures
and flagging their two documented limitations: no default-schedule-vs-activity-schedule baseline arm
(unlike 2J), so shapes are simulated-only; and no office lights/equipment split (aggregator data
limitation, not an oversight — same n/a already noted in §R1). (5) §R4 gained a closing paragraph on
the new Figure 5 (`figures/fig_longitudinal_both.png`, 3-panel: mid-day share / mean peak hour /
annual energy, both channels, 2005–2022), noting both channels read as flat/stable across cycles
(resid midday share 0.235–0.253, energy 433k–438k kWh; office midday share 0.438–0.440, energy
18.38M–18.44M kWh) — no strong historical trend. Not touched: Figure 2's "simulated-only, no
measured hourly dataset" caveat and Figure 3's density-normalization framing were left as-is because
the existing §R2 text (lines above) already states both points in equivalent language; the report
layout change (each §R1–R4 table now followed by its own figure, replacing the old bunched-at-end
figure block) is a presentation change with no prose claim to update. This doc was not re-run against
new outputs — it is a documentation-consistency sync only; once the .py regenerates
`outputs_step9/*` the numeric values embedded above should be spot-checked against the actual new
figure files/captions.

### 2026-07-05 (cont.) — Manager — residential lights/equip diurnal gap found + fix + re-agg cluster run started

User reviewed the new §R2a figures and asked why the lighting/equipment archetype panels were empty,
and whether it was tall/super-tall-building-specific. Checked the actual PNGs: all 4 residential
archetypes (SingleD, OtherDwelling, MidRise, HighRise) were empty for both meters, uniformly — not
a building-height issue. Root cause confirmed in
`Step8_docs/3rdJ_08_simulation_2split_agg.py::summarize_resid_run` (~L362–369): the hourly grid for
`InteriorLights:Electricity`/`InteriorEquipment:Electricity` was computed and summed into the annual
totals, but `_diurnal_rows()` — the function that writes hourly-shape rows into `agg_diurnal.csv` —
was only ever called for `Electricity:Facility`. This was a deliberate original scoping decision
("kept lean; only what the val gates consume") from before this Step-9 refresh asked for an end-use
diurnal split, not an oversight or a building-type limitation. See caveat 7 above.

Fix: added a `for meter in (M_LIGHTS, M_EQUIP): ... _diurnal_rows(...)` loop right after the existing
facility call in `summarize_resid_run`. `py -m py_compile` clean locally. Archived the remote
predecessor script (`Step8_docs/archive/3rdJ_08_simulation_2split_agg.20260705_pre_lights_equip_diurnal.py`),
`scp`'d the fix, md5-verified match. Submitted the existing `run_aggregation.sh` via `sbatch`
(7-day walltime) — **job 1067688** — which re-scans all 8,400 residential + 252 office runs
(`--rebuild`) to rebuild all four §8D agg tables, and also refreshes the Step-8 validation report
as its Pass 2. Once COMPLETED, will re-run `run_step9.sh` to regenerate `step9_report.html` against
the refreshed `agg_diurnal.csv`, confirm the two archetype panels populate with real curves, and
confirm both scorecards (Step-8 and Step-9) are unchanged (no new FAIL — no existing gate reads
these new rows). Job is running; tracked in
`outputs_step9/step9_report_improvements_TASKS.md` (Task 12).
