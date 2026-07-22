# 3J Leg-3 — Step 9: Activity-Driven End-Use Loads (Four-Channel)
### Residential + Office + Retail + Hotel — equal treatment ≠ identical parameters; matched evaluation, per-channel benchmarks, dual-basis reporting

---

## 0. WHY THIS STEP EXISTS (and why it is quad-channel)

| Channel | Coupling driver | Headcount basis | BEM action | EUI benchmark (own) | Design |
|---|---|---|---|---|---|
| Residential | AT_HOME presence | HHSIZE | REPLACE | SHEU 2019 bands | inherited |
| Office | AT_WORK fraction | NECB density | MODULATE | PNNL as-modelled 135 [100–200]; SCIEU INFO | inherited |
| Retail ⚠️ | **customer** presence (People gains only) | NECB ~3.7 m²/p | MODULATE | dr_L3-02: 110 [80–155] PASS; 280 [150–380] INFO | NEW |
| Hotel ⚠️ | s(t) × monthly rate | NECB density | MODULATE (monthly) | dr_L3-03: 240 [180–300] PASS; 350 [220–480] INFO | NEW |

**Equal importance ≠ identical parameters** (pipeline STEP 9):
- **Retail:** lighting and HVAC follow **opening hours** (near-flat while open, off overnight); **plug loads follow staff, not footfall** — customer presence modulates People-driven gains only, while the staff-driven plug baseload stays in the NECB baseline. Floors kept: `Lmin = 0.15` egress lighting, `Pbase = 0.20` never-zero plug.
- **Hotel:** guest-room equipment + lighting scaled by `s(t) ×` monthly amplitude; amenity zones baseline (consistent with Step-7 v1 / OD-6). ~40–50 % of guest-room energy is presence-independent (dr_L3-05) — expect a damped response by construction.
- **Calibration anchor:** commercial magnitudes vs **NRCan SCIEU** (the commercial analogue of the residential SHEU anchoring), per channel.

## 1. SCOPE & DEPTH (honest statement)

Aggregate depth, as in Leg-2 Step 9: this step **reads** the Step-8 §8E agg tables — no re-simulation, no new coupling implementation (coupling lives in Step 7/8). Activity-resolved commercial loads remain out of scope (was already flagged "a Leg-3 candidate" in Leg 2; the decision here: the two NEW channels ship at the same aggregate depth first — deepening is post-paper work).

## 2. METHOD

- **§9.1** Presence-driven coupling audit per channel (verify the Step-8 §2.6/2.7-class floors from the agg tables).
- **§9.2** Aggregate EUI calibration, each channel vs its **own** benchmark, on the **dr_L3-10 dual basis** (CFA primary; occupiable-GFA share for the SCIEU/CEUD INFO comparison; basis stated on every table/figure) with hourly load-weighted central-plant attribution (done in §8D — consumed here).

## 3. INPUTS

`Step8_docs/outputs_step8/agg/{agg_annual, agg_peak, agg_diurnal, agg_meta}.csv` (with per-channel and per-end-use columns — the Leg-2 re-aggregation lesson: end-use diurnals captured from the start), benchmark band constants (§0 table).

## 4. RESULTS (skeleton — filled at run time)

- **§R1 — EUI vs benchmark**, per channel × archetype × basis, verdict column.
- **§R2 — Load shape & peak timing**: per-channel peak hour; the four-channel **coincidence story** (retail midday + office midday vs residential evening vs hotel overnight — the tower's diversity factor); metric definitions stated explicitly (per-run-mean vs diurnal-profile — the Leg-2 dual-definition caveat; pick one convention per table and label it).
- **§R3 — Scenario response (2030 bundles + sensitivities)**, per channel:
  - **G8o (office)** — inherited: WFH-modulation non-degenerate; conservative may sit ABOVE 2022 (return-to-office framing — 2022 already carries ~30 % WFH).
  - **G8r (retail, NEW)** — the in-store lever is non-degenerate: retail-zone energy responds monotonically to 0.90/0.97/1.05, and `|energy Δ%| ≤ |occ Δ%| + 1 pp` (damped, direction-agnostic — §7.2 form).
  - **G8h (hotel, NEW)** — the SARIMA band is non-degenerate: guest-room energy responds monotonically to low/central/high, monthly seasonality visible; same damped-response bound.
- **§R4 — Longitudinal 2005→2022**: per-channel midday/evening share trajectories; COVID break signatures (office ↓, retail ↓, resid ↑; hotel from the multiplier series).

## 5. EQUAL-TREATMENT LEDGER (the parity check)

Every analysis row computed AND reported for all four channels, each vs its own benchmark; genuine gaps flagged, not hidden. Known accepted gaps to declare up front: (a) hotel has no GSS-side behavioural depth (aggregate multiplier only — by construction); (b) retail staff invisible in GSS (staff loads live in the baseline — frame caveat, carried to the paper's limitations); (c) office end-use split availability per the Step-8 agg schema.

## 6. OUTPUTS (`Step9_docs/outputs_step9/`)

`step9_eui_by_channel.csv`, `step9_loadshape_peaks.csv`, `step9_scenario_response.csv`, `step9_longitudinal.csv`; figures: `fig_eui_4ch.png`, `fig_diurnal_4ch.png` (stacked coincident, winter+summer), `fig_diurnal_<channel>_enduse.png` ×4, `fig_peakhour_4ch.png`, `fig_scenario_4ch.png`, `fig_longitudinal_4ch.png`, `fig_hotel_monthly.png` (NEW — monthly amplitude vs energy); `step9_report.html`.

## 7. GATES (mapped to the Step-8 validator)

| Gate | Check | Maps to |
|---|---|---|
| EUI in band | per channel, as-modelled PASS / empirical INFO | §4.2/4.6/4.7 |
| EUI share sanity | ±2 pp vs occupiable shares | §4.10 |
| Peak-hour direction | office ~13h; retail 12–16h; resid 15–22h; hotel load-weighted overnight | §5.2 |
| Weekend structure | office WE<WD; retail Sat≥WD; hotel WE plateau shift | §5.3 |
| **G8o / G8r / G8h** | scenario non-degeneracy + damped bound per channel | §7.2 |
| Coincidence factor | stacked peak < Σ channel peaks (diversity) | §5.1 |
| Monthly seasonality (hotel) | energy follows multiplier | §5.4 |

## 8. CAVEATS (paper-facing)

1. Dual-basis mismatch (CFA vs GFA-share) — state basis everywhere.
2. Damped scenario response is **by design** (only People/L/E gains modulated) — not a bug; cite the §7.2 direction-agnostic gate.
3. Metric-definition consistency: one peak-hour convention per table (Leg-2 14.8h-vs-16.1h lesson). **Hour-of-day is a circular quantity — use a circular mean, never an arithmetic mean** (a 2J plotting bug arithmetic-averaged a bimodal morning/evening population into a meaningless ~14.5h); where household-level and stock-aggregate statistics diverge legitimately, report both and label which is headline.
4. Retail staff / hotel guests frame caveats (GSS sees customers only / nothing).
5. Hotel amenity zones unmodulated in v1 (OD-6).
6. Ground-level EPW on a supertall (no altitudinal gradient).
7. **Cite sim-side evidence (G8r/G8h/§7.2), not input-side, as the modulation-signal proof** — the Leg-2 lesson (G8o vs §6.3).
8. Cross-era comparability: each cycle's channel products derive from that cycle's GSS pool (different underlying respondents by construction) — the longitudinal comparison is population-level, not a paired design; one manuscript sentence (the Leg-2 cross-era-pairing ticket, generalized).
9. If the multi-zone residential injection fix is ever cited: it is **energy-neutral on annual aggregates** (2J/Leg-2 verified — building totals conserved); claims scope to zone-level load distribution only, never "restored energy".
10. Report regeneration: after any data/rake change, re-render **every** embedded figure and stamp a regen token — a report built as an additive copy of its predecessor can carry stale charts under fresh prose (2J v6 shipped 7 pre-fix charts).

## 9. REFERENCES

Pipeline STEP 9; dr_L3-02/03/05/06/10; Leg-2 `3rdJ_09_activityDrivenLoads_2split.md` (template + G8o precedent); NRCan SCIEU 2019; SHEU 2019.

## Script

`3rdJ_09_activityDrivenLoads_4split.py` (reads agg tables; no re-simulation) + `run_step9_4split.sh` (sbatch, 7-day walltime). Report scorecard target: 0 FAIL, WARNs documented.

## Progress Log

*(append entries below — dated `###` entries with job IDs)*
