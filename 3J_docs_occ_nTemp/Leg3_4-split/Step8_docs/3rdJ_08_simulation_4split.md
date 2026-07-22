# 3J Leg-3 — Step 8: Four-Channel BEM Simulation (MAIN DOC)
### Mixed-use Tall/SuperTall 2-city sweep, all four channels injected · TWO MANDATORY PROBES before any campaign · dual-basis EUI + load-weighted plant attribution (dr_L3-10)

---

## 0. Locked Decisions (inherited + Leg-3)

| OD | Decision | Resolution |
|---|---|---|
| OD-8H | Interpolate to Timestep | **No** (inherited Leg 2; uniform across retail + hotel) |
| OD-8I-L3 | MC design | **Deterministic, no MC** — the whole campaign is population-fraction/multiplier-driven (the Leg-2 office pattern); no per-household sampling in the towers |
| L3-P | Probes | **Mandatory pre-campaign** (see §7) — scenario-differentiation + stale-output guard |
| L3-R | Reporting basis | **Dual-basis EUI + hourly load-weighted plant allocation + MEP proration** (dr_L3-10, OD-12) |
| L3-E | EUI gates | as-modelled band = PASS criterion; empirical band = INFO (per channel, §9) |

## 1. Aim

End-to-end EnergyPlus runs of the geometry-identical mixed-use prototypes with all four channels injected per Tag-2, producing one EUI table per **scenario × climate × channel** plus load-shape and peak-timing metrics per channel band. Annual EUI is secondary — the contribution is the load shape (as in Legs 1–2).

## 2. Sub-Step Structure

| Sub | Task |
|---|---|
| 8A | Historical schedule products per cycle (2005/2010/2015 retail fractions + hotel monthly lookups; office/resid ported) |
| 8B | IDF transition check: reuse the Leg-2 v22.1→v24.2 transitioned Tall/SuperTall stock (`3rdJ_08C0` chain already run in Leg 2 — verify, don't redo) |
| 8C | **Probes** (§7) — gate the campaign |
| 8D | Campaign: injection (`inject_mixed_use`) + simulation array |
| 8E | Aggregation (per-channel attribution) + validation + figures |

## 3. Inputs

- **Step-7 products** (4 channels × scenarios) + `commercial_integration.py` (wiring gate already passed — Step-7 W-section).
- **Buildings:** `CAN_MTL/{Tall,SuperTall}Building_*_Z6_v24.2` and `CAN_CLG/*_Z7A_v24.2` (transitioned stock from Leg 2; SuperTall 40,846 m² / Tall 26,750 m² verified identical across cities → EUI deltas isolate climate).
- **EPWs:** Montreal McTavish 716120 (6A), Calgary Olympic Park 712350 (7A).
- **Cluster:** Speed; EnergyPlus 24.2 SIF (`/speed-scratch/o_iseri/step9_spike/energyplus_24.2.0.sif`), singularity wrapper with **`--bind /speed-scratch --bind /nfs/speed-scratch`** (the Cycle-7 lesson: python resolves the symlink), wrapper scripts NEVER in `/tmp` (noexec), `_ensure_output_objects()` called on **every** path (Output:SQLite + hourly meters — the office SQL-gap lesson), no `capture_output=True` on EP calls in diagnostic mode.

## 4. Run Matrix

| Axis | Values | Count |
|---|---|---|
| Building | Tall, SuperTall | 2 |
| City/climate | MTL Z6, CLG Z7A | 2 |
| Scenario | Default(NECB) + 2005 + 2010 + 2015 + 2022 + 3 bundles (B-cons/B-central/B-opt) + 6 one-at-a-time sensitivities (per Step-7 matrix) | 14 |
| **Total** | deterministic, 1 run per cell | **56 runs** |

Small campaign (vs Leg-2's 8,652) — array `#SBATCH --array=0-55`, each task ≈ minutes-to-hours. Walltime still `-t 7-00:00:00` (hard rule).

## 5. Two-Channel → Four-Channel Handling

- Residential REPLACE + office MODULATE: verbatim Leg 2 (rides `inject_mixed_use`'s residential/office branches).
- Retail: `modulate_baseline()` on People/Lights/Equipment per the Step-9 rules (Lights/HVAC follow opening hours; plug follows staff — the People multiplier is the customer signal; `Lmin = 0.15`, `Pbase = 0.20` floors kept).
- Hotel: `modulate_baseline_monthly()` on GuestRoom5/6/7; amenity + service Spaces baseline (OD-6).
- Fall-back guarantee active: any missing product reverts that channel to baseline and **logs it loudly** in the run manifest (a silently-baseline channel would poison the differentiation probe).

## 6. Cluster Execution Plan

**HARD RULES (unchanged):** sbatch only, never blocking srun; no bare python on the login node; single-line commands; 7-day walltime; ≥ 30-min monitoring spacing; expect `AssocGrpCpuLimit` slow drain (~4–8 concurrent slots — not a bug).

Upload tree `/speed-scratch/o_iseri/step8_4split/upload/…` mirroring the repo; `run_mixeduse_array.sh` (56 tasks); **injector-version fingerprint in every output path** (`outputs_step8/campaign_<INJ_HASH>/<cell>/`) — the stale-output guard is structural, not procedural: a wiring fix changes the hash, which invalidates every completion check automatically. `--no-skip` flag additionally available.

## 6b. 🔴 PRE-LAUNCH DISCIPLINE (2J + Leg-2 improvement-campaign lessons, 2026-07-15/18 — all mandatory)

1. **Complete input inventory, md5-verified both ends, written down BEFORE launch.** One table: every scenario → the exact schedule file it reads → local md5 == cluster md5; plus the injector (`commercial_integration.py`), `eSim_bem_utils` modules, **and the launcher scripts themselves** (Leg-2: `run_office_array.sh` was simply absent on the cluster; `integration.py` was a stale pre-fix version — both caught only by hashing, either would have poisoned the campaign). *Verify the artifact, not the assumption that it's there.* Note `main.py`'s scenario→file map is the ground truth for what the campaign actually reads — open it; the Leg-2 campaign was cancelled 25 min in because 3 scenarios silently read stale historical schedules nobody had listed.
2. **8A §0 gates run BEFORE any launch** — the historical-schedule generator's own gates (schema byte-identical to 2022, row counts, continuity) are declared mandatory-pre-launch; the Leg-2 relaunch happened because this was skipped once.
3. **Residential branch: per-zone carrier replication (2J Bug A).** The tower apartment zones are multi-zone; any neutralize-legacy + single-zone-carrier implementation collapses whole-building equip/lights to ~1/N. Use the FIXED `integration.py` lineage (per-zone carriers, fallback occupancy-zone). Retail/hotel are MODULATE-in-place (no neutralize+carrier) — structurally immune, assert it stays that way. **Verified Leg-2 finding: the multi-zone fix is energy-neutral on annual aggregates (building totals conserved) — never claim it "restored" energy; scope any claim to zone-level load distribution.**
4. **Meter coverage closure (2J Bug B).** Request per-end-use `Output:Meter`s covering **everything electric — including `WaterSystems:Electricity`** (2J: 100 %-electric DHW was ~80 % of MidRise electricity yet invisible to post-processing) and gas equivalents. Validator gate: Σ(requested end-use meters) ≈ `Electricity:Facility` per run (unmetered-end-use tripwire). DHW matters doubly here: hotel guest rooms are DHW-heavy.
5. **Completeness = row count AND mtime freshness, together.** A stale pre-fix `hourly_meters.csv` (or `eplusout.end`) can have a valid row count; existence alone proves nothing. The injector-hash output path (§6) makes this structural; the audit re-checks both anyway.
6. **Single-writer discipline**: exactly one process ever runs against a campaign tree (2J: a 5-min duplicate launch corrupted 12 files).
7. **Archive jobs: guard the source AND check the return code** (a Leg-2 archive `mv` silently failed on a wrong path, `mkdir -p` + `echo` faked success); use `cp -a` + per-file md5 for irreplaceable baselines, `mv` only when duplication is impossible.
8. **One-off helper scripts get committed to the repo step folder**, never left in agent scratchpads (2J: two repair scripts existed only in scratchpads and caused false "not found" flags).

## 7. 🔴 TWO MANDATORY PROBES (lessons from Leg 2 — run BEFORE the full campaign; sbatch, small)

1. **Scenario-differentiation probe.** One building (SuperTall MTL), ≥ 2 scenarios per channel varied one at a time (Default vs 2022; B-central vs one sensitivity per channel) → diff `hourly_meters.csv` per channel meter. **Byte-identical outputs across scenarios = automatic FAIL** — the modulation is not reaching the engine, regardless of how correct the inputs look (this exact symptom hid the Leg-2 People-field bug through 7 "successful" scenarios).
2. **Stale-output guard check.** Verify the fingerprint mechanism: rerun one probe cell after touching the injector → new output dir created; header-only or partial `hourly_meters.csv` = FAIL (8,760 rows required).

Campaign submission is **blocked** until both probes PASS (validator §P).

## 8. Aggregation & Reporting (dr_L3-10, locked)

`3rdJ_08_simulation_4split_agg.py` (`--rebuild` flag):

- **Per-channel attribution:** zone-level meters mapped Space→channel via the Tag-2 census.
- **Central plant:** **hourly load-weighted allocation** — each timestep, split shared chiller/boiler electricity + gas across channels by share of total simulated coil load. Never area-weighted, never unattributed.
- **Dual-basis EUI per channel:** (1) **CFA** of the channel's Spaces — primary, thermodynamic; (2) **occupiable share of GFA** — stock-comparison basis for SCIEU/CEUD INFO bands. CFA reads ~5–10 % higher than GFA-basis databases (the known basis mismatch — the Leg-2 SingleD-WARN analogue); **state the basis on every table and figure**.
- **Service/MEP (~52 % gross):** prorated by area onto the four channels when comparing to stock EUIs; kept as a separate fifth "core" row in as-modelled tables.
- Outputs: `agg_diurnal.csv`, `agg_annual.csv`, `agg_meta.csv`, `agg_peak.csv` (+ per-channel columns), `outputs_step8/agg/`.
- **Figures:** stacked diurnal load curves (winter + summer × weekday + weekend, all four channels coincident — the load-timing story) and per-channel end-use EUI stacked bars (heating, cooling, fans, pumps, interior lighting, equipment, DHW). Capture per-end-use diurnals from the start (`InteriorLights:Electricity`, `InteriorEquipment:Electricity` meters per zone group — the Leg-2 re-aggregation lesson: schema additions force a full `--rebuild`).

## 9. EUI plausibility gates (as-modelled = PASS; empirical = INFO)

| Channel | As-modelled PASS band (kWh/m²/yr) | Empirical INFO band | Source |
|---|---|---|---|
| Office | central 135 [100–200] | 230 [170–360] SCIEU/CEUD | Leg 2 (job 1054800 precedent) |
| Retail | central 110 [**80–155**] | 280 [150–380] | dr_L3-02 (locked 2026-07-02) |
| Hotel | central 240 [**180–300**] | 350 [220–480] | dr_L3-03 (locked 2026-07-02) |
| Residential (tower apartments) | HighRise SHEU 130.6 [113.9–147.2] as INFO context (tower ≠ SHEU stock basis) | — | Leg-2 §4.1 lineage |

Floor-area sanity: per-channel EUI shares vs parsed occupiable shares within **±2 pp** (project-novel gate — ASHRAE 211 suggests the comparison, no code enforces it; dr_L3-10).

## 10. Paper positioning (dr_L3-10 novelty matrix — encode in the Methods draft)

Unclaimed combination: **one longitudinal TUS database (GSS 2005–2022 + 2030) driving four channels inside a single vertically stacked mixed-use tower.** Differentiate: Doma & Ouf (2023, 2024 — SafeGraph, district-scale, no forecast), Buttitta & Finn (2020), Widén & Wäckelgård (2010 — residential-only, single-wave). Reviewer-exposure checklist already answered by design: double-counting (dr_L3-12 projection), basis mismatch (dual-basis), plant allocation (load-weighted). Stated limitation: ground-level EPW on a supertall (no altitudinal gradient).

## 11. References

Pipeline STEP 8; dr_L3-02/03/10; Leg-2 Step-8 doc (operational war-stories: IDF transition, singularity binds, tcsh `--wrap` quirks — all still apply).

## Progress Log

*(append entries below — dated `###` entries; job IDs; fix-cycle numbering if needed)*
