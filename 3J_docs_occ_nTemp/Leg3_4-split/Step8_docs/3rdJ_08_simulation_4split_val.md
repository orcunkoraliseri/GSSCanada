# 3J Leg-3 — Step 8 Validator: Four-Channel BEM Simulation
### §P probes → §0–§8 (Leg-2 scheme, per-channel columns now Resid/Office/Retail/Hotel)

---

> **Threshold provenance.** NMBE ±5 %/±10 % and CV(RMSE) 15 %/30 % = **ASHRAE Guideline 14** (cite the standard). Everything else (EUI bands' PASS/INFO split, ±2 pp share gate, ≤ 1 h timing, ±15 % peak) is project-chosen or dr-report-locked — never cite to literature.

## §P — Pre-campaign probes (⚠️ NEW — HARD, block the campaign)

| Gate | Check | Target | Severity |
|---|---|---|---|
| P1 | Scenario-differentiation, per channel: probe pairs differ in the channel's meters (max abs hourly delta > 0) | all 4 channels differentiate | **FAIL = campaign blocked** |
| P2 | Byte-identity tripwire: any two *different* scenarios byte-identical | none | **FAIL** |
| P3 | Stale-output guard: injector-hash output dirs verified; header-only `hourly_meters.csv` detection | mechanism works | FAIL |
| P4 | Fall-back loudness: a deliberately-missing channel product logs the baseline reversion in the manifest | logged | FAIL |

## §0 — Historical schedule products (gates the campaign)

0.1 schema byte-identical headers to 2022 products; 0.2 row counts; 0.3 per-cycle retail normalization applied (peak = 0.95); 0.4 longitudinal continuity, no leakage; 0.5 historical office/retail gating caveat (INFO); 0.6 no NaN/empty.

## §1 — EnergyPlus run integrity

1.1 completeness 56/56, 0 skipped; 1.2 no fatal errors; 1.3 sizing converged; 1.4 `hourly_meters.csv` 8,760 rows **AND mtime postdates the injector-hash dir creation** (header-only OR stale-fresh mismatch = FAIL); 1.5 SQL outputs present (`_ensure_output_objects` on every path — the office SQL-gap lesson); **1.6 meter-coverage closure (2J Bug B): Σ requested end-use meters ≈ `Electricity:Facility` per run (±5 %), `WaterSystems:Electricity` explicitly requested** — WARN outside, FAIL if a nonzero end-use is entirely unrequested.

## §2 — Schedule injection fidelity (per channel)

| Gate | Check | Target |
|---|---|---|
| 2.1–2.3 | Residential People round-trip ±0.5 %; hour alignment; HHSIZE basis | Leg-2 verbatim |
| 2.4–2.5 | Office density preserved (0.040 ppl/m²); AT_WORK round-trip ±0.5 % | Leg-2 verbatim |
| 2.6–2.7 | Lights coupling (Lmin floor never violated); Equipment coupling (Pbase floor) | Leg-2 verbatim, all modulated channels |
| **2.10** | Retail round-trip: zone People schedule = 0.95 × shape ± 0.5 %; staff-shoulder slots = baseline | NEW |
| **2.11** | Retail density preserved (~3.7 m²/person untouched) | NEW |
| **2.12** | Hotel round-trip: guest-room schedule = s(t) × monthly rate ± 0.5 %; **12 distinct monthly amplitudes present in the annual schedule** | NEW |
| **2.13** | Hotel density untouched; amenity zones = baseline (OD-6) | NEW |
| 2.8–2.9 | Code densities untouched (LPD/plug W/m²); Interpolate = No everywhere | Leg-2 verbatim |
| **2.14** | Residential branch carrier audit (2J Bug A): one equip/lights carrier per neutralized zone, count == neutralized-zone count per building; retail/hotel branches contain NO neutralize+carrier path (modulate-in-place only) | NEW — FAIL |

## §4 — Physical plausibility (dual-basis, per channel)

| Gate | Check | Target |
|---|---|---|
| 4.1 | Residential-zone EUI vs HighRise SHEU band | INFO (basis mismatch expected) |
| 4.2 | Office EUI | as-modelled 135 [100–200] PASS; 230 [170–360] INFO |
| **4.6** | Retail EUI | **as-modelled 110 [80–155] PASS; 280 [150–380] INFO** (dr_L3-02) |
| **4.7** | Hotel EUI | **as-modelled 240 [180–300] PASS; 350 [220–480] INFO** (dr_L3-03) |
| 4.3 | Heating dominance rises with CZ severity (MTL vs CLG) | direction |
| **4.8** | Dual-basis discipline: every EUI table/figure carries its basis label; CFA > GFA-share values by ~5–10 % | present |
| **4.9** | Plant-allocation conservation: Σ per-channel allocated plant energy = total plant energy, per timestep aggregate | ± 0.1 % — FAIL |
| **4.10** | Floor-area sanity: per-channel EUI shares vs parsed occupiable shares | **± 2 pp** (project-novel) |

## §5 — Load-shape sanity (per channel)

5.1 peak-occupancy coupling; 5.2 diurnal shapes — office hump + lunch dip; **retail midday/afternoon hump, Sat > weekday, near-zero night; hotel overnight plateau + daytime trough (inverted vs office — the load-timing story)**; 5.3 weekend structure — office WE < WD; retail Sat ≥ WD; **5.4 hotel monthly seasonality visible in guest-room loads (summer/winter amplitude follows the multiplier)**.

## §6 — Longitudinal, COVID break, scenario bands (headline)

6.1 per-cycle separability per channel; 6.2 COVID break visible (2015→2022): office ↓, retail ↓, resid ↑; 6.3 band ordering energy per channel (office cons > hyb > fully; retail 0.90 < 0.97 < 1.05 in load; hotel low < central < high); 6.4 cross-channel coincidence: stacked peak timing reported (the mixed-use diversity story); 6.5 2005–2015 smooth monotonicity.

## §7 — Scenario plausibility

7.1 2022 baseline plausible per channel; **7.2 direction-agnostic damped response per channel: `|energy Δ%| ≤ |occ Δ%| + 1 pp`** (the Leg-2 reworded gate — occupancy modulates only L/E/People gains; envelope+HVAC dominate); 7.3 uncertainty framing: hotel SARIMA PI reported alongside bands (INFO).

## §8 — Summary scorecard

FAIL on §P/§0/§1/§2 blocks campaign sign-off; §4–§7 FAILs investigated and documented as known limitations where defensible. Expected shape: comparable to Leg-2's 50P/2W/17I/0F end-state, with ~15 additional Leg-3 gates.

## PASS / WARN / FAIL Convention

Canonical. INFO = context bands (empirical EUI, SARIMA PIs, historical-gating caveats). Two standing disciplines (2J master-log rules): **never relax a gate threshold to clear a FAIL** — the accepted alternative is relabel + document with evidence ("goalpost-moving" rejected twice in 2J); and **every computed/persisted quantity gets a gate or an explicit INFO designation** — a metric computed but never checked is a silent coverage gap (2J's `covid_signal_pp`; the un-validated §4b columns).

## Test Method

`run_validation.sh` (sbatch) after aggregation; report `outputs_step8/step8_validation_report.html`. Regenerate the report after ANY re-sim or re-agg (stale-HTML lesson); the canonical scorecard lives in the newest report on the cluster — sync local copies before quoting numbers (the Leg-2 scp-sync caveat).

## Progress Log

*(append entries below)*
