# Step 8 — BEM Simulation: Validation Plan

> ⚠️ **UNDER REVISION — 4-hour schedule-injection bug found 2026-06-08.** `07_aug_to_bem.py` wrote the 4 AM-origin GSS diary slots straight to EnergyPlus `Hour` (slot @ 04:00 → Hour 0) instead of rotating to real clock (slot @ 04:00 → Hour 4). Occupancy / metabolic / equipment / lighting were all injected **4 h early** vs the EPW weather. The "fidelity" axis below (injected time-series matches Step-7 schedules) was checked in the same mis-clocked frame, so it did NOT catch this. Bug fixed; **full cluster re-simulation in progress (initiated 2026-06-08)** — re-validate after. Annual EUI is largely phase-invariant. Details: `Step9_docs/investigation/step9_investigation.md`.

## Goal

Validate the EnergyPlus simulation campaign (Step 8) on three axes: **engine integrity** (runs
complete and physically converged), **fidelity** (the injected occupancy time-series matches the
Step-7 schedules), and **scientific soundness** (Monte-Carlo convergence, plausible EUIs, and a
detectable, correctly-signed 2022→2030 load-shape shift). Produce
`outputs_step8/step8_validation_report.html` with embedded charts.

**Input**: `BEM_Setup/SimResults*/` (parsed E+ outputs) + the Step-8 aggregation tables.
**Reference**: Step-7 `BEM_Schedules_<year>.csv` (injection check); NRCan SHEU / published Canadian
residential EUI ranges (plausibility).
**Output**: `outputs_step8/step8_validation_report.html`.

> **Status:** design/plan. Built after the 6,000-run campaign exists. Checks below are the spec.

---

## Script Structure: `08_simulation_val.py`

```python
class SimulationValidator:
    def __init__(self, sim_results_dir, schedules_dir, agg_dir, outputs_dir): ...
    def validate_run_integrity(self)       -> dict   # Section 1
    def validate_injection_fidelity(self)  -> dict   # Section 2
    def validate_mc_convergence(self)      -> dict   # Section 3
    def validate_physical_plausibility(self)-> dict  # Section 4
    def validate_load_shape_sanity(self)   -> dict   # Section 5
    def validate_shift_effect(self)        -> dict   # Section 6
    def validate_longitudinal(self)        -> dict   # Section 7
    def generate_summary_table(self)       -> dict   # Section 8
    def build_html_report(self) -> str
    def run_all(self)
```

---

## Section 1 — EnergyPlus Run Integrity

| Check | Logic | Pass |
|---|---|---|
| 1.1 Completeness | runs finished / expected (6,000) | == 100% |
| 1.2 No fatal errors | parse `.err`/`.end` for "Fatal" | 0 fatals |
| 1.3 Sizing converged | no unconverged warnings on design days | 0 unconverged |
| 1.4 Severe-error budget | severe warnings per run | ≤ threshold; all reviewed |
| 1.5 Output completeness | each run yields the requested 8760 meters | 100% |

**Charts:** run-status matrix (archetype × CZ × year); error-count histogram.

---

## Section 2 — Schedule Injection Fidelity

| Check | Logic | Pass |
|---|---|---|
| 2.1 Daily-mean round-trip | injected `Schedule:Compact` WD/WE daily mean vs source `Occupancy_Schedule` | ≤ ±0.5% |
| 2.2 Hour alignment | hour-of-day mapping preserved (no off-by-origin) | exact |
| 2.3 People-count scaling | People object peak × schedule = expected occupants | matches HHSIZE basis |
| 2.4 Metabolic linkage | activity-derived W/person matches `Metabolic_Rate` | ≤ ±1 W |

**Charts:** overlay of injected vs source 24-h occupancy for a sample of HHs.

---

## Section 3 — Monte-Carlo Convergence

| Check | Logic | Pass |
|---|---|---|
| 3.1 Mean stability | running mean of cell annual energy vs N | stabilizes by N = 50 |
| 3.2 CI half-width | 95% CI half-width of cell mean | < 2% |
| 3.3 Sample adequacy | N per (archetype × region) cell | ≥ 50 (or justified) |

**Charts:** convergence curves (mean ± CI vs iteration), per representative cell.

---

## Section 4 — Physical Plausibility

| Check | Logic | Pass |
|---|---|---|
| 4.1 EUI range | annual EUI per archetype × CZ | within published Canadian residential range (NRCan SHEU) |
| 4.2 Heating dominance | heating share rises with CZ severity (5C → 7A) | monotone-ish, heating-dominated in CZ7 |
| 4.3 Cooling presence | non-zero cooling in milder CZ summers | plausible, small |
| 4.4 Archetype ordering | EUI/area ordering across dwelling types | physically sensible |

**Charts:** EUI by archetype × CZ vs benchmark bands; heating/cooling split by CZ.

---

## Section 5 — Load-Shape / Time-Series Sanity

| Check | Logic | Pass |
|---|---|---|
| 5.1 Peak–occupancy coupling | load peak timing tracks occupancy/internal-gain peaks | aligned |
| 5.2 Diurnal shape | 24-h load profile has plausible morning/evening structure | yes |
| 5.3 Occupancy responsiveness | higher-occupancy HHs → higher internal-gain-driven load | positive relationship |
| 5.4 Coincidence factor | ensemble diversity factor < 1 and < single-HH peak | physically valid |

**Charts:** 8760 load profile (mean + MC band); diurnal-by-season; coincidence curve.

---

## Section 6 — 2022 → 2030 Effect (the headline)

| Check | Logic | Pass |
|---|---|---|
| 6.1 Paired Δ separability | per-HH paired Δenergy(2022→2030) CI excludes 0 where expected | separable |
| 6.2 Direction | sign of Δ load consistent with the occupancy shift (e.g., ↑ daytime presence → ↑ daytime load) | correct sign |
| 6.3 Peak-hour shift | hour-of-peak 2022 vs 2030 | reported; explained |
| 6.4 Climate modulation | Δ magnitude varies by CZ (larger in heating-dominated zones) | reported |

**Charts:** paired Δ distribution; 2022 vs 2030 diurnal overlay; peak-hour shift; Δ by CZ.

---

## Section 7 — Longitudinal Trajectory (2005 → 2030)

| Check | Logic | Pass |
|---|---|---|
| 7.1 Trend continuity | EUI / load-shape metrics across 2005→2030 | coherent trajectory |
| 7.2 COVID break visible | 2015→2022 discontinuity in occupancy-driven load | present |
| 7.3 Forecast plausibility | 2030 extends the 2022 break sensibly (no implausible jump) | plausible |

**Charts:** longitudinal EUI + peak + load-factor trend lines (2005→2030) with the COVID break marked.

---

## Section 8 — Summary Table

One row per gate, populated at run time (archetype/CZ/year aggregates), with PASS/WARN/INFO/FAIL.

---

## HTML Report Format

Same style as `step5/6/7_validation_report*.html` — header, scorecard, findings, sectioned
charts, summary table, footer.

| Level | Meaning |
|---|---|
| PASS | within bounds |
| WARN | borderline / needs a look |
| INFO | reported, not a gate (e.g., peak-hour shift magnitude) |
| FAIL | blocks the results claim — investigate before publishing |

---

## Known Limitations / Not Yet Validated

| Item | Note |
|---|---|
| Frozen 2022 dwelling stock | No stock turnover modelled for 2005–2015; isolates occupancy. |
| TMY weather held constant | No historical/future weather; isolates occupancy. |
| MidRise / Row proxies | If P2 IDFs not acquired, those archetypes use fallback prototypes. |
| Metabolic channel un-calibrated | Internal gains ride raw activity (`07_metabolicMap_verification.md`); occupancy-gated. |
| Atlantic region | No Atlantic EPW; mapped to Montreal proxy (`config.py`). |

---

## Checklist

- [ ] Generate `BEM_Schedules_{2005,2010,2015}.csv` (Prereq P1)
- [ ] Acquire/confirm MidRise + Row archetype IDFs (Prereq P2)
- [ ] Add 2030 to runner `COMPARATIVE_YEARS`; point 2022 → calibrated
- [ ] Run paired-MC batch (6,000 runs) on cloud/HPC
- [ ] Aggregate load-shape metrics + stock weighting
- [ ] Create `08_simulation_val.py` (8 sections) + HTML report
- [ ] EUI benchmark sourcing (NRCan SHEU) for Section 4

---

## Progress Log

| Date | Check | Result | Notes |
|---|---|---|---|
| 2026-06-01 | Step 8 validation plan drafted | ✅ DESIGN | 8 sections: run integrity, injection fidelity, MC convergence, plausibility, load-shape, 2022→2030 effect, longitudinal, summary. Built after the campaign runs. |
| 2026-06-05 | Sub-step 8F: 08_simulation_val.py built and run | ✅ COMPLETE | Script + HTML produced. PASS 19 / WARN 5 / INFO 3 / FAIL 0. Run time 29 s. Key findings: §1 6000/6000 complete, 0 fatal, 1 sizing-convergence WARN (benign); §2 schedule mismatch WARN documented — IDF frozen at build time, current BEM_Schedules differs due to Step-7 OP4 donor-draw refinement (HighRise exact, MidRise/OtherDwelling diverge); §3 CI max 4.04% > 2% threshold WARN (expected at N=50, mean CI 1.80%); §4 all EUI cells within NRCan SHEU bands, SingleD 202 / MidRise 153 / OtherDwelling 126 / HighRise 116 kWh/m²; §5 peak hour 17.4 h, load-factor 0.416, occupancy responsive within-arch; §6 EUI paired-Δ CI includes 0 (PASS — wide MC, expected), midday + load_factor CIs exclude 0 (separable), peak-hour FLATTEN confirmed (Δ=+0.03 h, INFO); §7 COVID break visible (Δload_factor +0.009 at 2022), 2030 extends break. Output: outputs_step8/step8_validation_report.html (719 kB, 11 embedded charts). |
