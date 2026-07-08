# 2J Step 8 — Residential Heating/Cooling Dominance Investigation (§4 Physical Plausibility)

**Authored:** 2026-07-07 · **Status:** ROOT CAUSE ESTABLISHED (inherited from 3J, confirmed on 2J data) — fix NOT applied; re-sim SEQUENCED AFTER the 3J Leg-2 coolfix is executed and verified (user decision 2026-07-07)
**Why this exists:** while fixing the same anomaly in the 3J Leg-2 two-channel report, the user
noticed the 2J (single-channel) `outputs_step8/step8_validation_report.html` §4 shows the same
signature: residential cooling rivals or exceeds heating in cold Canadian climate zones. Since
the 2J paper is at submission stage (`readySubmission.md`), this needs its own paper-facing
diagnosis and a scoped re-sim plan.

**Companion (read first for the full mechanism trace):**
`3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`
— diagnosis independently verified and Mechanism A directly proven by a winter-cooling probe
(§8.1 there). This doc establishes that the same defect applies to 2J and quantifies it on 2J's
own outputs.

---

## 0. The observed anomaly (2J report §4)

2J validator gates 4.2/4.3 (`08_simulation_val.py:620-640`) both PASS, yet the underlying
end-use split is physically wrong for apartments in cold zones. Exactly as in 3J, **neither
gate can catch it**: 4.2 only checks heating share *rises* cold→warm (`shares[-1] >
shares[0]*1.3` → PASS/WARN only), 4.3 only checks cooling is *present* (`cool_min > 0.05` →
PASS/WARN only). Neither compares heating to cooling, and neither can ever emit FAIL.

## 1. Confirmed data: the anomaly is real on 2J outputs, archetype-specific, and pervasive across all 5 years

From `outputs_step8/agg/agg_annual.csv` (6,000 rows = 4 arch × 6 cities × 50 HH × 5 years),
year 2022, **CZ 7A (Winnipeg)**, per-m² annual energy-transfer means:

| Archetype | Heating (kWh/m²/yr) | Cooling (kWh/m²/yr) | Cooling/Heating |
|---|---|---|---|
| SingleD | 36.28 | 25.69 | 0.71x (heating-dominated — physically fine) |
| OtherDwelling | 25.04 | 23.44 | 0.94x (borderline-fine) |
| HighRise | 16.08 | 29.84 | **1.86x** |
| MidRise | 10.39 | 34.91 | **3.36x** |

Same archetype-graded skew as 3J (houses fine, apartments inverted), and heating of 10–16
kWh/m²/yr for Winnipeg apartments is implausibly low. The cooling/heating ratio in CZ7A is
**stable across every campaign year** (MidRise 3.2–3.7x, HighRise 1.8–2.0x for 2005/2010/2015/
2022/2030) — this is a static-input artifact, not an occupancy-scenario effect.

**Magnitude note vs 3J:** the skew is milder than 3J's (3.4x/1.9x here vs 9.8x/5.3x there).
The two pipelines inject different occupancy/lighting schedule sets into the same templates, so
the internal-gain profiles — the *trigger* — differ in magnitude; the *mechanism* (below) is
identical. The milder ratio does not make 2J acceptable: cooling exceeding heating at all in a
5,670-HDD climate is the anomaly.

## 2. Root cause — identical to 3J, by construction

Both mechanisms live in the static prototype IDFs, which **physically reside in this pipeline's
tree** (`2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/`) — 3J merely borrows them:

- **Mechanism A — frozen cooling setpoint.** `NECB-G-Thermostat Setpoint-Cooling` in both
  `ASHRAE901_Apartment{MidRise,HighRise}_STD2022_Buffalo_NECB17_Z6_v242.idf` is a single
  `Through: 12/31` block, every hourly value 24.0 °C, all day-types, all year (verified
  programmatically in the 3J investigation §7 — same files). Internal gains (lights 2.15 W/m²,
  equip 5.0 W/m², schedule floor never fully off) + solar push zones past 24 °C regardless of
  outdoor temperature → mechanical cooling in deep winter. **Directly proven** for these
  templates by the 3J winter-cooling probe (same IDF, same Winnipeg EPW; only the injected
  occupancy schedules differ): in January, MidRise cooling exceeded heating; the SingleD
  control showed ~0 winter cooling.
- **Mechanism B — one Z6 envelope for all 6 CZs.** 2J's `run_bem.py:40-47` `resolve_cell()`
  picks the IDF by archetype substring only from the single fixed `STEP8_BUILDINGS_DIR`
  (`eSim_bem_utils_2J/main.py:76`); only the EPW varies per city. The 2J campaign is therefore
  a Zone-6 envelope driven by six different weather files, same as 3J.

Ruled out (same checks as 3J, same files/meters): meter swap (`heating_ET_kWh`/`cooling_ET_kWh`
map to the standard `Heating:EnergyTransfer`/`Cooling:EnergyTransfer` meters), zone multipliers
(all =1 in both apartment IDFs).

## 3. Which pipeline step is responsible

Same attribution as 3J: Steps 1–7 (occupancy channel) are untouched and remain valid — the
defect enters only where Step 8 consumes the static templates (`resolve_cell()` /
`STEP8_BUILDINGS_DIR`). A fix means new IDF inputs + re-running Step 8's affected subset, then
the downstream aggregation/validation/Step-9 refresh.

## 4. Fix options (mirroring 3J; option numbering kept aligned)

1. **(Chosen for 3J; natural choice here) Seasonal cooling-setpoint relief on IDF copies.**
   The 3J coolfix (variant 1a: 28.0 °C Oct–Apr / 24.0 °C May–Sep, design-day rows kept at 24.0)
   produces patched copies in `...Leg2_2-split/Step8_docs/Buildings_MTL_v242_3Jfix/`. For 2J:
   reuse the **byte-identical patched apartment IDFs** so both journals share the same corrected
   physics — point `eSim_bem_utils_2J/main.py:76` at the patched dir (or a 2J-local copy of it;
   naming/location is an execution detail to settle at 2J GO — do NOT edit the original
   `Buildings_MTL_v242/` templates in place, they are the provenance record of what the
   submitted-version results used).
   **2J re-sim scope: 3,000 of 6,000 runs** (MidRise + HighRise × 6 cities × 50 HH × 5 years);
   houses untouched. Then re-run the 2J aggregation + `08_simulation_val.py` (8E-equivalent) +
   Step-9 (`09_activityDrivenLoads_val.py` — note 2J Step-9 SHEU 48/48 and EUI figures will
   move and must be re-validated).
2. **(Deferred, same as 3J) Per-CZ code-appropriate envelopes.** Bigger lift, full re-sim;
   record as paper limitation instead.
3. **(Validator-side, do regardless) Heat-vs-cool dominance gate** in `08_simulation_val.py`
   §4 (mirror 3J's new gate 4.9: per archetype × CZ∈{6A,6B,7A}, FAIL if cooling/heating > 2.0
   in 7A, WARN if > 1.25 in 6A/6B/7A). Current 4.2/4.3 can never FAIL — that gap is what let
   this ship in both journals.

## 5. Decision gate — SEQUENCED, not immediate (user decision 2026-07-07)

**Agreed sequencing:** (1) execute the 3J Leg-2 coolfix first
(`step8_coolfix_implementation_plan.md` / `step8_coolfix_employee_prompt.md`, ready to run);
(2) verify its acceptance criteria (CZ7A apartment ratios → O(1), DJF cooling collapse, 0-FAIL
scorecard); (3) **only then** decide the 2J re-sim GO with the proven patch. No 2J code, IDF,
or paths change until that GO. Paper implication to keep in view: `readySubmission.md` cites
pre-fix Step-8/Step-9 numbers — if the paper is submitted before the 2J re-sim, the §4 end-use
split and apartment EUI values in it are known-affected (heating understated, cooling
overstated for MidRise/HighRise); either hold those claims or complete the 2J re-sim first.

## 6. Test method (when 2J GO is given)

- Reuse the 3J smoke pattern before the 3,000-run spend: 2 cells (MidRise + HighRise ×
  Winnipeg_7A × 2022, n=2) with the patched IDFs through the 2J runner, then the winter probe
  (`...Leg2_2-split/Step8_docs/investigation/probe_winter_cooling.py` — point `STEP8_CAMP_DIR`
  at the 2J smoke outputs; layout `<arch>__<city>/sample_*/<year>/hourly_meters.csv` matches).
- Acceptance: before/after CZ7A table vs §1 above (target ratios O(1)); 2J scorecard 0 FAIL
  including the new dominance gate; house archetypes bit-identical (not re-run).
- Optional pre-GO evidence (cheap): run the winter probe on 5 existing 2J CZ7A apartment runs
  from cluster scratch to demonstrate 2J's own winter cooling directly (the 3J probe result
  transfers by construction, but a 2J-native table is stronger for the paper's response letter
  if reviewers ask).

---

## Progress Log

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-07 | Investigation opened; anomaly confirmed on 2J data (this doc) | ROOT CAUSE ESTABLISHED — awaiting 3J coolfix verification before 2J re-sim GO | User spotted the same §4 signature in the 2J report during the 3J investigation. Confirmed from local `outputs_step8/agg/agg_annual.csv`: CZ7A 2022 cooling/heating MidRise 3.36x, HighRise 1.86x (houses 0.71x/0.94x — fine); ratio stable across all 5 campaign years → static-input artifact. Root cause = same two template mechanisms as 3J (templates live in THIS tree; 3J borrows them); Mechanism A already probe-proven on the same IDFs+EPW in the 3J investigation §8.1. 2J gates 4.2/4.3 confirmed PASS/WARN-only (`08_simulation_val.py:620-640`) — same validator gap. Scope if GO: 3,000/6,000 runs + agg/val/Step-9 refresh; sequencing per user = 3J first, verify, then 2J. No code/IDF modified. |
