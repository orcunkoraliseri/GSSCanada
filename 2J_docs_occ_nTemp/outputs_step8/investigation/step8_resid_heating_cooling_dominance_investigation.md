# 2J Step 8 — Residential Heating/Cooling Dominance Investigation (§4 Physical Plausibility)

**Authored:** 2026-07-07 · **Status:** ROOT CAUSE SUPERSEDED 2026-07-08 (see §7) — the 3J coolfix falsified Mechanism A; true cause = metering artifact (thermostat-independent ERV ventilation air on `Cooling:EnergyTransfer`). **NO re-sim needed for 2J** — the planned 3,000-run scope is CANCELLED; revised fix = re-aggregation + validator re-base only (2J-equivalent of 3J Fix v3), sequenced after the 3J canonical full-campaign regen (cluster currently unavailable)
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

## 7. SUPERSEDING UPDATE (2026-07-08) — true root cause is a METERING ARTIFACT; Mechanism A retired; NO 2J re-sim

The 3J coolfix execution **falsified Mechanism A experimentally**: raising the apartment winter
cooling setpoint 24.0 → 28.0 → 40.0 °C (verified-correct injected schedules) left DJF
`Cooling:EnergyTransfer` unchanged (~100–104% of pre-fix). The manager then root-caused the
anomaly from the preserved smoke outputs — full trace in the 3J investigation **§11**
(`3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`):

- `Cooling:EnergyTransfer` = Σ `Zone Air System Sensible Cooling Energy` per zone (proven from
  `eplusout.mtd`) — net sensible cooling delivered by **any** air system, NOT compressor energy.
- Every apartment zone in these templates has a thermostat-independent
  `ZoneHVAC:EnergyRecoveryVentilator` (24 in MidRise, 46 in HighRise; HX only, no coil, no
  thermostat link). In a cold-climate winter, post-heat-recovery supply air is below room
  temperature → metered as "cooling" at **zero electricity**. The compressor never ran in
  winter, even at the 24.0 °C setpoint. Houses have no per-zone ventilation air system — that,
  not their thermostat, is why SingleD/OtherDwelling looked "clean".
- On the true **end-use** metric (ABUPS End Uses: Cooling Electricity vs Heating fuel), 3J's
  CZ7A apartments came out **heating-dominated** (cooling/heating 0.67× MidRise, 0.71×
  HighRise); the residual 1.4–1.8× cooling-heaviness in 6A/6B is a code-prototype
  characteristic (dense ASHRAE gains + tight STD2022 envelope + ERV recovery) → paper caveat,
  not a bug. 3J's re-based report was verified and accepted 2026-07-08 (0 FAIL).

**Consequences for this doc:**

- **§2 Mechanism A is RETIRED.** The frozen 24.0 °C setpoint drives nothing in winter; the §1
  table reads `heating_ET_kWh`/`cooling_ET_kWh` — the artifact meter — so it demonstrates the
  metric asymmetry, not a physical defect. The "implausibly low" Winnipeg apartment heating in
  §1 is likewise an ET-basis reading, to be re-judged on end-use fuel. Mechanism B (one Z6
  envelope for all CZs) still stands as a separate, real limitation → paper note.
- **§4 option 1 (patched IDFs + 3,000-run re-sim) is CANCELLED.** The 2J templates were never
  broken and were never modified. All 6,000 existing 2J runs remain valid.
- **§4 option 3 survives, re-based:** the dominance gate must compare **end-use** cooling
  electricity vs heating fuel (not ET), mirroring 3J's re-based gate 4.9 (FAIL > 2.0× in 7A;
  WARN > 1.25× in 6A/6B/7A), plus relabeling any ET-based §4 chart as "air-system delivered
  sensible energy (incl. ventilation air)".
- **§6 test method is obsolete** (it probes the artifact meter). The 2J acceptance test is the
  3J one: extractor dry-run against a run with known `eplustbl.csv` End-Uses values, then
  end-use ratio table per archetype × CZ.

**Revised 2J fix (2J-equivalent of 3J Fix v3 — re-aggregation only):**

1. 2J's runner persists `eplusout.sql` per run by design (`Step8_docs/eSim_bem_utils_2J/main.py:1994`
   — same docstring/mechanism as 3J), so the ABUPS End Uses table is already on cluster scratch
   for all 6,000 runs. Port 3J's `extract_enduse_annual.py` (stdlib sqlite,
   `TabularDataWithStrings` / `AnnualBuildingUtilityPerformanceSummary` / `End Uses`; **keep the
   3J unit fix — house prototypes report kBtu, apartments GJ**) to the 2J campaign layout →
   `agg_enduse_annual.csv`.
2. Add the end-use dominance gate + end-use table to `08_simulation_val.py` §4 and relabel the
   existing ET-based split; regenerate `outputs_step8/step8_validation_report.html`.
3. Both steps run on the cluster via `sbatch` (extractor, then validator
   `--dependency=afterok:`). **Blocked until Speed is back** (unavailable as of 2026-07-08);
   sequence after the 3J canonical full-campaign regen so the ported extractor is re-verified
   first.
4. Expected outcome (to confirm, not assume): 2J's ET ratios (3.36×/1.86×) are milder than 3J's
   ET ratios were, and 3J's end-use result flipped 7A to heating-dominated — 2J plausibly
   lands at/below WARN territory. The gate decides.

**Paper implication — materially improved vs §5's warning:** `readySubmission.md`'s EUI /
site-energy / SHEU numbers were **never affected** (site energy is metered correctly; the
artifact only affects the ET-based heating-vs-cooling split reading). What remains for the paper
is (a) re-basing any heating-vs-cooling-dominance claim on the end-use table once extracted, and
(b) the Mechanism-B and prototype-cooling-heaviness caveats. The "hold the submission for a
3,000-run re-sim" tension in §5 is dissolved.

---

## Progress Log

| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-07 | Investigation opened; anomaly confirmed on 2J data (this doc) | ROOT CAUSE ESTABLISHED — awaiting 3J coolfix verification before 2J re-sim GO | User spotted the same §4 signature in the 2J report during the 3J investigation. Confirmed from local `outputs_step8/agg/agg_annual.csv`: CZ7A 2022 cooling/heating MidRise 3.36x, HighRise 1.86x (houses 0.71x/0.94x — fine); ratio stable across all 5 campaign years → static-input artifact. Root cause = same two template mechanisms as 3J (templates live in THIS tree; 3J borrows them); Mechanism A already probe-proven on the same IDFs+EPW in the 3J investigation §8.1. 2J gates 4.2/4.3 confirmed PASS/WARN-only (`08_simulation_val.py:620-640`) — same validator gap. Scope if GO: 3,000/6,000 runs + agg/val/Step-9 refresh; sequencing per user = 3J first, verify, then 2J. No code/IDF modified. |
| 2026-07-08 (later) | Execution package authored (manager): `step8_enduse_rebase_implementation_plan.md` + `step8_enduse_rebase_employee_prompt.md` (this folder) | READY FOR EXECUTION — local-first, ZERO sbatch (login-node ls/tar/scp only); fresh Sonnet employee session | Un-blocks §7's plan without waiting for cluster compute: fetch 600-file 2022 `eplustbl.csv` subset (CZ 6A/6B/7A × 4 arch) from scratch via one-shot tar+scp (3J precedent), extract locally (kBtu/GJ unit-aware), add gate 4.9/4.10 + end-use chart + ET relabel + `--section` arg to `08_simulation_val.py`, produce §4-local + merged HTMLs; canonical report untouched until the cluster-era full regen. |
| 2026-07-08 | Root cause superseded (§7 added): metering artifact, Mechanism A retired | RE-SIM CANCELLED — revised fix = re-aggregation + validator re-base (3J Fix-v3 port); BLOCKED on cluster availability | 3J fix v2 smoke falsified Mechanism A (24/28/40 °C → DJF cooling ET unchanged); true cause = thermostat-independent ERV ventilation air on `Cooling:EnergyTransfer` (3J investigation §11). 3J's re-based end-use report verified & accepted 2026-07-08 (CZ7A apartments heating-dominated 0.67–0.71×; 0 FAIL). 2J templates never broken; all 6,000 runs stay valid; `eplusout.sql` persisted per run (`eSim_bem_utils_2J/main.py:1994`). Revised plan in §7: port `extract_enduse_annual.py` (with kBtu/GJ unit fix) + end-use dominance gate + ET relabel in `08_simulation_val.py`, regen report via chained sbatch — after 3J canonical regen, once Speed is back. Paper: readySubmission.md EUI/site-energy numbers unaffected; only dominance-split claims need re-basing. No code/IDF modified. |
| 2026-07-08 (later) | §7 revised fix EXECUTED, local-only (2JV3-A…F, employee); full detail logged in `step8_enduse_rebase_implementation_plan.md` | **CLOSED — gate 4.9 PASS, 0 FAIL, ratio table confirms end-use flip on 2J's own data** | Ported the 3J extractors (`eplustbl.csv` variant; dry-run exact-matched the 3J smoke ground truth 78.34/136.12), fetched a 600-file 2022 subset (CZ 6A=Montreal/6B=Calgary/7A=Winnipeg × 4 archetypes × 50 samples) from `/speed-scratch/o_iseri/GSSCanada/SimResults_Step8_corrected_v2/campaign_N50` via one `ls`+one `ls`+one one-shot `tar`+one `scp` (zero sbatch, zero compute), extracted 600/600 rows with 0 skips, hand-verified both unit families (GJ apartment + kBtu house) exactly against raw `eplustbl.csv`. **§1's original ET-basis table is superseded by the true end-use ratios (mean cooling_elec/mean heating_fuel, n=50/cell):** HighRise 6A=0.34×/6B=0.37×/7A=0.26×; MidRise 6A=0.40×/6B=0.32×/7A=0.26×; OtherDwelling 6A=0.35×/6B=0.20×/7A=0.20×; SingleD 6A=0.22×/6B=0.14×/7A=0.15× — every archetype × CZ is heating-dominated (≤0.40×), well under both the 1.25× WARN and 2.0× FAIL thresholds, and more decisively than 3J's 0.67–0.71× CZ7A result. Added gate 4.9 (can FAIL; PASSed) + gate 4.10 (INFO table) + a new true-end-use chart to `08_simulation_val.py` §4, relabeled the ET-based gates 4.2/4.3 and chart as "air-system delivered sensible energy (incl. ventilation air)" without changing their PASS/WARN logic, and added a `--section` CLI flag. Produced `step8_validation_report_v3_section4_local.html` (local §4-only run) and `step8_validation_report_v3_merged.html` (spliced into a copy of canonical; scorecard 24→25 PASS, 3→4 INFO, 0 WARN/FAIL; non-§4 sections verified byte-identical; canonical file untouched, md5-verified). **Paper implication:** the §0/§1 "implausibly low apartment heating" and cooling-exceeds-heating readings were entirely an artifact of the `:EnergyTransfer` metric; on true fuel/electricity end-use energy 2J's residential heating/cooling split is physically unremarkable in every tested cold CZ. `readySubmission.md` EUI/site-energy numbers remain unaffected (as established in §7); any heating-vs-cooling-dominance narrative in the paper should now cite this end-use table, not the §0/§1 ET table. Full-campaign canonical regen (all 6,000 runs via sqlite extractor + full validator, chained sbatch) remains a separate later-phase task once Speed compute is back, sequenced after the 3J canonical regen — out of scope for this pass. |
