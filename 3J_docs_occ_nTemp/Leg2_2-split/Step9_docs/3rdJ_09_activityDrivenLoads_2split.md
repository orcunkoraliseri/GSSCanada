# 3J Leg-2 · STEP 9 — Activity-Driven End-Use Loads (Both Channels)
### Residential (AT_HOME) + Office (AT_WORK) — equal treatment, matched evaluation

> **Status:** BUILT 2026-07-01 (Manager/Opus). Aggregate-depth unification of the two-channel
> activity-driven end-use loads. **Both channels are first-class here — same analyses, same rigor,
> each on its own physically-correct benchmark and parameters.** No re-simulation: reads the
> existing §8D aggregation tables (`Step8_docs/outputs_step8/agg/`).

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

*Numbers below are the ACTUAL Step-9 analysis output (job 1055064, `outputs_step9/*.csv`), not
transcribed from the §8E log. Where a Step-9 number differs from §8E it is because Step 9 uses a
per-run summary of `agg_annual`/`agg_peak` (e.g. mean of per-run daily-peak hours) whereas §8E read
the mean diurnal profile — both are defensible; the Step-9 values are the ones reported here.*

### §R1 — End-use intensity vs benchmark (EUI)  ✅ solid, both channels

| Channel | Unit | n | Median EUI (kWh/m²) | Band | Verdict | Lights / Equip share |
|---|---|---|---|---|---|---|
| Residential · SingleD | dwelling | 2100 | **212.5** | SHEU 130.6–186.1 | **WARN** (basis: conditioned incl. basement) | 0.16 / 0.61 |
| Residential · OtherDwelling | dwelling | 2100 | 140.4 | SHEU 136.1–186.1 | **PASS** | 0.17 / 0.62 |
| Residential · MidRise | dwelling | 2100 | 177.3 | SHEU 111.1–216.7 | **PASS** | 0.19 / 0.28 |
| Residential · HighRise | dwelling | 2100 | 142.9 | SHEU 113.9–147.2 | **PASS** | 0.28 / 0.40 |
| **Office (all)** | tower | 252 | **179.6** | PNNL 100–200 | **PASS** | n/a (see below) |
| Office · Knowledge / Public / Sales | tower | 84 each | 179.6 each | PNNL 100–200 | **PASS** | n/a |

Ordering sanity: SingleD (212.5) ≥ HighRise (142.9) — plausible. Office 179.6 sits in-band, on the
high side of the prototype central (135) — consistent with tall towers (high internal loads +
envelope), and correctly **below** the ≈230 empirical stock. The three office archetypes share the
same median (179.6) because at the annual EUI level the tower's energy is dominated by
envelope + HVAC (unchanged across archetypes); archetype differences show up in the *shape*, not the
annual intensity.

> **Office end-use split is n/a:** `agg_annual` carries `lights_kWh`/`equip_kWh` only for the
> residential reader; the office reader captured aggregate `office_elec`, so the office
> lighting-vs-equipment split is not available here. Residential split is shown; office is
> aggregate-EUI only. (A §8D-aggregator extension to split office end uses is the way to close this.)

### §R2 — Load shape & peak timing

| Metric | Residential | Office |
|---|---|---|
| Mean daily-peak hour | **14.8 h** (per-run mean; by cycle 15.1–15.8 h) | **13.6 h** (work-day, tracks AT_WORK) |
| WD midday vs night | 22.6 kW midday **<** 33.5 kW night (away midday; overnight HVAC/appliances) | 146.0 kW midday **>** 57.0 kW night (occupancy hump) ✅ |
| WD vs WE midday | — | 48.5 kW WE **<** 146.0 kW WD ✅ |
| Coincidence-factor proxy | **0.82** (profile-peak ÷ mean individual peak; < 1) | deterministic (single profile) |

The **office** load-shape story is clean and strong: a work-day mid-day hump (146 kW) far above
night (57 kW), and weekend well below weekday — textbook occupancy-driven office electricity. The
**residential** peak sits mid-afternoon in the per-run mean (14.8 h) rather than a sharp evening
spike, because annual mean-daily-peak-hour averages summer-AC afternoon peaks with winter-evening
peaks. (Note: the coincidence-factor proxy here, 0.82, is cruder than §8E's diurnal coincidence
metric, 0.56 — different definitions; both are < 1.)

### §R3 — Scenario / WFH response (2030 bands)

**Residential — clean signal ✅:**

| Scenario | Mid-day share | Δ vs 2022 | Energy % vs 2022 |
|---|---|---|---|
| 2022 | 0.252 | 0 | 0 |
| 2030-conservative | 0.254 | +0.002 | +1.15% |
| 2030-hybrid | 0.266 | +0.014 | +1.79% |
| 2030-fullyhybrid | 0.273 | +0.021 | +2.14% |

Residential mid-day share and energy both rise monotonically with the WFH band — the expected
"WFH keeps people home during the day → more daytime home load" signature. **PASS.**

**Office — annual metrics are degenerate; the WFH signal is in peak/shape, not annual ⚠️:**
In `agg_annual`, office `occ_mean_persons` = **163.683 for ALL seven scenarios** (that is the NECB
design density, not the simulated AT_WORK-modulated occupancy) and annual energy ≈ **19,066 MWh**
varies < 0.01% across scenarios. So "office annual energy vs WFH" is ~0% by construction — **not a
usable scenario result at the annual level.** This is *physically expected* (office annual energy is
dominated by envelope + HVAC held at code baseline; only lights/equipment are occupancy-coupled, a
small fraction of a 19 GWh tower), but it means the office WFH story must be told with **peak / load
shape**, where §8E §6.3 already showed office 2030 WD peak declining (cons 0.70 / hyb 0.62 /
full 0.60). **Action (flagged for the fresh session): re-source the office scenario response from
`agg_peak`/`agg_diurnal` (peak kW, peak hour, mid-day occupancy) instead of annual energy, and
re-draw `fig_scenario_both` with an office peak/shape metric.**

### §R4 — Longitudinal (2005→2022)

| Cycle | Resid mid-day share | Resid mean peak-hr | Office mid-day share |
|---|---|---|---|
| 2005 | 0.250 | 15.1 h | 0.447 |
| 2010 | 0.253 | 15.2 h | 0.447 |
| 2015 | 0.235 | 15.8 h | 0.447 |
| 2022 | 0.252 | 15.3 h | 0.447 |

Residential mid-day share dips 2010→2015 (−0.018) then steps back up into 2022 (+0.017) — the
pre-COVID→COVID break is visible on the residential channel. **Office mid-day share is flat at 0.447
across all cycles** — same annual-metric degeneracy as §R3 (the office historical signal is in the
shape/peak, not the annual mid-day share). Same re-sourcing action applies.

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
| Peak-hour timing | ✅ 14.8 h | ✅ 13.6 h | ✅ equal |
| Weekend vs weekday | ⚠️ (CF proxy only) | ✅ WE < WD | partial |
| Scenario / WFH response | ✅ midday ↑ + energy ↑ | ⚠️ annual degenerate → use peak/shape | **office refinement pending** |
| Longitudinal / COVID break | ✅ visible | ⚠️ annual flat → use peak/shape | **office refinement pending** |
| Uncertainty representation | ✅ N=50 MC bands | deterministic (design choice) | *appropriate, not equal* |

Two honest asymmetries: (1) the **deterministic office** (last row) is channel-appropriate design,
not a bias. (2) Three rows are flagged **office refinement pending** — the office end-use split isn't
in the agg tables, and office scenario/longitudinal signals are in peak/shape not annual metrics.
These are real parity gaps to close (see §8) — the ledger reports them rather than hiding them.

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
| `figures/fig_peakhour_both.png` | paired peak-hour distributions |
| `figures/fig_scenario_both.png` | paired 2030-band response |
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
| Scenario non-linearity | §7.3 (2030 midday ≥ 2022) | §7.2 (energy saving ≤ occ cut) | sub-proportional |

---

## 8. CAVEATS

1. **Aggregate depth** (see §1) — end-use = lighting + equipment coupling + aggregate EUI, not
   activity-resolved appliance disaggregation. Deep residential model = Leg-1 provenance; deep
   office model = Leg-3 candidate.
2. **MC vs deterministic** — residential has N=50 uncertainty bands; office is deterministic. A
   design choice, documented, not a bias.
3. **Residential EUI basis** — conditioned-area-incl-basement vs SHEU heated-excl-basement, so
   SingleD reads high (non-blocking WARN).
4. **Office scenario/longitudinal metrics are degenerate at the annual level** (job 1055064): office
   `occ_mean_persons` = 163.683 and annual energy ≈ 19,066 MWh are identical across all 7 scenarios
   in `agg_annual` (design density + HVAC-dominated annual total). The office WFH/longitudinal signal
   is real but lives in **peak / load shape** (agg_peak/diurnal; §8E §6.3 showed office 2030 WD peak
   0.70→0.62→0.60). **FIX:** re-source `build_scenario`/`build_longitudinal` office rows from
   `agg_peak`/`agg_diurnal` (peak kW, peak hour, mid-day office_occ) and re-draw `fig_scenario_both`
   with an office peak/shape metric. Residential scenario/longitudinal are correct as-is.
5. **Office end-use split unavailable** — `agg_annual` has `lights_kWh`/`equip_kWh` only for the
   residential reader; office kept aggregate `office_elec`. To reach parity on the lighting-vs-
   equipment breakdown, extend the §8D office reader to split office end uses.
6. **Load-shape metric definitions** — Step-9 numbers (mean-of-per-run-daily-peak-hour 14.8 h resid /
   13.6 h office; CF proxy 0.82) differ from §8E's diurnal-profile-based numbers (16.1 h; CF 0.56).
   Not a contradiction — different estimators. Pick one convention for the paper and state it.

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
