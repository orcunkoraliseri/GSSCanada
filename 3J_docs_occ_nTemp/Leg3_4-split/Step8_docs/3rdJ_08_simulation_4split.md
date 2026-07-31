# 3J Leg-3 — Step 8: Four-Channel BEM Simulation (MAIN DOC)
### Mixed-use Tall/SuperTall 2-city sweep, all four channels injected · TWO MANDATORY PROBES before any campaign · dual-basis EUI + load-weighted plant attribution (dr_L3-10)

---

## 0. Locked Decisions (inherited + Leg-3)

| OD | Decision | Resolution |
|---|---|---|
| OD-8H | Interpolate to Timestep | **No** (inherited Leg 2; uniform across retail + hotel) |
| OD-8I-L3 | MC design | **Deterministic, no MC** — ~~the whole campaign is population-fraction/multiplier-driven (the Leg-2 office pattern); no per-household sampling in the towers~~ **AMENDED 2026-07-28 by OD-8R-L3 below.** The commercial channels remain fraction/multiplier-driven; the residential channel does draw households, but deterministically (fixed seed), so "no MC" still holds in the sense that matters — one run per cell, reproducible, no ensemble |
| **OD-8R-L3** | **Residential collapse rule** (user decision 2026-07-28; resolves the gap found while arming the §P probes) | **One distinct household per residential `Space`, drawn at a fixed seed** from the Step-7 per-household product (`BEM_Schedules_4split_<cycle>.csv`, keyed `SIM_HH_ID`). N = the building's residential Space count (Tall = 30; SuperTall = TBD, higher — the rule is per-Space, not literally 30). *Rationale:* deterministic and reproducible; preserves the inter-household diversity that is the entire point of driving BEM from a time-use survey; avoids the mean-across-households collapse, which would flatten the coincident residential peak — the load-shape story is the contribution (§1), so flattening it would defeat the study. **Sub-questions RESOLVED 2026-07-28 → see §7b:** draw pool = condo/apartment only (`DTYPE`/`CONDO`), `Number_of_People` = `HHSIZE`, seed = **42**. Specified but **not yet implemented**. |
| L3-P | Probes | **Mandatory pre-campaign** (see §7) — scenario-differentiation + stale-output guard |
| L3-R | Reporting basis | **Dual-basis EUI + hourly load-weighted plant allocation + MEP proration** (dr_L3-10, OD-12) |
| L3-E | EUI gates | as-modelled band = PASS criterion; empirical band = INFO (per channel, §9) |

## 1. Aim

End-to-end EnergyPlus runs of the geometry-identical mixed-use prototypes with all four channels injected per Tag-2, producing one EUI table per **scenario × climate × channel** plus load-shape and peak-timing metrics per channel band. Annual EUI is secondary — the contribution is the load shape (as in Legs 1–2).

## 2. Sub-Step Structure

| Sub | Task |
|---|---|
| 8A | Historical schedule products per cycle (2005/2010/2015 retail fractions + hotel monthly lookups; office/resid ported) |
| 8B | ✅ **DONE 2026-07-28** — IDF transition check: reuse the Leg-2 v22.1→v24.2 transitioned Tall/SuperTall stock (`3rdJ_08C0` chain already run in Leg 2 — verify, don't redo). 4/4 present + AUDIT-W 9P/1W/0F (jobs 1169582, 1169584) |
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

## 7b. ✅ RESOLVED 2026-07-28 — residential draw pool + occupancy count

OD-8R-L3 fixed *how many* households and *that the draw is seeded*. The three sub-questions it
left open were put to the user and answered the same day; all three change publishable results,
which is why they were escalated rather than assumed:

1. **Pool filter — DECIDED: condo/apartment only.** Drawing uniformly from the full ~23 115-HH
   frame would put single-detached households inside a supertall tower. The draw is restricted to
   apartment/condo dwelling types using the Step-7 product's `DTYPE` / `CONDO` columns. *The exact
   column values constituting "condo/apartment" must be read off the data and written into the
   implementing script's docstring — do not guess them.* Bedroom-count matching to the prototype's
   unit mix was **not** adopted; if it is later, it is a new OD.
2. **`Number_of_People` per Space — DECIDED: from `HHSIZE`**, as in Leg 2 (one household = one
   dwelling), not the IDF's NECB apartment default. Without this the drawn households' diversity
   would enter the schedule *shape* but not the load *magnitude* — half the effect lost.
3. **Seed — DECIDED: 42.** The literal value is recorded here, and the resulting
   `SIM_HH_ID → Space` assignment must be persisted in the run manifest. Deterministic in
   principle is not reproducible in practice unless the realised mapping is written down.
4. **Per-zone carrier discipline (2J Bug A) still applies.** Residential is REPLACE, and the
   tower apartment Spaces are multi-zone in the Leg-2 lineage; the neutralize-legacy +
   single-zone-carrier implementation collapses whole-building equipment/lights to ~1/N. Use the
   fixed per-zone-carrier lineage (`integration.py` md5 `6a92268be1f8dc3301df3bec80d6dd2e`).
   Note the Leg-2 finding: that fix is **energy-neutral on annual aggregates** — never claim it
   "restored" energy, scope any claim to zone-level load distribution.

**Status:** the rule is now fully specified, but **not yet implemented**. Probe cells 0–6
(job 1169664) were built and submitted *before* this resolution, so they leave residential at
NECB baseline; P1's residential leg stays **NOT EXERCISED** for that array and requires a
separate residential-injection build + its own wiring audit (residential W-gates) before any
energy run — the Leg-2 lesson is that wiring is asserted at the IDF level *first*, never inferred
from energy output afterwards.

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

### 2026-07-28 — 8B verified + AUDIT-W PASS (jobs 1169582, 1169584)

**8B — v24.2 stock verified, not redone.** The four Leg-2 transitioned IDFs are present on scratch under
`/speed-scratch/o_iseri/step8_2split/upload/3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/`:

| City | File | Bytes | mtime |
|---|---|---|---|
| CAN_MTL | `TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` | 5 142 928 | Jun 29 11:51 |
| CAN_MTL | `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` | 7 721 326 | Jun 29 12:24 |
| CAN_CLG | `TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf` | 5 142 964 | Jun 29 10:55 |
| CAN_CLG | `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z7A_v242.idf` | 7 721 362 | Jun 29 11:29 |

All four report `Version, 24.2`. Each MTL/CLG pair differs by exactly **36 bytes** (Tall 5 142 928 vs
5 142 964; SuperTall 7 721 326 vs 7 721 362) → identical geometry, climate tag only, as designed
(EUI deltas therefore isolate climate). Note the filenames retain the upstream `6A_Buffalo` prototype
token in both cities — the operative climate marker is the `Z6` / `Z7A` suffix.
**8B = PASS.** Leg-2 job `1016780` output reused; no re-transition.

**AUDIT-W.** Script `3rdJ_08W_audit_wiring.py` + launcher `.sh` (sbatch, `-p ps`, `-t 7-00:00:00`, 16 G).
§6b md5 inventory matched at both ends for all 5 artifacts before each submission.

- **Run 1 — job `1169582`** (47 s, exit 0): 8P/1W/0F, but the log carried **26 `WARN: … injection failed`**
  lines. Diagnosed: not an injection failure. `commercial_integration.py` L381/391/401 wrote
  `Interpolate_to_Timestep="No"` on LIGHTS/ELECTRICEQUIPMENT — a field that exists only on
  `Schedule:Day:Interval`, so eppy raised on every commercial load object. The schedule assignment
  precedes the throw and therefore survived; the wiring was correct all along. Confirmed textually on the
  saved IDF: 19 / 11 / 10 references to `MXU_Office_People_scenario` / `MXU_Retail_People_scenario` /
  `MXU_Hotel_GuestRoom_scenario` = 1 definition + PEOPLE + LIGHTS + ELECTRICEQUIPMENT per channel.
- **BUG-W7 fixed** (not a threshold relaxation — a defect removal). The three `Interpolate_to_Timestep`
  writes were deleted. Rationale: (a) 26 false "failed" lines per run would **mask a genuine failure**
  across a 56-run campaign; (b) the code was order-fragile — swapping the two `setattr` calls would have
  silently dropped the LIGHTS/EQUIP wiring, i.e. the Leg-2 byte-identical bug reborn. Per-class counters
  (`n_lights`, `n_equip`) added to the result dict, the verbose print and the provenance file.
- **New gate W7** added to the audit script: before today, **neither W2 nor W3 looked at anything but
  PEOPLE**, so the commercial LIGHTS/ELECTRICEQUIPMENT wiring sat under no gate at all. W7 re-classifies
  every load object off the *saved* IDF (independent of the module's own counters) and requires each
  commercial-channel object to reference the matching `MXU_*` schedule.
- **Run 2 — job `1169584`** (25 s, exit 0): **9P / 1W / 0F, zero WARN lines.**

| Gate | Result |
|---|---|
| Tag-2 census (Spaces) | PASS — residential 30 / office 33 / retail 9 / hotel 25 / service_MEP 63 = **164**, matches expectation exactly |
| Tag-2 unknown | **WARN** — 4 Spaces: `F21 Resi_bot_Plenum`, `F22-F29 Resi_mid_Plenum`, `F30 Hotel_bot_Plenum`, `F31-F37 Hotel_mid_Plenum`. Plenums, carry no PEOPLE/LIGHTS/EQUIP loads → **accepted as documented**, no injection impact |
| Tag-2 recovery on PEOPLE (module logic) | PASS — 22 PEOPLE objs → hotel 3 / hotel_support 6 / office 6 / residential 2 / retail 3 / service_MEP 2; **0 unresolved** |
| Injection | PASS — PEOPLE office 6 / retail 3 / hotel 3; `fallback=[]`; `ambiguous=0` |
| W2 field-wiring | PASS — 22 PEOPLE audited, 0 violations (the Leg-2 wrong-field bug is absent) |
| W7 LIGHTS/EQUIP wiring | PASS — office 6+6, retail 4+3, hotel 3+3; **mismatches=0** |
| W3 office | PASS — 48/48 slots differ, max abs delta 0.5144 vs `NECB-A-Occupancy` |
| W3 retail | PASS — 85/120 slots differ, max abs delta 0.9500 |
| W3 hotel | PASS — 120/120 slots differ, max abs delta 0.8221 |
| W6 pre-v24.2 fields | PASS — 0 occurrences of `Zone_Name` / `Zone_or_ZoneList_Name` |

Non-regression: run 2 reproduced run 1's PEOPLE counters exactly (6/3/3, empty fallback), so the fix is
behaviour-neutral by measurement, not by assertion.

**Documented gaps (open, non-blocking):**
1. `assert_wiring()` in `commercial_integration.py` (L436-461) **advertises W2+W3 in its docstring but
   only implements W2.** W3 is implemented in the audit script instead; the module was deliberately not
   patched for it. Manager decision pending: lift W3 into the module, or keep it validator-side.
2. W3 compares series of unequal parsed length (base 120 vs injected 48 / 144 / 1152 field slots) and
   truncates to the shorter. Deltas are large and unambiguous, so the verdict stands, but the comparison
   is resolution-naive.
3. The injector never reads `Space.Tag_2`; it exact-matches the load object's zone/space/zonelist
   reference (L373). It works on this stock because the ZoneList names coincide with the Tag-2 tokens —
   true by DOE-prototype convention, not by construction. Measured, not assumed (recovery census above).

**8B and AUDIT-W both PASS → §7 probes (P1–P4) unblocked.** Campaign still gated on those.

### 2026-07-28 — P1–P4 probe harness built + array submitted (job 1169664)

**Scope executed:** handoff `prompts/2026-07-28_employee_step8_probes_P1P4.md` §4.1–4.3 only
(write + compile-check the three files, upload + md5-verify both ends, submit the array,
confirm with `squeue`). §4.4 stop-and-report honored: gate script (§4.5) and the P3(a)
second-hash rerun (§4.6) **not** run — awaiting the array landing + manager authorization.

**Files written** (`3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/`), each `py -3 -m py_compile`
clean (`.sh` checked with `bash -n`):

| File | Local md5 | Remote md5 (post-upload) |
|---|---|---|
| `3rdJ_08P_probe_driver.py` | `a7f9dd34ffc4fb0f690be9dcfd408ef5` | `a7f9dd34ffc4fb0f690be9dcfd408ef5` — match |
| `3rdJ_08P_probes.sh` | `5676471cdc2543f5fa34b8be17c4eb22` | `5676471cdc2543f5fa34b8be17c4eb22` — match |
| `3rdJ_08P_probe_gates.py` | `ffad50902f01fa9a2ad6b0d3748ded13` | `ffad50902f01fa9a2ad6b0d3748ded13` — match |

Also uploaded (2030 Step-7 products needed by cells 1–4; central + opt variants only —
`_cons` variants exist but no probe cell uses them, so not uploaded this pass) and
md5-verified both ends:

| File | Local md5 | Remote md5 |
|---|---|---|
| `office_presence_multiplier_2030.csv` | `9507fbd6b760d5e1ac965b3fbbbd8981` | match |
| `retail_presence_multiplier_2030_central.csv` | `bfb89627979922d885f11c80277d4fdb` | match |
| `retail_presence_multiplier_2030_opt.csv` | `337ac1b508e6d042f05c9f109037dc45` | match |
| `hotel_schedule_multiplier_2030_central.csv` | `4b3d3a4603cc0cccc6a1bf42139d69ee` | match |
| `hotel_schedule_multiplier_2030_opt.csv` | `e0ab6c86fbe3c0ea2475f8cada6d1bd6` | match |

Injector re-verified (already uploaded, unchanged since AUDIT-W): local and remote
`eSim_bem_utils/commercial_integration.py` both md5 `5670f6026a91577126cd1329f60acb1a`
(matches the handoff's stated hash) — confirms no stale injector risk before submission.

**EPW path — verified, no discrepancy (corrected 2026-07-28 by the manager).** An earlier draft
of this entry recorded the handoff as having pointed at a nonexistent `step8_4split` EPW path;
that is wrong. The handoff (§2) states the **step8_2split** path, which is the correct and only
location: `/speed-scratch/o_iseri/step8_2split/upload/BEM_Setup/WeatherFile/CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw`,
alongside the reused v24.2 IDF stock. Verified present by `ls` before writing the constant into
the driver. `IDF_SUPERTALL`, `SIF`, `IDD`, and the python env path were likewise all verified
present exactly as stated in the handoff. *(Logged because a false "the spec was wrong" note in a
permanent record is itself a defect — §6b's verify-the-artifact discipline cuts both ways.)*

**Driver design (`3rdJ_08P_probe_driver.py`), key decisions:**
- `INJ_HASH = md5(commercial_integration.py)[:8]`, output root
  `/speed-scratch/o_iseri/step8_4split/probes/campaign_<INJ_HASH>/<cell_tag>/` — never hard-coded.
- 7-cell table built exactly per handoff §3.2 (cell 0 `baseline_necb` = empty `channels` dict;
  cells 1–4 one-at-a-time off `B_central`; cell 5 `cycle_2022`; cell 6 `fallback_retail` points
  its retail `csv` at a deliberately nonexistent file, never created).
- `_ensure_output_objects()`: adds `Output:SQLite=SimpleAndTabular` if absent, 12 hourly
  `Output:Meter`s (the full electric+gas list incl. `WaterSystems:Electricity`, 2J Bug B),
  3 hourly `Output:Variable(Key_Value="*")`s, and forces `RunPeriod` to Jan 1–Dec 31 if it
  isn't already (idempotent — checked, not assumed; the source IDF's own RunPeriod is
  already full-year, verified by `grep` on the cluster before writing this logic).
- SQL→CSV extraction: **reimplemented locally**, not a direct import of Leg-2's
  `eSim_bem_utils_3J/plotting.py::get_hourly_meter_data` (that module lives under
  `Leg2_2-split/Step8_docs/`, outside this driver's `PYTHONPATH`) — ported the same
  `ReportData`/`ReportDataDictionary`/`Time`/`EnvironmentPeriods` join shape
  (`EnvironmentType=3`, `ReportingFrequency='Hourly'`), restricted to the requested
  meters/variables, pivoted to one column per meter (`hourly_meters.csv`) or per
  `<channel>_<metric>` (`channel_hourly.csv`). `channel_hourly.csv`'s zone→channel map is
  built the same way as AUDIT-W's Tag-2 census: walks `SPACE` objects on the *injected* IDF,
  reads `Tag_2` (fallback `Space_Type_Name`/`Space_Type`/`Name`), classifies via
  `classify_tag2()`, aggregates `residential+residential_common`, `office+office_support`,
  `retail`, `hotel+hotel_support`, `service_mep` — same aggregation AUDIT-W Block 2 uses.
- Manifest carries `FALLBACK_LOUD` + the `!!! FALLBACK: <channel> reverted to NECB baseline !!!`
  stdout banner whenever `inject_mixed_use()`'s own `fallback` list is non-empty. Note this
  fires for **cell 0 on all three commercial channels by design** (nothing was requested —
  it's the un-injected NECB reference), not only for cell 6's deliberate retail gap; the gate
  script's P4 checks target cell 6 specifically (`FALLBACK_LOUD == ["retail"]`), so this is
  not a conflict.

**Gate script (`3rdJ_08P_probe_gates.py`) written but NOT run** (§4.5 is out of scope this
pass). Implements P1 (per-channel max|Δ|, both the one-at-a-time-vs-`B_central` comparison
and the `B_central`-vs-`baseline_necb` comparison, plus INFO cross-checks on the unvaried
channels; residential always INFO/NOT-EXERCISED), P2 (md5 collision check, cells 0–5), P3a
(path/hash consistency for whatever `campaign_*` dirs exist now — the full "hash flips on
wiring change" proof needs the §4.6 second submission, explicitly flagged INFO/pending here)
and P3b (row-count-AND-mtime-freshness, together), P4 (cell 6 `FALLBACK_LOUD`, SLURM-log
banner, byte-for-byte retail-column identity vs cell 0).

**Submission:** `sbatch 3rdJ_08P_probes.sh` → **job `1169664`** (`--array=0-6`, `-p ps`,
`--cpus-per-task=4`, `--mem=16G`, `-t 7-00:00:00`). `squeue -u o_iseri` confirmed all 7 tasks
running immediately after submission (`1169664_0`..`1169664_6`, state `R`, nodes
magic-node-03/04/05/07/08/09 + speed-24).

**Stopped here per instruction.** Not polling in a loop; next check at ≥30 min. When the
array lands: verify exit codes / row counts / manifests, then (on manager authorization)
submit `3rdJ_08P_probe_gates.py` (§4.5) and report the P1–P4 scorecard with numbers, and
only after that append the injector-comment-line + cell-1-only rerun for P3(a) (§4.6).

**Nothing in the spec could not be satisfied** in this pass, other than the out-of-scope
items §4.4–4.6, which were deliberately not started.

### 2026-07-28 — channel_hourly.csv case-mismatch bug fixed (job 1169671 diagnosis) + postprocess-only recovery armed (job 1169672)

**Confirmed bug.** `channel_hourly.csv` came out with 0 rows on every cell. Cause: EnergyPlus
writes zone-variable `KeyValue` in **ALL-CAPS** in `ReportDataDictionary` (e.g.
`'BASEMENT_CORRIDOR ZN'`), but `_build_zone_channel_map()` built `zone_to_channel` from the
IDF's `SPACE`/zone names in **mixed case** (e.g. `'Basement_Corridor ZN'`). The `.map()` in
`_write_channel_hourly_csv()` therefore returned NaN for 100% of rows and the `dropna` emptied
the table. The three variables (`Zone People Occupant Count`, `Zone Lights Electricity Energy`,
`Zone Electric Equipment Electricity Energy`) ARE present in the SQL, hourly, `Type='Sum'`,
`IndexGroup='Zone'` — purely a join-key casing mismatch, nothing missing from the simulation.

**Fix (`3rdJ_08P_probe_driver.py`):**
- `_build_zone_channel_map()` (~L313-334): keys now built as `zone_name.upper()` instead of
  bare `zone_name`, with a comment recording why (EnergyPlus uppercases `KeyValue`, diagnosed
  job 1169671, 2026-07-28).
- `_write_channel_hourly_csv()` (~L373-398): `df["KeyValue"]` is now `.str.strip().str.upper()`
  before `.map(zone_to_channel)`, matching the canonical upper-case key. Diagnostic printing
  made loud: prints `mapped=<n> unmapped=<n> (of <n> report rows)` unconditionally, plus (if
  any unmapped) up to 10 distinct unmapped `KeyValue` strings verbatim. **Hard error added:**
  if `n_mapped == 0`, raises `RuntimeError` *before* any CSV is written (never a silent 0-row
  file "produced") — this propagates through the existing exception handler and the existing
  8,760-row gate, so exit stays non-zero with a clear message. A *small* unmapped set is
  explicitly NOT a failure (the 4 known plenum Spaces — `F21 Resi_bot_Plenum`,
  `F22-F29 Resi_mid_Plenum`, `F30 Hotel_bot_Plenum`, `F31-F37 Hotel_mid_Plenum` — carry no
  Tag-2/loads, accepted-as-documented per the AUDIT-W entry above).
- `driver_md5` added to the manifest (both the normal path and `--postprocess-only`), computed
  as `md5_file(os.path.abspath(__file__))`. Rationale recorded in-code: `INJ_HASH` fingerprints
  the *injector* (`commercial_integration.py`) only, so a post-processing-only change to this
  driver correctly does not invalidate the simulation output path — but the derived CSVs'
  provenance still needs to trace back to the exact driver code that produced them.
- New `--postprocess-only` CLI flag: skips injection and the EnergyPlus run entirely; requires
  `<outdir>/run/eplusout.sql` and `<outdir>/injected.idf` to already exist (errors clearly,
  exit 1, if either is missing), loads the existing `manifest.json` if present (else starts a
  minimal one), re-derives `hourly_meters.csv` + `channel_hourly.csv` via a new shared
  `_do_postprocess()` helper (factored out of the step-5 block so both code paths call the
  same logic), and rewrites `manifest.json`. Row-count gate (8,760) and exit-code behavior
  otherwise unchanged.

**Compile-check:** `py -3 -m py_compile 3rdJ_08P_probe_driver.py` clean, locally.

**Upload + md5 verification (both ends match):**

| File | Local md5 | Remote md5 |
|---|---|---|
| `3rdJ_08P_probe_driver.py` | `ed36feb8ddee26281c5deb88275baf53` | `ed36feb8ddee26281c5deb88275baf53` — match |
| `3rdJ_08P_postprocess.sh` | `56eee11bacad6c1071da35fcd99d0ffa` | `56eee11bacad6c1071da35fcd99d0ffa` — match |

Nothing else was uploaded (no re-upload of `commercial_integration.py` or Step-7 CSVs — unchanged,
already verified in the prior entry).

**Recovery array chained, not polled.** `3rdJ_08P_postprocess.sh` written (SLURM array
`--array=0-6`, `-p ps`, `--cpus-per-task=4`, `--mem=16G`, `-t 7-00:00:00`, same `EPLUS_IDD` /
`PYTHONPATH` / python env as `3rdJ_08P_probes.sh`, log to
`/speed-scratch/o_iseri/step8_4split/logs/8P_post_%A_%a.out`), running
`3rdJ_08P_probe_driver.py --cell $SLURM_ARRAY_TASK_ID --postprocess-only`. Submitted with
`sbatch --dependency=afterany:1169664` → **job `1169672`**. `afterany` (not `afterok`) is
deliberate: cell 6 (`fallback_retail`) already FAILED (exit 1, by design — the P4 fall-back
trip wire) but its `eplusout.sql` is valid and must be recovered too.

**Deviation from spec, flagged explicitly (not worked around silently):** the spec expected
`squeue` to show the new job queued in a `Dependency` state. By the time it was submitted, job
`1169664`'s array had already finished (its own `squeue` entry was gone), so SLURM's `afterany`
condition was satisfied immediately and `1169672_0..6` went straight to state `R` (running) on
`gomory`/`speed-24`, never appearing in a Dependency (`PD`) state to observe. The dependency
mechanism itself was still exercised correctly — the job would not have been submittable/queued
without a valid, already-satisfied dependency id — but there was no window in which to *see* the
`Dependency` reason string, since it never had a reason to wait.

**Stopped here per instruction.** Gate script not run, no polling loop started, residential
work not started. Job `1169672` will land the recovered `channel_hourly.csv` (and rewritten
`manifest.json`) for all 7 cells; next check should be ≥30 min out and by the user/manager, not
this session.

### 2026-07-28 — §P scorecard: 23P / 0W / **2F** (job 1169679) — retail sensitivity is a silent duplicate

**Recovery worked.** Probe array `1169664`: all 7 cells FAILED exit 1 on the zone-name case bug
(the driver's row-count gate caught it — a 0-row `channel_hourly.csv` was never passed off as
success). Their EnergyPlus output was nonetheless valid, so recovery array `1169672`
(`--postprocess-only`, `--dependency=afterany:1169664`) re-derived both CSVs from the existing
`eplusout.sql` in **~40 s per cell** instead of re-simulating at ~38 min per cell. All 7
COMPLETED exit 0, `mapped=5 045 760 unmapped=0`, 8 760 rows in both CSVs. The 6 unclassified
Space names are plenums (`F38 Resi_bot_Plenum ZN` etc.; SuperTall has 6 where Tall has 4) — they
carry no loads, hence contribute no report rows, hence `unmapped=0`. Consistent, expected,
accepted-as-documented.

**Scorecard (job `1169679`, exit 1):**

| Gate | Verdict | Evidence |
|---|---|---|
| P1 office, cell 2 vs 1 | **PASS** | max\|Δ\| people **16.49**, lights 8.20e6, equip 1.11e7 |
| P1 office, cell 1 vs 0 | **PASS** | max\|Δ\| people **128.10**, lights 7.90e7, equip 1.19e8 |
| P1 retail, cell 3 vs 1 | 🔴 **FAIL** | max\|Δ\| people **0.0**, lights **0.0**, equip **0.0** |
| P1 retail, cell 1 vs 0 | **PASS** | max\|Δ\| people **117.15**, lights 6.62e7, equip 6.48e7 |
| P1 hotel, cell 4 vs 1 | **PASS** | max\|Δ\| people **1.95**, lights 7.75e5, equip 1.32e6 |
| P1 hotel, cell 1 vs 0 | **PASS** | max\|Δ\| people **27.90**, lights 1.03e7, equip 1.81e7 |
| P1 residential | INFO | NOT EXERCISED — see §7b, rule specified 2026-07-28 but not implemented |
| Cross-channel leakage | **PASS** (6 INFO) | every unvaried channel max\|Δ\| = 0.0 in every pair — injection is cleanly channel-scoped |
| P2 byte-identity | 🔴 **FAIL** | cell 1 (`B_central`) and cell 3 (`var_retail`) share md5 `949aceb7b45e2073dcc666b780a90dfb` |
| P3a current-hash | **PASS** | campaign dir hash == live injector md5 (`5670f602`) |
| P3a second-hash rerun | INFO | not performed — §4.6, deliberately deferred |
| P3b completeness | **PASS** ×14 | all 7 cells × 2 CSVs: rows = 8 760 **and** mtime newer than the injected IDF |
| P4 FALLBACK_LOUD | **PASS** | cell 6 manifest `FALLBACK_LOUD=['retail']` |
| P4 banner | **PASS** | `!!! FALLBACK` found in the cell-6 SLURM log |
| P4 reversion identity | **PASS** | cell 6 vs cell 0 retail columns identical, max\|Δ\| = 0.0 |

**Root cause of both FAILs — one defect, and it is UPSTREAM in Step 7, not in the wiring**
(diagnostic job `1169680`):

- The driver did **not** misconfigure the cells: cell 1 read `retail_..._2030_central.csv`
  (md5 `bfb89627…`), cell 3 read `retail_..._2030_opt.csv` (md5 `337ac1b5…`). Different files,
  different injected-IDF md5s. Ruled out first.
- For `PR=QC`, the two products differ in **exactly one column**: `at_retail_fraction`
  (max\|Δ\| 0.008206, 120 of 144 rows). **`multiplier` is identical, max\|Δ\| = 0.**
- `load_retail_series()` consumes **only** `multiplier`. So both cells produced numerically
  identical 144-slot `Schedule:Compact` objects (n_differing = 0), hence identical energy.
- Interpretation: the 2030 band scaling (B-central 1.00 vs B-opt 1.05) was applied to
  `at_retail_fraction` but **never propagated into `multiplier`**. The ratio checks out —
  0.008206 / ~0.15 ≈ 5 %, i.e. exactly the 1.05 factor.

**Why this matters more than a probe failure.** Had the campaign run, the retail sensitivity axis
would have returned *identical* results for B-central and B-opt with entirely plausible EUIs, and
nothing downstream would have flagged it. This is the Leg-2 byte-identity symptom reproduced in a
new place — the precise failure §7 was written to catch. **The gates are NOT to be relaxed**: P1
retail and P2 stay FAIL until the Step-7 retail product is regenerated with the band scaling
propagated into `multiplier`, after which cells 1 and 3 must be re-simulated (not merely
re-post-processed — the schedule itself changes) and the scorecard re-run.

**SCOPE OF THE DEFECT (checked locally, same day).** Worse than the one probed pair, and the
cause is structural:

| Channel | Bands compared | `multiplier` differs? |
|---|---|---|
| **Retail** | cons vs central, cons vs opt, central vs opt | 🔴 **NO — all three identical, Δ=0** |
| Retail | 2022 vs any 2030 band | yes, Δ 0.7253 |
| Hotel | cons/central/opt, all pairs (+2022) | yes, Δ 0.059–0.126 (0.18–0.25 vs 2022) |
| Office | conservative/hybrid/fullyhybrid, all pairs | yes, Δ 0.115–0.149 |
| Residential | 4 scenario files | distinct size+md5 only — **column-level NOT verified** |

So **all three 2030 retail bands are one and the same scenario** at the BEM interface; the retail
axis of the campaign has 2 distinct states (2022, "2030"), not 4. Hotel and office are clean,
consistent with their passing probes.

**Root cause — `Step7_docs/3rdJ_07_aug_to_bem_4split.py`, `_retail_rows_from_slotarray()`:**
```
421  peak = float(arr_clock48.max())
422  shape = arr_clock48 / peak if peak > 0 else np.zeros(48)
423  multiplier_raw = 0.95 * shape
```
`arr_clock48` is the **band-levered** `at_retail_fraction` array. Line 422 normalizes it by **its
own peak**, so any level-only rescale the band lever applied cancels exactly. The band signal
survives into the `at_retail_fraction` output column (diagnostic, unread) and is destroyed in
`multiplier` (the only column `load_retail_series()` consumes). `build_retail_product_2030()`
(L456) calls this identically for all three bands, so all three collapse together.

**This is a design decision, not a mechanical patch — manager/user call required.** Two candidate
fixes: **(a)** normalize by a *fixed reference* peak instead of each band's own peak (reference =
the central band's peak leaves central bit-identical and lets cons/opt scale relative to it —
minimally invasive, preserves the already-validated central case); **(b)** keep self-normalization
and multiply by an explicit band constant (retail 0.90 / 0.97 / 1.05 per the Step-7 bundle
definition). (a) is recommended: it preserves the existing shape semantics rather than layering a
second scaling concept on top. Either way this changes Step-7 published product values, so it is
escalated, not applied unilaterally.

**Campaign remains blocked.** Open items, in order: (1) the Step-7 retail `multiplier` defect
above — decide (a) vs (b), regenerate all three 2030 retail bands, **re-simulate** cells 1+3, re-run
the scorecard; (1b) close the residential column-level gap (its 4 files differ, but only by
size/md5 — a level-destroying normalization in that path would be invisible to that check);
(2) the residential injector (§7b — rule now specified, seed 42, condo/apartment pool,
`HHSIZE`) plus its own wiring audit; (3) sub-step 8A historical products (2005/2010/2015) and the
6 one-at-a-time sensitivity product sets, none of which exist; (4) the Calgary EPW tagged `_6B`
on disk where §3 says 7A.

---

## 2026-07-28 — fix (a) retail `multiplier` : normalisation par pic de référence central

**Employee session, executing the manager-authored fix + a mid-task manager-issued resolution.**
Continues the defect logged above (§ "Root cause -- `_retail_rows_from_slotarray()`").

### Mapping scenario -> bande (confirmed by code, not assumed)

`BUNDLE_MAP["central"]["retail_scenario"] = "plateau"` (`3rdJ_07_aug_to_bem_4split.py:150`),
wired to the output filename by `cmd_year_2030`: `cfg = BUNDLE_MAP[bundle]` (L791) ->
`retail_states = [(bundle, cfg["retail_scenario"])]` (L798) -> `retail_out =
build_retail_product_2030(scenario)` (L846) -> `out_ret = OUT_DIR /
f"retail_presence_multiplier_2030_{blabel}.csv"` (L848). So `blabel="central"` <->
`scenario="plateau"` <-> `retail_presence_multiplier_2030_central.csv`, unambiguous. `cons` <->
`shift`, `opt` <-> `renaissance`.

### Blocker found BEFORE writing code, and how it was resolved

Original instruction was option (a) anchored to **central's own peak** (self-referential, keeps
central bit-identical). Before implementing, traced the raw Step-6 lever files
(`at_retail_fraction_2030_{shift,plateau,renaissance}.csv`) and found `levered = base * lever`
**exactly**, a uniform scalar per band, confirmed numerically at every slot (std ~1e-14): shift
lever 0.90, plateau (central) lever 0.97, renaissance (opt) lever 1.05 -- matching
`RETAIL_LEVER_VALUE` and the raw files' own `multiplier` column exactly. Consequence: anchoring on
central's own peak forces `opt`'s multiplier to `0.95 * (1.05/0.97) = 0.95 * 1.082474 = 1.028351`
at every (Day_Type, PR) peak slot -- **> 1, an invalid EnergyPlus schedule fraction**, structurally
unavoidable under that anchor, not a data artifact. Stopped and escalated instead of clipping or
improvising. **Manager resolution (relayed mid-task):** abandon central bit-identity (it wasn't
saving anything -- cell 1 was already slated for re-simulation) and anchor instead on the
**un-levered `at_retail_fraction_2030_base` column's own peak**, matched by (Day_Type, PR). Verified
first that `base` is present and **exactly identical** (bit-for-bit, not just `np.isclose`) across
all 3 lever files -- confirmed, so this is a single shared, unperturbed reference read from the
data, not a fallback substitution.

### Conceptual diff

`_retail_rows_from_slotarray()` (`3rdJ_07_aug_to_bem_4split.py`, ~L419-490 after edit): added
`ref_peak=None` parameter. `ref_peak=None` (default) keeps the exact old self-normalizing
behaviour (`peak = arr_clock48.max()`) -- this is the **only** path `build_retail_product_2022`
uses, unmodified call site, so 2022 is untouched. `ref_peak=<float>` normalizes against that fixed
value instead. `build_retail_product_2030()` now also reads the group's
`at_retail_fraction_2030_base` column, applies the same `+4h` roll, takes its max per
(Day_Type, PR_GROUP), and passes it as `ref_peak`. Since `levered = base * lever` pointwise, this
reduces to `peak(band) = 0.95 * lever(band)` for every band -- mathematically the same result as
"self-normalize x hardcoded band constant" (rejected option (b)) **minus** the hardcoded constant
and **minus** the second source of truth; the two previously-rejected designs merge into one that
is provably safe and reads its factor from data. `shape` uses the same normalization as
`multiplier` (kept internally consistent; does not disturb 2022's behaviour, and for 2030 now
correctly shows each band's amplitude relative to the shared base peak instead of a synthetic
self-peak of 1.0). No other column, rounding, the `np.roll(arr, 8)` (+4h discipline), or the
`staff_shoulder_flag` branch (`baseline <= 0.10` -> `mult_final = baseline`) was touched.

`run_retail_gates()` **relabeled, not loosened** (project rule: never relax a gate to erase a
FAIL; only relabel with proof when the semantics genuinely changed):
- OLD: `multiplier` capped at `[0, 0.95+eps]`; peak required `== 0.95` exactly for every band, per
  (Day_Type, PR). This encoded the bug itself (self-normalization always drives peak to 0.95
  regardless of lever) -- it could never actually fail once the bug was present, so it was not
  testing anything beyond the broken invariant it depended on.
- NEW: `multiplier` capped at the real EnergyPlus physical bound `[0, 1.0+eps]` (strictly wider
  where valid, since 0.95 was never a real physical ceiling); AND
  `peak(band) == 0.95 * RETAIL_LEVER_VALUE[retail_scenario]` for 2030 (or `== 0.95` exactly for
  2022, `retail_scenario=None`, unaffected). This second check is mathematically EQUIVALENT to
  `peak(band)/peak(central) == lever(band)/lever(central)` (both reduce to `peak(x) == 0.95*lever(x)`
  for all x, since the 0.95 anchor is the shared `base` peak) and is **strictly stronger** than the
  old check: if today's bug is ever reintroduced, this assertion fails for every band whose lever
  != 1.0 (all of them), so the regression cannot reproduce silently. `run_retail_gates()` signature
  gained a `retail_scenario=None` parameter; only the 2030 call site
  (`cmd_year_2030`, retail block) passes it, the 2022 call site is unchanged (default `None`).
  Discrepancy flagged plainly: the manager's message literally said "peak of each band <= 0.95",
  but the manager's own predicted `opt` peak (0.9975) exceeds 0.95 -- I implemented the `<=1.0`
  bound (explicitly called "la vraie contrainte EnergyPlus" in the same message, and restated in
  point 3), not the `<=0.95` bound, since the two are inconsistent for `opt` and `<=1.0` is
  physically correct.

### Regeneration (minimal, no unnecessary heavy processing)

Ran the fixed functions directly via a standalone driver script (not the CLI's `--year 2030
--bundle <x>`, which would also rebuild residential/office/hotel for that bundle -- unrelated
heavy processing this fix doesn't touch). All 3 gate calls **PASSED**. 2022 was also regenerated
(cheap: 68 MB stock, 1.3 s load, 1.5 s total) to prove-by-execution the default path is intact,
rather than only proving it by code inspection.

### MD5 before / after

| File | MD5 before | MD5 after | Changed? |
|---|---|---|---|
| `retail_presence_multiplier_2030_central.csv` | `bfb89627979922d885f11c80277d4fdb` | `cf8721c62030fc7c1f23b999f85056d0` | **YES -- expected** (manager: "central DOIT changer maintenant, c'est attendu, plus un echec") |
| `retail_presence_multiplier_2030_cons.csv` | `f47de539edfedbc84905ea468ff0ca93` | `0e3b256e69713b3942161adc1ee247d2` | YES |
| `retail_presence_multiplier_2030_opt.csv` | `337ac1b508e6d042f05c9f109037dc45` | `f7152e5a887f636c4a13e5b4295555f9` | YES |
| `retail_presence_multiplier_2022.csv` | `e31f528e26bd74286a90c425921fd32b` | `e31f528e26bd74286a90c425921fd32b` | **NO -- bit-identical, confirmed by regeneration** |

(Old files backed up automatically by `atomic_write` -> `*_BAK_2026-07-28.csv` alongside the
existing `*_BAK_2026-07-23.csv` snapshots.)

### Verification (re-derived from the artifacts' own columns)

**max|delta| `multiplier` across pairs, and rows differing / 288:**

| Pair | max&#124;delta&#124; | rows differing |
|---|---|---|
| cons vs central | 0.066500 | 148 / 288 |
| central vs opt | 0.076000 | 148 / 288 |
| cons vs opt | 0.142500 | 148 / 288 |

All > 0 as required (the bug made all three exactly 0). The 140 non-differing rows/pair are the
shared zero-occupancy hours and the shoulder-flagged slots, which correctly stay identical across
bands (see below).

**Peak per band per (Day_Type, PR)** -- identical across all 6 groups within each band (uniform
scalar lever, as expected): `cons = 0.855000` (expected 0.8550, delta 0), `central = 0.921500`
(expected 0.9215, delta 0 -- **was 0.95, a -3.0% INTENDED change, not a regression**),
`opt = 0.997500` (expected 0.9975, delta 0, <= 1 valid).

**Inter-band peak ratios vs Step-6 lever ratios:** `opt/central` observed `1.082474` vs lever ratio
`1.05/0.97 = 1.082474` (delta 0.000000); `cons/central` observed `0.927835` vs lever ratio
`0.90/0.97 = 0.927835` (delta 0.000000); `opt/cons` observed `1.166667` vs `1.05/0.90 = 1.166667`
(delta 0.000000). Exact match, not approximate -- confirms the fix reproduces the Step-6 lever
ratios structurally, not coincidentally.

**Global max `multiplier`:** cons 0.855000, central 0.921500, opt 0.997500 -- all <= 1, PASS.

**`staff_shoulder_flag == 1` slots:** identical (Day_Type, PR, slot) set flagged across cons/
central/opt (132 slots each), and identical `multiplier` value at those slots between bands (max
abs diff 0.0) -- confirmed, since the NECB baseline proxy is band-independent by construction.

**New check -- non-shoulder slot dipping below adjacent shoulder baseline:** no crossing found in
any (band, Day_Type, PR) group. Note for the record: given the current NECB-proxy rescale
(x1.1875), the `baseline <= 0.10` flag condition only ever fires at literal-zero-occupancy hours in
practice (the rescaled "0.1 raw step" becomes 0.11875 > 0.10, so it never trips the flag) --
`max_shoulder_baseline` was `0.000000` in every one of the 18 (band x Day_Type x PR) groups
checked. This is a pre-existing property of the FLAGGED-OPEN-ITEM NECB proxy (see file header),
unrelated to and unchanged by this fix; it makes the crossing check structurally unable to fire
under the current proxy, which is worth noting but is not something this fix introduced or should
correct.

**Row count / columns / NaN:** all 3 files have exactly 288 rows, `RETAIL_OUT_COLS` order
unchanged. `n_persons` is NaN for all 288 rows in all 3 2030 files -- **confirmed pre-existing**
(checked against the `_BAK_2026-07-23` opt snapshot: same NaN pattern before this fix; 2030 never
carried real person counts, `n_persons=None` is passed unconditionally by
`build_retail_product_2030`, untouched by this edit). No other NaNs anywhere.

**2022 unaffected, confirmed two ways:** (1) by code -- `build_retail_product_2022` calls
`_retail_rows_from_slotarray(..., n_persons=len(sub))` with no `ref_peak` argument, so the default
`None` (self-normalizing, original behaviour) applies; the `run_retail_gates` 2022 call site
(`cmd_year_2022`) passes no `retail_scenario`, defaulting `expected_peak` back to `0.95` exactly.
(2) by execution -- regenerated it (cheap, 1.5 s total) and its MD5 is bit-identical to before.

### shape column choice

`shape` uses the same `ref_peak` as `multiplier` (not a separate self-normalization). For 2022 this
is unchanged (ref_peak=None there too). For 2030 this does not disturb `central`'s values relative
to what bit-identity would have given it, because -- as established above -- bit-identity for
`central` was abandoned entirely per the manager's resolution, not preserved; there is no longer a
"central must equal its old self" invariant to protect. Keeping `shape` and `multiplier` on the
same normalization was chosen because `multiplier = 0.95 * shape` by construction, and having them
disagree on what "1.0" means would silently reintroduce a second, contradictory normalization
concept -- exactly the kind of hidden second source of truth this fix was written to eliminate.

### Compile-check

`py -3 -m py_compile 3rdJ_07_aug_to_bem_4split.py` -- exit 0.

### Remaining work (not done in this session)

1. **Re-simulate cells 1 (`B_central`) and 3 (`var_retail`)** -- the retail schedule itself changed
   (not just post-processing), per the campaign note above.
2. **Re-run the scorecard** (P1 retail, P2 byte-identity) against the re-simulated cells; both
   should flip from FAIL to PASS now that `multiplier` differs meaningfully across bands.
3. The other three open items already logged above (§"Campaign remains blocked") are untouched by
   this session: residential injector wiring audit (§7b), sub-step 8A historical products, Calgary
   EPW tag mismatch.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

## 2026-07-28 — fix (b) retail gate: hardcoded `RETAIL_LEVER_VALUE` replaced with runtime-derived lever (second-source-of-truth defect)

**Context.** Independent counter-verification of fix (a) (retail `multiplier` re-anchored on
`at_retail_fraction_2030_base`'s own peak, see the entry directly above) flagged one open item in
the gate side, not the product side: `run_retail_gates()` validated the regenerated products
against `RETAIL_LEVER_VALUE = {"shift": 0.90, "plateau": 0.97, "renaissance": 1.05}`, a dict
hand-maintained in `3rdJ_07_aug_to_bem_4split.py`, instead of against the lever actually present in
the Step-6 lever files. Today the constant matched the data exactly (confirmed), but structurally
this is the same defect family as fix (a): a value derivable from data, copied into a second
location, that can silently go stale if Step-6 is ever regenerated with different levers -- the
gate would then PASS a product validated against a number nobody re-checked.

**No product CSVs touched this session.** Scope was gate/validator code only in
`3J_docs_occ_nTemp\Leg3_4-split\Step7_docs\3rdJ_07_aug_to_bem_4split.py`. **No re-simulation is
induced by this fix** -- product values are bit-identical before/after (see MD5 below).

**Usage audit of `RETAIL_LEVER_VALUE`** (grep, pre-fix): 3 sites -- the definition
(then-line 153), `run_retail_gates()` (then-line 685, `expected_peak = 0.95 * RETAIL_LEVER_VALUE[...]`),
and `_check_h5_monotonicity()` (then-line 977, H5 band-ordering report). Generation
(`build_retail_product_2030`) does **not** use it -- it reads `at_retail_fraction_2030_base` /
`_levered` directly from the lever file. All 3 usages are gate/reporting-side, so the constant was
removed outright and replaced (not kept as a cross-check assertion; that variant would have been
redundant here since nothing else depends on the constant).

**Replacement: `_derive_retail_lever(retail_scenario)`**, new function at
`3rdJ_07_aug_to_bem_4split.py:153` (replacing the old `RETAIL_LEVER_VALUE` dict at the same
location), called from `run_retail_gates()` (`:710`) and `_check_h5_monotonicity()` (`:1002`).
Reads `RETAIL_LEVER_FILES[retail_scenario]`'s own `multiplier` column (one row per slot, already
carrying the scalar lever value verbatim) rather than the
`at_retail_fraction_2030_levered / _base` ratio -- confirmed numerically equivalent (ratio mean
matches the `multiplier` column to <3e-14 on non-zero-base rows) but the `multiplier` column is
strictly more direct: 71 of 432 rows per lever file have `base == 0` (closed hours), which would
make the ratio an undefined 0/0 needing extra masking logic the `multiplier` column sidesteps
entirely.

**Uniformity assertion.** `_derive_retail_lever` asserts `max(multiplier) - min(multiplier) < 1e-9`
per file and raises an explicit `AssertionError` naming the file, min, max, and spread if violated
-- a non-uniform lever would mean Step-6 varies the retail *shape*, not just the *level*, which
would invalidate fix (a)'s entire premise.

**Derived levers + spread (this session):** shift = 0.9, plateau = 0.97, renaissance = 1.05 (all
exactly matching the retired constant's values, spread `hi-lo` = 0.0 in all 3 files, `multiplier`
column `nunique()` = 1 per file).

**Decisive test** (scratchpad, `test_gate_fix.py`): built a synthetic "buggy" retail product from
the real `cons` file by rescaling every non-shoulder `multiplier` to force peak = 0.95 on all 3
(Day_Type, PR) groups -- reproducing the exact self-normalization signature of the original bug.
Fed through the corrected gate:

```
buggy peaks per (Day_Type,PR): [0.95]
shift: AssertionError raised (EXPECTED) -> H2/R1 peak != expected 0.8550 (lever=shift) [BUGGY/shift] [Saturday/AB]: 0.950000
renaissance: AssertionError raised (EXPECTED) -> H2/R1 peak != expected 0.9975 (lever=renaissance) [BUGGY/renaissance] [Saturday/AB]: 0.950000
```

Both `shift` and `renaissance` raised as required; the gate can no longer silently PASS the
old bug's signature.

**Non-regression:** the 3 production 2030 CSVs (`cons`/`central`/`opt`, unchanged) and the 2022 CSV
all PASS the corrected gate: `peak=0.8550 exact (lever=shift)`, `peak=0.9215 exact (lever=plateau)`,
`peak=0.9975 exact (lever=renaissance)`, `peak=0.9500 exact (lever=None)` -- all 4 `[GATE PASS]`.

**MD5 (all 4 retail product CSVs, before session == after session, unchanged):**
`retail_presence_multiplier_2022.csv` = `e31f528e26bd74286a90c425921fd32b`;
`retail_presence_multiplier_2030_cons.csv` = `0e3b256e69713b3942161adc1ee247d2`;
`retail_presence_multiplier_2030_central.csv` = `cf8721c62030fc7c1f23b999f85056d0`;
`retail_presence_multiplier_2030_opt.csv` = `f7152e5a887f636c4a13e5b4295555f9`.

**Compile-check:** `py -3 -m py_compile 3rdJ_07_aug_to_bem_4split.py` -- exit 0.

**Open item, not addressed this session (flagged for the user to decide):**
`staff_shoulder_flag` never fires on a *reduced*-staffing hour -- the NECB baseline proxy (see file
header FLAGGED OPEN ITEM) never takes a value in (0, 0.10], so the flag only ever captures fully
*closed* hours and forces 132 of 288 slots to `multiplier = 0.0`. The name implies a "reduced
shoulder staffing" state that the current data can never actually populate; whether "assume zero
staff outside opening hours" is the intended design (vs. a reduced-but-nonzero staffing floor) is a
design decision for the user, not a bug -- and it does not affect the retail sensitivity axis
(identical across cons/central/opt by construction, since the NECB baseline is band-independent).

---

### 2026-07-28 -- employee session: retail-fix upload, archive, re-simulation launch (deployment)

**Scope corrected before execution**: cells **{1, 2, 3, 4}**, not {1, 3} as an earlier Progress Log
entry implied. `var_office` (cell 2) and `var_hotel` (cell 4) both also read
`retail_presence_multiplier_2030_central.csv` for their non-varied retail channel (see `CELLS` table,
`3rdJ_08P_probe_driver.py:92-121`), so both were stale too even though retail is not their varied
axis.

**Upload (`scp`, locally invoked, login node target)**: 3 corrected retail 2030 CSVs uploaded to
`/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/`
(`retail_presence_multiplier_2030_cons.csv`, `..._central.csv`, `..._opt.csv`). `cons` had never been
uploaded before this session (not read by any probe cell; staged now for the future 56-run campaign).
`2022` was not re-uploaded (md5 unchanged, per doc).

**MD5 inventory, local vs cluster (post-upload):**

| File | Local md5 | Cluster md5 | Concorde ? |
|---|---|---|---|
| `retail_presence_multiplier_2030_cons.csv` | `0e3b256e69713b3942161adc1ee247d2` | `0e3b256e69713b3942161adc1ee247d2` | OUI |
| `retail_presence_multiplier_2030_central.csv` | `cf8721c62030fc7c1f23b999f85056d0` | `cf8721c62030fc7c1f23b999f85056d0` | OUI |
| `retail_presence_multiplier_2030_opt.csv` | `f7152e5a887f636c4a13e5b4295555f9` | `f7152e5a887f636c4a13e5b4295555f9` | OUI |
| `retail_presence_multiplier_2022.csv` | `e31f528e26bd74286a90c425921fd32b` | `e31f528e26bd74286a90c425921fd32b` | OUI (inchangé, non re-téléversé) |
| `eSim_bem_utils/commercial_integration.py` | `5670f6026a91577126cd1329f60acb1a` | `5670f6026a91577126cd1329f60acb1a` | OUI |
| `3rdJ_08P_probe_driver.py` | `ed36feb8ddee26281c5deb88275baf53` | `ed36feb8ddee26281c5deb88275baf53` | OUI |
| `3rdJ_08P_probes.sh` | `5676471cdc2543f5fa34b8be17c4eb22` | `5676471cdc2543f5fa34b8be17c4eb22` | OUI |
| `3rdJ_08P_gates.sh` | `d6b2c513022846ffa1aa87b8b49c62f4` | `d6b2c513022846ffa1aa87b8b49c62f4` | OUI |
| `3rdJ_08P_postprocess.sh` | `56eee11bacad6c1071da35fcd99d0ffa` | `56eee11bacad6c1071da35fcd99d0ffa` | OUI |
| `3rdJ_08P_probe_gates.py` | `ffad50902f01fa9a2ad6b0d3748ded13` | `ffad50902f01fa9a2ad6b0d3748ded13` | OUI |

All concord -- gate to proceed satisfied (had any of the 3 retail 2030 CSVs diverged, execution would
have stopped here; it did not need to).

**Job 1 -- disk guard + archive** (`3rdJ_08P_archive_retailfix.sh`, new file, uploaded then `sbatch`):
job **1169799**. Confirmed by log (`logs/8P_archive_1169799.out`): 9.4 TB free on
`/speed-scratch` (`filer-speed:/userdata/speed_scratch`, well above the 5 GB floor) -> proceeded ->
renamed all 4 dirs under `probes/campaign_5670f602/` to `<tag>_PRE_RETAILFIX_20260728`
(`B_central`, `var_office`, `var_retail`, `var_hotel`) -> listing confirms rename, not copy (`baseline_necb`,
`cycle_2022`, `fallback_retail` untouched, as expected -- their inputs are not stale).

**Job 2 -- re-simulation** (`3rdJ_08P_probes.sh`, existing file, unmodified): job **1169800**,
`sbatch --dependency=afterok:1169799 --array=1-4 -t 7-00:00:00 …`. Verified before submission by
reading the script: `SLURM_ARRAY_TASK_ID` is passed straight through as `--cell $SLURM_ARRAY_TASK_ID`,
and the driver's `CELLS` list (`3rdJ_08P_probe_driver.py:90-122`) indexes directly by that integer --
so `--array=1-4` maps 1:1 onto cells `B_central`(1), `var_office`(2), `var_retail`(3), `var_hotel`(4),
no offset. Real simulation, not `--postprocess-only`. `squeue` immediately after submission showed all
4 array tasks (`1169800_1..4`) already `R` on `magic-node-03/04/05/07` (Job 1 cleared its dependency
right away).

**Job 3 -- scorecard** (`3rdJ_08P_gates.sh`, existing file, unmodified): job **1169804**,
`sbatch --dependency=afterok:1169800 -t 7-00:00:00 …`. Pending on the array dependency at submission
time. Expect 4 FAIL/stale->PASS transitions on cells 1-4 once it lands, plus (correctly) unresolved
FAILs on cells 0/5/6 which were never in scope for this fix -- do not treat those as regressions, and
do not touch any gate threshold to clear them.

**Exact commands submitted (cluster, one per line):**
```
scp retail_presence_multiplier_2030_cons.csv retail_presence_multiplier_2030_central.csv retail_presence_multiplier_2030_opt.csv o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/outputs_step7/
scp 3rdJ_08P_archive_retailfix.sh o_iseri@speed.encs.concordia.ca:/speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/
ssh o_iseri@speed.encs.concordia.ca 'sbatch /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08P_archive_retailfix.sh'
ssh o_iseri@speed.encs.concordia.ca 'sbatch --dependency=afterok:1169799 --array=1-4 -t 7-00:00:00 /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08P_probes.sh'
ssh o_iseri@speed.encs.concordia.ca 'sbatch --dependency=afterok:1169800 -t 7-00:00:00 /speed-scratch/o_iseri/step8_4split/upload/3J_docs_occ_nTemp/Leg3_4-split/Step8_docs/3rdJ_08P_gates.sh'
```

**New file added to the Step8_docs tree**: `3rdJ_08P_archive_retailfix.sh` (disk-guard + rename job,
`#SBATCH -t 7-00:00:00`, `-p ps`, `--mem=4G`). No existing script modified.

**No polling performed.** Job 2 (~38 min/cell x 4 in parallel) and Job 3 chain by SLURM dependency;
the manager reads the scorecard once Job 3 lands.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

### 2026-07-28 — LOCAL PORT: probe harness runs on Windows, additive, cluster path unchanged

**Task**: prepare (not consume) a local Windows execution path for the §P probe harness, ahead of
moving the remaining ~64 annual runs off Speed. LOCAL ONLY, no cluster commands. No annual run
executed in this task (forbidden by the handoff) -- validated with short design-day / 2-day
weather-file test runs instead.

**Files modified (additive, cluster path preserved)**:

- `3rdJ_08P_probe_driver.py` -- added `--engine {auto,cluster,local}` (default `auto`:
  `sys.platform=="win32"` -> `local`, else `cluster`), `--outroot`, `--repo-root`. Cluster branch
  reproduces the pre-port constants byte-for-byte (`STEP7_OUT`/`IDF_SUPERTALL`/`EPW`/
  `INJECTOR_PY`/`PROBES_ROOT`, Singularity wrapper text and `subprocess.run` call unchanged) --
  verified by reading the `engine == "cluster"` branch at each fork point, not assumed.
  - `CELLS` (previously a literal list built from the hardcoded `STEP7_OUT`, old L88-122) is now
    built by `_build_cells(step7_out)`; module-level `CELLS = _build_cells(STEP7_OUT)` keeps the
    exact old value for any external importer. `main()` calls `_build_cells(step7_out)` with
    whichever `step7_out` the resolved engine points at.
  - Added `LOCAL_*` path constants (`LOCAL_REPO_ROOT` derived from the script's own location,
    `LOCAL_PROBES_ROOT`, `LOCAL_IDF_SUPERTALL`, `LOCAL_EPW`, `LOCAL_STEP7_OUT`,
    `LOCAL_INJECTOR_PY`) resolved against the local checkout, not hardcoded to this machine.
  - Simulate step: on `engine=="local"`, calls `eSim_bem_utils.config.ENERGYPLUS_EXE` directly
    (no Singularity wrapper script written); on `engine=="cluster"`, the original
    `#!/bin/bash` + `singularity exec --bind /speed-scratch --bind /nfs/speed-scratch {SIF}
    {SIF_EXE}` wrapper is written and invoked exactly as before.
  - `EPLUS_IDD`: cluster keeps the original hard-require-env-var check unchanged. Local adds a
    fallback to `eSim_bem_utils.config.resolve_idd_path()` (already IDD-24.2-version-gated) when
    the env var is absent. **Bug found and fixed while validating this**: `resolve_idd_path()`
    only returns a local variable; `commercial_integration.py::_find_idd()` (no explicit-IDD
    parameter on `inject_mixed_use`) reads the `EPLUS_IDD` **env var**, so the resolved path must
    also be `os.environ["EPLUS_IDD"] = eplus_idd` after resolution -- added; no-op on cluster
    where the sbatch script already exports it.
  - Added `_energyplus_provenance(engine)`: writes `PLATFORM` (`sys.platform`), `engine`,
    `energyplus_version`, `energyplus_build`, `energyplus_exe_used` into every manifest (both the
    normal path and `--postprocess-only`). Cluster derives version/build from the `SIF_EXE`
    constant string via regex (zero new subprocess calls, zero behavioural change); local
    actually invokes `energyplus.exe --version` (cheap, confirmed sub-second) so the recorded
    build is verified against what really ran, not assumed.
- `3rdJ_08P_probe_gates.py` -- added a **new** PLATFORM gate (fails if cells being compared in a
  `campaign_*` dir don't share `PLATFORM`; WARNs if a manifest predates this field). This is not a
  relaxation of any existing gate. Also added the same `--engine/--outroot/--repo-root` pattern
  (via `global PROBES_ROOT, LOGS_DIR, INJECTOR_PY` reassignment in `main()`) so the script is
  actually runnable off-cluster, not just carrying dead code for a gate that could never fire
  locally.
- `3rdJ_08P_probes_local.py` (**new file**) -- Windows orchestrator replacing what
  `3rdJ_08P_probes.sh` / `3rdJ_08P_postprocess.sh` do on the cluster (`3rdJ_08P_gates.sh` needs no
  replacement -- it's a single non-parallel invocation, `py -3 3rdJ_08P_probe_gates.py --engine
  local` covers it directly). Memory watchdog **ported (pattern) from**
  `2J_docs_occ_nTemp/Step8_docs/run_campaign_local.py:13,51-75,144` (`_MEMORYSTATUSEX`,
  `_committed_pct()`, `_kill_active()`, watchdog polling loop -- same implementation, adapted to
  per-cell subprocess bookkeeping): `--mem-abort` default 80%, kills all active cell subprocesses
  (`taskkill /F /T`) on breach. `--workers` default **6** (not cores-2 -- user works on the
  machine during runs, per handoff). Resume: a cell outdir is skipped only if its manifest
  records success (`ep_return_code==0` or `postprocess_only==True`), no `*_exception` key, and
  both CSVs have manifest-recorded `rows==8760`. **No silent overwrite**: an existing outdir that
  is not complete is renamed aside to `<outdir>_STALE_<timestamp>` before the cell (re)runs --
  never overwritten in place (this is exactly "Défaut 3 -- trou d'empreinte" from the reference
  doc, closed at the orchestrator level; the single-cell driver's own `INPUTS_HASH` fix stays
  OUT of scope, as the reference doc marks it). `--postprocess-only` mirrors
  `3rdJ_08P_postprocess.sh`'s recovery array and deliberately bypasses resume/archive (archiving
  would delete the `eplusout.sql` that mode exists to recover from). Dep precheck
  (`import eppy, pandas, numpy`) mirrors the `.sh` scripts' fail-fast check.

**Non-regression, by reading (not just compiling)**: traced every fork point in
`3rdJ_08P_probe_driver.py` main() for `engine == "cluster"` and confirmed each resolves to the
exact pre-port value/behaviour (`SIF`/`SIF_EXE` untouched, wrapper text untouched, `EPLUS_IDD`
strict-require untouched, `STEP7_OUT`/`IDF_SUPERTALL`/`EPW`/`INJECTOR_PY`/`PROBES_ROOT` untouched
unless `--outroot`/`--repo-root` explicitly passed, which no existing cluster caller does).
**Not run on Linux in this task** (no cluster access here) -- this is a by-reading verification,
flagged as such per instructions.

**Watchdog**: ceiling 80% committed-memory (Windows `GlobalMemoryStatusEx` commit charge, same
metric `run_campaign_local.py` uses), polled every 3 s, hard-kills every tracked cell subprocess
tree on breach. Source: `2J_docs_occ_nTemp/Step8_docs/run_campaign_local.py:60-98` pattern,
reimplemented in `3rdJ_08P_probes_local.py` (same struct/functions, different process
bookkeeping unit: per-cell, not per-archetype-city).

**PLATFORM gate**: lives in `3rdJ_08P_probe_gates.py`, runs before P1/P2, reads the
`PLATFORM`/`energyplus_version`/`energyplus_build` fields the driver now writes into every
manifest. Empirically demonstrated both ways (per the reference doc's "gate must be proven to
trip on the defect it claims to catch" standard): with a fabricated `PLATFORM: "linux"` manifest
alongside a real local `win32` one, the gate correctly `FAIL`ed with the exact mismatch dict; with
both manifests `win32`, it `PASS`ed.

**Startup test (short, no annual run)** -- both IDFs were present locally
(`3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/`,
confirmed on disk before starting), so the full chain was exercised:

1. **Design-day only** (`-D` flag), cell 0 (`baseline_necb`, all-fallback/NECB baseline):
   inject -> ensure-outputs -> `energyplus.exe` direct call -> `eplusout.sql`. EnergyPlus
   `Version 24.2.0-94a887817b` (exact cluster build match), return code 0, **56.1 s** EnergyPlus
   run time (**73.1 s** total incl. injection). `hourly_meters.csv`/`channel_hourly.csv` came back
   0 rows -- expected, not a bug: `-D` produces only `EnvironmentType` sizing-period rows, and the
   extraction query filters `EnvironmentType = 3` (weather-file run periods) by design.
2. **2-day weather-file RunPeriod** (real `EnvironmentType=3` environment, not `-D`), cell 1
   (`B_central`, real office+retail+hotel injection: 6/3/3 PEOPLE objects wired): same chain,
   EnergyPlus return code 0, **76.7 s** EnergyPlus run time (**92.7 s** total). `hourly_meters.csv`
   = 48 rows, `channel_hourly.csv` = 48 rows, all 15 channel/metric columns non-zero (office/
   retail/hotel/residential/service_MEP x people/lights/equip); `channel_hourly` mapping
   27,648/27,648 report rows mapped (0 unmapped, consistent with AUDIT-W's 4-plenum-exception
   census).
3. **Real driver entry point** (not the scratch harness): copied that 2-day `injected.idf` +
   `eplusout.sql` into the expected `probes_local/campaign_5670f602/B_central/` layout and ran
   `py -3 3rdJ_08P_probe_driver.py --cell 1 --engine local --postprocess-only` for real. Wrote a
   correct `manifest.json` (`PLATFORM=win32`, `engine=local`, `energyplus_version=24.2.0`,
   `energyplus_build=94a887817b`, `energyplus_exe_used=C:\EnergyPlusV24-2-0\energyplus.exe`),
   correctly exited 1 on the (expected, honest) `rows=48 != 8760` gate -- confirming the row-count
   gate itself is not weakened for the local path.
4. All scratch outputs (`probes_local/`, scratchpad smoke dirs) deleted after validation; nothing
   left in the repo tree from this test.

**INJ_HASH cross-check**: the local injector's md5[:8] resolved to `5670f602` -- **identical** to
the cluster campaign dir name in the existing runbook entries above, confirming the local
`eSim_bem_utils/commercial_integration.py` checkout is byte-identical to what's on Speed (per the
§6b md5 inventory already on file).

**Time observed (first local measurements, supersedes the 25-50 min/run cluster-based estimate
for planning purposes, but is NOT a full-annual data point)**: 2-day weather-file run with real
3-channel injection = 92.7 s total, of which ~55-75 s is warmup/zone-sizing overhead that does not
scale with RunPeriod length. This means the local full-annual-run wall time **cannot be linearly
extrapolated** from this number (warmup dominates a 2-day run, not an 8760h one) -- an actual
annual local run (out of scope for this task) is still needed for a real per-run estimate.

**What is NOT done yet (before the 64 local runs can launch)**:
- No local campaign driver exists for the full 2-building x 2-city x 14-scenario matrix -- only
  the 7-cell §P probe table is wired. That matrix driver is separate future work.
- Défaut 3 (`INPUTS_HASH` stale-Step-7-product guard) remains OPEN in the single-cell driver
  itself, exactly as the reference doc leaves it -- `3rdJ_08P_probes_local.py` only closes the
  no-silent-overwrite gap at the orchestrator level, for outdirs it manages.
- A. Injector résidentiel (OD-8R-L3), B. produits manquants (8A), and the campaign-launch blockers
  A/B/C in the reference doc are unchanged by this port -- it only makes the *existing* probe
  harness runnable locally.
- No full annual local run has been timed. No CAN_CLG / Calgary IDF was exercised (only CAN_MTL,
  matching the probe table's MTL-only scope).

**What was NOT verified**: the cluster (`engine=="cluster"`) branch was not executed in this
task -- verified by reading only, no Speed access available here. The `--postprocess-only` mode of
`3rdJ_08P_probes_local.py` was dry-run-tested (plan resolution) but not executed against a real
missing-sql cell to confirm the driver's own per-cell error message surfaces correctly through the
orchestrator's log-per-cell mechanism (the driver's own `--postprocess-only` error path was,
however, exercised directly and confirmed correct at commit-level testing above).

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

---

## Progress Log — 2026-07-28 (mesure diagnostique : bruit de plateforme cluster vs local, cellule 1 `B_central`)

**Tâche** : quantifier l'écart Linux (cluster, job `1169800` tâche 1) vs Windows (local, 15,9 min) sur
la cellule 1 `B_central`, même build EnergyPlus 24.2.0 `94a887817b`, mêmes fichiers d'entrée — pour
juger si mélanger les plateformes dans la campagne 56 runs est interprétable.

**1. `sacct`** — `1169800_1/2/3/4` : `COMPLETED`, `ExitCode 0:0`, ~37,5-38,0 min chacun. `1169804`
(scorecard) : `COMPLETED`, `0:0`, 4 s. Rien à signaler côté cluster.

**2. Vérification préalable des entrées (manifest vs manifest)** — **entrées identiques confirmées**
avant toute interprétation :
- `INJ_HASH` : `5670f602` des deux côtés.
- md5 des 3 CSV Step-7 lus par la cellule, identiques cluster/local : office `9507fbd6b7…`, retail
  `cf8721c620…`, hotel `4b3d3a4603…`.
- `inject_mixed_use_result` (n_spaces/n_lights/n_equip par canal) identique des deux côtés.
- `driver_md5` diffère (`ed36feb8…` cluster vs `3f42ce85…` local) — **attendu et sans incidence** :
  c'est le portage additif `--engine local` documenté en §C-bis de `3rdJ_08_implementation_improvements.md`,
  pas une différence d'entrée physique.
- `injected_idf_md5` diffère (`11c413e3…` vs `a4de0c36…`) — attendu, chemins absolus spécifiques à la
  plateforme embarqués dans l'IDF (répertoire de run), pas le contenu physique.
- Manifeste local porte bien `PLATFORM=win32`, `engine=local`, `energyplus_version=24.2.0`,
  `energyplus_build=94a887817b`, `energyplus_exe_used=C:\EnergyPlusV24-2-0\energyplus.exe` — manifeste
  cluster n'a pas ces champs (version antérieure au portage, cohérent avec la chronologie).

**3. Comparaison colonne-par-colonne** (`py -3` + pandas, script et CSV bruts dans le scratchpad, PAS
dans le repo). 8 760 lignes, mêmes colonnes des deux côtés pour les deux fichiers ; alignement
positionnel (aucune colonne clé temporelle explicite dans l'un ou l'autre CSV — les deux sont des
séries horaires annuelles générées par le même driver, ordre garanti identique, confirmé par les Δ=0
exacts obtenus ci-dessous, qui seraient impossibles sous un décalage de lignes).

- **`channel_hourly.csv` (le fichier que lisent les gates §P — colonnes `*_people`)** :
  **max|Δ| = 0,0 EXACTEMENT, 0 ligne différente, sur les 5 colonnes `*_people`**
  (office/retail/hotel/residential/service_MEP). Les colonnes `*_lights` ont un bruit
  flottant **~1,49e-8 absolu (~1e-13 relatif)**, 15-126 lignes affectées selon canal — négligeable,
  et de toute façon hors métrique de gate. Les colonnes `*_equip` sont aussi à Δ=0 exact.
  Byte-identique : **non** (md5 diffèrent) — mais taille cluster 2 111 094 o vs local 2 119 863 o,
  écart ≈ 8 769 o ≈ 1 octet/ligne × 8 761 lignes (en-tête compris) → **fins de ligne CRLF (Windows)
  vs LF (Linux)**, pas un écart numérique. Confirmé par les Δ=0 exacts ci-dessus.
- **`hourly_meters.csv` (meters bâtiment, énergie)** : plus de bruit, comme attendu (HVAC/contrôle
  plus sensible à l'ordre d'arrondi que des schedules `People`). Pire cas horaire : `Pumps:Electricity`
  max|Δ|=1,04e8, ≈43 % de la moyenne horaire (bascule d'état d'équipement sur une heure-frontière isolée,
  8301/8760 lignes montrent un Δ non nul). Mais **totaux annuels** (la métrique EUI) : tous les écarts
  relatifs annuels sont **≤ 0,0081 %** (Heating:Electricity 0,0081 % ; Pumps 0,0062 % ; WaterSystems
  0,0025 % ; Cooling 0,00045 % ; Electricity:Facility 0,00029 % ; Fans 0,00059 %). `Gas:Facility`,
  `Heating:Gas`, `InteriorEquipment:Gas`, `WaterSystems:Gas` = 0 des deux côtés (bâtiment 100 %
  électrique, cohérent avec 2J Bug B). Byte-identique : non, md5 diffèrent (même explication CRLF/LF +
  bruit flottant réel sur les colonnes HVAC).

**4. Mise en perspective — verdict** : la métrique que les gates §P consomment réellement
(`channel_hourly.csv`, colonnes `*_people`) a un **écart de plateforme = 0,0 exactement**, donc un
**rapport 0 / 1,95 = 0** face au signal le plus ténu (P1 hôtel cellule 4 vs 1, Δpeople = 1,95). Ce
n'est pas seulement « petit devant » — il n'y a **aucun** bruit de plateforme mesurable sur cette
colonne, sur les 8 760 heures de l'année. Les colonnes énergie (`hourly_meters.csv`) portent un bruit
de plateforme réel mais **≤ 0,0081 % sur les totaux annuels**, sans commune mesure avec un delta de
scénario en pourcentage d'EUI (les scénarios §7 visent des écarts de l'ordre du pourcent, pas du
centième de pourcent).

**5. Recommandation** : le mélange de plateformes est **négligeable pour les métriques Δpeople des
gates §P actuelles**. **Ne pas assouplir/retirer la gate `PLATFORM`** pour autant — elle reste une
garde structurelle correcte en prévision de canaux/mesures futurs plus sensibles à l'arrondi (HVAC,
EUI fin), et cette mesure ne couvre qu'**une seule cellule, un seul run par côté** (pas de réplicats,
pas d'autre cellule testée). **Une campagne, une plateforme reste la règle** ; ce diagnostic dit
seulement que si un mélange accidentel s'était produit sur la métrique people, il n'aurait pas
contaminé le signal détecté à ce jour — ce n'est pas un feu vert pour mélanger délibérément.

**6. Non vérifié** : une seule cellule (`B_central`) testée, sans réplicat sur d'autres cellules
(office/retail/hotel variées) ni sur les meters d'un bâtiment moins électrifié. Pas de test sur
Calgary (CAN_CLG). Le mécanisme exact des bascules horaires HVAC (43 % ponctuel sur Pumps) n'a pas
été investigué plus loin que le constat — sans incidence sur le verdict people, mais non expliqué en
détail. Artefacts bruts (CSV cluster + script pandas) laissés dans le scratchpad local, pas dans le
repo, conformément à la consigne.

## Progress Log — 2026-07-28 (employé) : Défaut 3 fermé — `INPUTS_HASH` (trou d'empreinte)

**Tâche** : `3rdJ_08_implementation_improvements.md` §Défaut 3 (trou d'empreinte, OUVERT). L'empreinte
de sortie des probes (`campaign_<md5(commercial_integration.py)[:8]>/<tag>/`) ne couvrait que
l'injecteur, pas les produits Step-7 dont le contenu détermine entièrement les horaires injectés —
un re-simulation post-correctif produit aurait pu écraser en place sans garde-fou, avec l'injecteur
inchangé. LOCAL uniquement, aucun EnergyPlus lancé pendant cette tâche.

### Ce qui a été changé

- **`3rdJ_08P_probe_driver.py`** :
  - `_compute_inputs_hash(channels)` (nouveau) — md5 sur les CSV Step-7 réellement lus par la
    cellule : pour chaque canal en ordre **alphabétique** (pas l'ordre d'insertion de `_build_cells`),
    ligne `"<canal>|<chemin-csv-tel-que-configuré>|<md5-ou-MISSING>"`, jointes par `\n`, md5'd.
    Retourne `(hash[:8], detail)` où `detail` = liste de `{channel, csv_path, csv_md5}` (écrite dans
    le manifeste comme `INPUTS_HASH_DETAIL`).
  - `_check_inputs_hash_guard()` (nouveau) — appelée **avant** `os.makedirs(outdir)` (donc avant les
    4 sites d'écrasement recensés dans le doc : makedirs, `idf.saveas()`, EnergyPlus `-d run_dir`,
    `_write_manifest()`), identiquement pour `engine=="cluster"` et `engine=="local"` (insérée en
    amont du branchement spécifique-moteur, wrapper Singularity **non touché**, verbatim). Compare
    `INPUTS_HASH` courant à celui du `manifest.json` déjà présent dans `outdir` (s'il existe) :
    - identique → no-op silencieux (cas normal).
    - manifeste absent d'`INPUTS_HASH` (legacy, antérieur à ce correctif) → traité comme **INCONNU**,
      pas comme sûr — refuse par défaut (décision documentée : un manifeste vieux peut porter une
      simulation valide de 16-38 min, « rien d'enregistré » n'est pas une preuve de concordance).
    - mismatch réel → refuse, nomme les deux hash + le(s) canal/canaux produit qui diffère(nt)
      (`_diff_inputs()`, comparaison par canal des `csv_md5` enregistrés).
    - Override explicite `--allow-stale-inputs`, avec deux sémantiques **différentes** selon le mode
      (jamais la même remédiation) :
      - chemin simulation normale → **archive** l'outdir périmé (`_archive_stale_dir()`, suffixe
        `_STALE_<timestamp>`, jamais supprimé — **réutilise** la convention déjà en place dans
        `3rdJ_08P_probes_local.py::_archive_stale`, pas une deuxième convention) puis procède à une
        vraie re-simulation dans un outdir neuf.
      - `--postprocess-only` → **n'archive jamais** (l'archivage détruirait l'`eplusout.sql` que ce
        mode existe pour réutiliser). L'override n'est honoré que pour un manifeste **legacy** (adopte
        l'`INPUTS_HASH` courant en place, sans y toucher d'autre). Un mismatch **réel** (manifeste
        avec un `INPUTS_HASH` qui diverge) est refusé **inconditionnellement**, même avec l'override :
        `--postprocess-only` ne re-simule jamais, il ne peut donc jamais légitimement corriger un vrai
        changement de produit.
  - `INPUTS_HASH` + `INPUTS_HASH_DETAIL` écrits dans le manifeste sur **les deux** chemins
    (`--postprocess-only` et simulation normale).
  - Nouveau flag `--allow-stale-inputs` (CLI), documenté ci-dessus.
- **`3rdJ_08P_probes_local.py`** :
  - `_cell_complete()` prend un `expected_inputs_hash` optionnel ; un outdir par ailleurs complet
    (rc=0, 8760 lignes) mais dont l'`INPUTS_HASH` du manifeste diverge de celui attendu pour les
    produits **courants** est traité comme **non complet** — route vers l'appel `_archive_stale()`
    déjà existant (même convention `_STALE_<timestamp>`) au lieu d'un faux resume-skip.
  - `_load_driver_module()` (nouveau) charge `3rdJ_08P_probe_driver.py` via `importlib` (nom de
    fichier commençant par un chiffre, pas `import`able normalement) pour réutiliser
    `_build_cells()`/`_compute_inputs_hash()` **du driver lui-même** — même recette, pas une
    réimplémentation.
  - Passthrough `--allow-stale-inputs` ajouté (rarement nécessaire via cet orchestrateur, le
    pré-check archive déjà les outdirs périmés avant d'invoquer le driver ; gardé pour
    `--postprocess-only`, qui contourne le pré-check, et pour l'invocation directe du driver).
- **`3rdJ_08P_probe_gates.py`** : gate compagnon **INPUTS_HASH cross-cell consistency** (nouvelle,
  placée avant P1, même raisonnement que la gate `PLATFORM`) — pour chaque comparaison P1
  (cellule variée vs cellule 1), vérifie que les canaux **non variés** ont le même `csv_md5`
  enregistré (`channels_requested[...].csv_md5`) dans les deux manifestes comparés ; FAIL sinon
  (« comparaison contaminée »). Lecture seule sur les manifestes déjà au sol, ne relance pas le
  garde-fou d'écriture du driver.
  Aucun seuil de gate existant assoupli ou retiré.

### Démonstration empirique (règle §Test method n°2 — un garde-fou qui ne se déclenche pas est pire
qu'aucun garde-fou)

**Groupe A — sur le vrai répertoire `probes_local/campaign_5670f602/B_central/` (réel, legacy,
manifeste sans `INPUTS_HASH`), via `--postprocess-only` uniquement (jamais d'écriture sur
`run/eplusout.sql`, jamais d'EnergyPlus) :**

1. **Refus par défaut** (manifeste legacy = INCONNU) :
   ```
   [FAIL] STALE-INPUTS GUARD (probes_local\campaign_5670f602\B_central):
          existing manifest predates INPUTS_HASH (legacy/pre-Defaut-3-fix run) -- treated as UNKNOWN, not as safe-to-reuse
          differing product file(s): unknown -- existing manifest has no INPUTS_HASH_DETAIL (legacy/pre-Defaut-3-fix run)
          Refusing to write.
   EXIT=1
   ```
   md5 du `manifest.json` vérifié identique avant/après (aucune écriture) : `19ec5c34a3a5ef49d0836f8831c1538e` des deux côtés.
2. **Override → adoption en place** (`--allow-stale-inputs --postprocess-only`) : message d'adoption
   imprimé, `INPUTS_HASH=fdc5c095` calculé et écrit, CSV re-dérivées depuis le `eplusout.sql`
   existant (8760/8760 lignes), `EXIT=0`.
3. **Régime stable** (re-run sans override, produits inchangés) : **aucun** message `STALE-INPUTS
   GUARD`, `INPUTS_HASH=fdc5c095` retrouvé identique, `EXIT=0` — confirme `--postprocess-only`
   toujours opérationnel pour une cellule dont les produits n'ont pas changé.

**Groupe B — répertoire scratch isolé, dépôt fictif (`--repo-root`) avec copies réelles des 3 CSV
Step-7 de la cellule 1 (jamais les fichiers réels touchés — vérifié par md5 avant/après) :**

4. **Falsification + refus** (copie de `retail_presence_multiplier_2030_central.csv` altérée, une
   valeur `multiplier` changée) :
   ```
   [FAIL] STALE-INPUTS GUARD (...\fake_probes_out\campaign_81f9dd5f\B_central):
          existing INPUTS_HASH=14165e3a != current INPUTS_HASH=a72336ad
          differing product file(s): retail: cf8721c62030fc7c1f23b999f85056d0 -> f2e15de2b9d94cef2f2dc1af1e56b676
          Refusing to write. Pass --allow-stale-inputs to archive the existing outdir aside (never overwritten in place, never deleted) and proceed with a real re-simulation against the current products -- only for a deliberate re-simulation after a known product fix.
   EXIT=1
   ```
   Seul le canal `retail` (le fichier tamponné) est nommé — office et hotel, inchangés, ne
   déclenchent rien. md5 réel du produit `retail_presence_multiplier_2030_central.csv` sur disque
   vérifié inchangé (`cf8721c6…`) avant et après.
5. **Restauration → passe silencieusement** : copie retail restaurée octet-pour-octet
   (`cf8721c62030fc7c1f23b999f85056d0`), re-run identique → **aucun** message `STALE-INPUTS GUARD`,
   `INPUTS_HASH=14165e3a` retrouvé identique à la ligne de base, poursuit jusqu'à l'échec **attendu
   et sans rapport** (IDF absent du dépôt fictif minimal, `[FAIL] inject_mixed_use raised: ... No
   such file or directory ...SuperTallBuilding...idf`) — jamais atteint EnergyPlus.
6. **Override + archive** (re-tamponnage, `--allow-stale-inputs`, mode simulation normale) :
   `[archive] stale-inputs outdir archived -> ...\B_central_STALE_20260728_202355 (never overwritten
   in place)`, nouvel outdir créé, ancien conservé intact.
7. **Mismatch réel sous `--postprocess-only` + override → refusé quand même** (produits restaurés,
   manifeste de l'étape 6 porte encore le hash du produit tamponné) :
   ```
   --allow-stale-inputs is NOT honored here: a genuine INPUTS_HASH mismatch under --postprocess-only
   means the existing eplusout.sql was built from DIFFERENT products than today's -- postprocess-only
   never re-simulates, so it cannot legitimately fix that. Run a real simulation instead.
   Refusing to write.
   EXIT=1
   ```

### État final vérifié

- Répertoire réel `probes_local/campaign_5670f602/B_central/` : sain, `ep_return_code=0`,
  `INPUTS_HASH=fdc5c095`, 8760/8760 lignes sur les deux CSV, aucune clé `*_exception`.
- `py -3 -m py_compile` propre sur les 3 fichiers modifiés (`3rdJ_08P_probe_driver.py`,
  `3rdJ_08P_probes_local.py`, `3rdJ_08P_probe_gates.py`).
- `3rdJ_08P_probe_gates.py --engine local` relancé sur les données réelles (1 seule cellule présente
  localement) : ne plante pas, nouvelle gate `INPUTS_HASH` silencieuse à raison (comparaisons P1
  nécessitent 2 cellules, une seule au sol) ; `PLATFORM` toujours PASS. Résultat global inchangé,
  aucun seuil touché.
- Aucun produit Step-7 réel modifié (vérifications md5 avant/après à chaque étape ci-dessus).
- Aucun EnergyPlus lancé (contrainte de la tâche) — les runs Groupe B échouent volontairement plus
  loin dans la chaîne (IDF absent du dépôt fictif minimal), un point **après** le garde-fou, jamais
  atteint le sous-processus EnergyPlus.

### Non vérifié / hors scope de cette tâche

- La gate compagnon `INPUTS_HASH` de `3rdJ_08P_probe_gates.py` n'a pas pu être testée en FAIL réel
  (aucun jeu à 2+ cellules avec produits divergents disponible localement sans lancer EnergyPlus) —
  seule sa lecture de code + le no-op gracieux sur données insuffisantes ont été vérifiés.
  Recommandation : la vérifier au premier scorecard §P réel qui suit une campagne locale multi-cellule.
- Migration effective des **autres** répertoires legacy (cellules 0, 2-6, cluster) vers
  `INPUTS_HASH` : non faite ici (seule `B_central` locale existait) — chacun refusera par défaut au
  premier `--postprocess-only`/simulation jusqu'à un `--allow-stale-inputs` explicite ou une
  re-simulation complète. À anticiper avant la campagne 56 runs.
- Le comportement précis en cas de course concurrente (deux invocations simultanées sur le même
  outdir) n'a pas été testé — hors scope, le harnais reste mono-opérateur/mono-machine.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

---

## Progress Log — 2026-07-28 (§B : injecteur résidentiel OD-8R-L3, implémenté + audit de câblage IDF)

**Tâche** : fermer §B de `3rdJ_08_implementation_improvements.md` — `inject_mixed_use()` n'injectait
que office/retail/hotel ; les 27 Spaces résidentielles (Tag-2 exact `HighriseApartment Apartment`,
tour Tall) ne recevaient rien (`P1 residential` = INFO/NOT EXERCISED). AUCUN EnergyPlus exécuté
(interdit par la tâche) ; câblage prouvé au niveau IDF, objet par objet, jamais déduit de l'énergie.

### 1. Fait empirique préalable — structure Space/Zone/carrier de la tour (avant tout code)

Sondé directement sur `TallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v242.idf` (copie de travail,
jamais la source touchée) avec eppy :

- **164 SPACE = 164 ZONE, correspondance 1:1** (aucune Zone n'héberge plus d'une Space).
- **27 Spaces** ont `Tag_2 == "HighriseApartment Apartment"` exactement (les 3 Spaces restantes du
  total AUDIT-W de 30 sont 2 `HighriseApartment Corridor` + 1 `HighriseApartment Office` — aires
  communes, hors périmètre de cette tâche, voir §4).
- **Le défaut réel n'est PAS « une Space couvre plusieurs Zones »** (elles sont 1:1) mais l'inverse
  et néanmoins la même famille de bug (« 2J Bug A » = un seul carrier pour N zones physiques) : **UN
  SEUL objet `PEOPLE`** (`HighriseApartment Apartment People`) référence les 27 Spaces **via une
  `SpaceList` nommée `HighriseApartment Apartment`**, méthode `People/Area` (densité), pas de
  comptage absolu. Un ménage distinct par Space est structurellement impossible sans intervention :
  un seul objet ne peut porter qu'un seul `Number_of_People_Schedule_Name`.
- Même schéma pour `LIGHTS` (2 objets SpaceList-level : `...Additional Lights`, `...Lights`) et
  `ELECTRICEQUIPMENT` (1 objet). **Non touchés** — hors périmètre OD-7D (voir §4).
- Script de sonde : `scratchpad/probe_residential_structure2.py` (non versionné, conforme consigne
  scratchpad).

### 2. Filtre condo/appartement — valeurs lues dans la donnée, pas devinées

`BEM_Schedules_4split_2022.csv`, 23 115 SIM_HH_ID uniques :

| DTYPE | n | | CONDO | n |
|---|---|---|---|---|
| SingleD | 12 939 | | 0 | 19 909 |
| MidRise | 4 836 | | 1 | 3 206 |
| OtherDwelling | 3 001 | | | |
| HighRise | 2 339 | | | |

Crosstab DTYPE×CONDO : `CONDO=1` existe sous **chaque** DTYPE (y compris SingleD, 157 lignes) — CONDO
est un attribut de **tenure** (propriété en copropriété), pas de forme du bâtiment ; il ne peut donc
pas identifier seul un immeuble d'appartements. Provenance DTYPE
(`3rdJ_07_aug_to_bem_4split.py::dtype_label`) : code recensement 2 = « immeuble d'appartements »,
splitté HighRise/MidRise par BEDRM (≤1 chambre vs plus) ; code 1 = SingleD ; code 3 = OtherDwelling
(maison en rangée/duplex/mobile — PAS un appartement).

**Filtre retenu : `DTYPE in {"HighRise", "MidRise"}`** (constante `RESIDENTIAL_DTYPE_APARTMENT`,
`eSim_bem_utils/commercial_integration.py:79-122`, docstring inline avec ces mêmes chiffres). Les
deux valeurs sont les deux sous-ensembles (par BEDRM) de la **même** catégorie recensement
« appartement » — capture tous les ménages en appartement (locataires ET copropriétaires),
exclut maisons individuelles et rangées/duplex. `CONDO` délibérément **non** utilisé en filtre
additionnel : en ET, exclurait la majorité des locataires en appartement (aucune raison) ; en OU,
admettrait des condos non-appartement (maisons en rangée) dans le pool d'une tour. Appariement du
nombre de chambres au mix du prototype : **non adopté** (verrouillé, nouvelle OD sinon), BEDRM ne
joue aucun rôle au-delà d'avoir déjà produit l'étiquette HighRise/MidRise. Pool résultant : 7 175
ménages (2022) / 7 175 (2030_central, distribution identique, vérifié) — très supérieur aux 27
Spaces, large marge pour un tirage sans remise.

### 3. Fichiers/fonctions touchés — additif strict

Tout dans `eSim_bem_utils/commercial_integration.py` (455 → 736 lignes) :

- **Docstring module** (L1-50) : section résidentielle mise à jour (pointait vers un module
  `eSim_bem_utils_3J/integration.py` inexistant dans le repo live — corrigé pour pointer vers ce
  module). Table Tag-2 routing (L24-45) : ligne `HighriseApartment Apartment` mise à jour pour
  refléter l'implémentation réelle ; ligne corridor/office annotée « hors périmètre ».
- **`RESIDENTIAL_DTYPE_APARTMENT`** (constante, L79-122) : nouvelle, filtre + justification + les
  comptages ci-dessus, inline.
- **`_build_compact_fields_2dt`** (L182-198) : **modifiée** — ajout d'un paramètre optionnel
  `type_limit: str = "Fraction"` (positionnel avant, donc **tout appelant existant est byte-
  identique** ; seul site d'appel préexistant, `modulate_baseline`, ne le passe jamais). Nécessaire
  car `Metabolic_Rate` est en `Any Number` (W/personne), pas une fraction 0-1.
- **`load_residential_pool()`** (nouvelle, L350-386) : charge `BEM_Schedules_4split_*.csv`, filtre
  DTYPE, retourne un ménage par `SIM_HH_ID` (hhsize/dtype/condo + 24×WD/WE Occupancy_Schedule +
  Metabolic_Rate). Réimplémentation pandas du même contrat de colonnes que
  `eSim_bem_utils/integration.py::load_schedules()` (`SIM_HH_ID`/`Occupancy_Schedule` :379,
  `Metabolic_Rate` :380) — **pas un import** du module `integration.py` complet, pour ne pas exposer
  les canaux office/retail/hotel byte-identiques à un futur échec d'import dans la chaîne
  idf_optimizer/schedule_generator/schedule_visualizer/config que ce module n'a jamais eue.
- **`draw_residential_households()`** (nouvelle, L387-406) : tirage déterministe sans remise,
  `np.random.default_rng(seed).choice(..., replace=False)` sur les `SIM_HH_ID` triés numériquement
  (l'ordre d'un dict Python n'est jamais la clé de tri).
- **`inject_residential()`** (nouvelle, L408-528) : (1) neutralise l'objet `PEOPLE` SpaceList-level
  existant (`Number_of_People=0`, méthode passée à `"People"`, objet **conservé** dans l'IDF, pas
  supprimé — auditable) ; (2) pour chacune des 27 Spaces, crée 2 `Schedule:Compact` (Occ + Met,
  nommés `MXU_Residential_{Occ,Met}_HH<id>`) et **1 nouvel objet `PEOPLE` par Space**, référencé
  directement par nom de Space (champ unifié v24.2), `Number_of_People = HHSIZE` du ménage tiré.
  Lights/Equipment résidentiels **non touchés** (OD-7D, aucune colonne équipement/éclairage dans le
  produit Step-7).
- **`inject_mixed_use()`** (L531+) : ajout d'une branche résidentielle **strictement conditionnelle**
  à `"residential" in channels` — si absente, aucune ligne de code résidentielle ne s'exécute (pas
  d'entrée `fallback`, pas de ligne de provenance, pas de ligne stdout supplémentaire) : la garantie
  « byte-identique » porte sur ce cas précis, prouvé en §5 ci-dessous, pas seulement affirmée.

### 4. Portée volontairement exclue (documentée, pas oubliée)

Corridor + Office résidentiels (3 Spaces sur les 30 dénombrées par AUDIT-W) : aucune donnée ménage
ne s'applique à une aire commune ; la spec du module (docstring L24-45, avant mon édit) prévoyait un
mécanisme séparé « multiplicateur Lights » pour ces 3 Spaces — **non implémenté ici**, aucun produit
Step-7 ne fournit cette donnée. `P1 residential` devient exerçable pour les 27 Spaces-logement ; les
3 Spaces communes restent untouched comme avant.

### 5. Preuve « additif strict » — régression office/retail/hotel

Reconstruction du fichier pré-édit (455 lignes, contenu exact du premier `Read` de cette session) en
scratchpad, exécution EN PARALLÈLE de l'ancien et du nouveau module sur deux copies fraîches de
`TallBuilding_..._v242.idf`, mêmes `channels` (office/retail/hotel, **sans** clé `"residential"`),
`building_meta={"scenario_label": "B_central"}` :

| Vérification | Résultat |
|---|---|
| `result` dict (nouveau moins clé `"residential"`) == `result` dict ancien | **True** |
| IDF de sortie, md5 | **identiques** (`d9e1271dc977c9e189d835c584f0dafc` des deux côtés) |
| Fichier `.provenance.txt` | **byte-identique** |
| stdout | identique à l'exception du nom de fichier de sortie (attendu, chemins différents) |

Script : `scratchpad/regression_test_office_retail_hotel.py`. Le nouveau `result` a bien une clé
`"residential"` supplémentaire (additif), toujours `{"n_spaces": 0, ...}` quand non demandée.

### 6. Audit de câblage IDF, objet par objet (`scratchpad/verify_residential_idf.py`)

Run complet (office+retail+hotel+résidentiel, `seed=42`, produit `BEM_Schedules_4split_2030_central.csv`,
`office_presence_multiplier_2030.csv` archétype `Office_Knowledge`/`hybrid`, retail/hotel PR=QC —
config identique à un vrai run cellule `B_central`, cf. `scratchpad/cluster_B_central/manifest.json`) :

- **(a)** 27/27 Spaces résidentielles ont un objet `PEOPLE` les référençant directement — 0 manquante.
- **(b)(c)(d)** 27/27 : `Number_of_People == HHSIZE` du ménage tiré, `Number_of_People_Schedule_Name`
  == nom attendu, `Activity_Level_Schedule_Name` == nom attendu, méthode = `"People"`. 0 échec.
- **(d2)** Valeurs du `Schedule:Compact` (pas seulement le nom) relues et comparées aux 24 valeurs
  Weekday `Occupancy_Schedule` du ménage tiré : **27/27 correspondance exacte** (tolérance 1e-6).
- **(e)** 27 ménages distincts tirés pour 27 Spaces — **0 collision**, aucun effondrement ; 27 noms
  de `Number_of_People_Schedule_Name` distincts effectivement câblés.
- **(f)** L'ancien objet `PEOPLE` SpaceList-level (`HighriseApartment Apartment People`) est **conservé**
  dans l'IDF de sortie, `Number_of_People=0.0`, méthode `"People"` — neutralisé, pas supprimé,
  auditable.
- **(g)** Converse — 0 référence des nouveaux objets `PEOPLE` résidentiels chevauchant un nom de
  Tag-2 non-résidentiel ; comptages office=6/retail=3/hotel=3 **identiques** au run isolé sans
  résidentiel (6/3/3, §5).
- **(g2)(g3)** Converse renforcée — 0 des 27 références résidentielles ne correspond à une Space
  non-résidentielle ; l'ensemble des 27 références est un sous-ensemble strict des 27 Spaces
  résidentielles (`<=`, vérifié `True`).
- **(h)** `LIGHTS`/`ELECTRICEQUIPMENT` résidentiels : 2 + 1 objets, **inchangés**, toujours
  SpaceList-level (hors périmètre §4).
- **Schedule:Compact** : 54 objets créés (27 Occ `Fraction` + 27 Met `Any Number`), les deux
  `ScheduleTypeLimits` existent déjà dans l'IDF source (`Fraction`, `Any Number`) — pas de référence
  pendante.
- **Déterminisme** : deux runs indépendants (copies fraîches, même seed 42) → `assignment` dict
  **identique** (`==` True) ET IDF de sortie **md5 identique**
  (`937c95fe4b5bb96c85ff0913b0dde753` les deux fois).

### 7. Ce qui n'a PAS été vérifié

- **Aucun EnergyPlus exécuté** (interdit par la tâche) — la correction énergétique du « 2J Bug A »
  (distribution par zone, neutre sur les totaux annuels) n'est donc **pas mesurée ici**, seulement
  le câblage IDF qui la rend possible.
- Uniquement la tour `TallBuilding` / MTL testée. `SuperTallBuilding` (nombre de Spaces résidentielles
  potentiellement différent) et les IDF CAN_CLG non sondés — le code est générique (compte les Spaces
  dynamiquement, ne suppose jamais 27), mais pas exercé sur ces fichiers.
- Le tirage n'a été exercé que sur les produits 2022 et 2030_central — pas 2030_cons/opt (même code,
  même filtre DTYPE, distribution identique vérifiée pour central ; cons/opt non lus dans cette
  tâche).
- `assert_wiring()` (W2/W3) n'a pas été étendu au chemin résidentiel — reste scopé PEOPLE
  office/retail/hotel comme avant ; hors périmètre de cette tâche (point ouvert mineur #3 du doc
  d'implémentation, non traité ici).
- Pas de test sur un cas dégénéré (pool de ménages filtrés plus petit que le nombre de Spaces) au-delà
  de la levée d'exception vérifiée par lecture de code (`draw_residential_households` lève
  `ValueError` si `len(pool) < n` — pas déclenché en pratique ici, le pool réel est 266× plus grand
  que le besoin).

Fichiers touchés : `eSim_bem_utils/commercial_integration.py` (seul fichier modifié). Aucun fichier
ML protégé touché. Scripts de vérification (non versionnés, scratchpad) :
`probe_residential_structure2.py`, `regression_test_office_retail_hotel.py`,
`verify_residential_idf.py`, `commercial_integration_ORIGINAL.py` (reconstruction pré-édit pour la
régression).

---

## Progress Log — 2026-07-28 (employé) : Sous-étape 8A fermée — produits historiques 2005/2010/2015 générés (résidentiel + office + retail ; hôtel volontairement exclu)

**Tâche** : `3rdJ_08_implementation_improvements.md` §C (sous-étape 8A). LOCAL uniquement, aucun
EnergyPlus lancé, aucun accès cluster.

**Livrable** : nouveau script `3rdJ_08A_gen_historical_products_4split.py` (Step8_docs/) +
9 CSV dans `Step8_docs/outputs_step8/historical_schedules/` (3 années × {résidentiel, office,
retail}). Compile-check `py -3 -m py_compile` propre.

### Réutilisation, pas de reimplémentation

Le script charge `3rdJ_07_aug_to_bem_4split.py` via `importlib.util` (nom de fichier non
importable normalement) et appelle **directement** ses fonctions : `convert()`,
`complete_day_types()`, `build_office_multiplier()`, `build_retail_product_2022()` (générique
malgré son nom — ne lit que PR/DDAY_STRATA/RET, correcte pour n'importe quelle année), plus
`check_mutex()`, `run_residential_gates()`, `run_office_gates()`, `run_retail_gates()`,
`atomic_write()`. Seul code réellement nouveau : `demo_assemble()` (assemblage démographique
apparié par paliers), porté de `Leg2_2-split/Step8_docs/3rdJ_08A_gen_historical_schedules.py`,
étendu de ACT+HOM+WRK à **ACT+HOM+WRK+RET** (4-split).

### 🔴 Hôtel — délibérément NON généré

Décision manager déjà prise, non rouverte : `hotel_multiplier_lookup.csv` ne couvre que 2011–2022
et le sol QC ne commence qu'en 2019. Fabriquer une courbe hôtel 2005/2010/2015 aurait extrapolé à
l'aveugle ou figé un canal pendant que les 3 autres varient — un confound province×canal. Le canal
hôtel reste donc **NECB baseline, non-injecté, sur les 3 années historiques, dans les deux villes**
— uniforme, donc sans confound et sans rien fabriquer.

### Cadre stock — lu dans le code Step-7, pas supposé

Vérifié à l'exécution (pas deviné) : `3rdJ_25CEN_aug_Full_Aggregated_excl.csv` contient les
**4 cycles dans le même fichier** (CYCLE_YEAR ∈ {2005,2010,2015,2022}), **29 502 lignes-personne**
au total. `cmd_year_2022()` de Step-7 lit ce fichier **sans filtre CYCLE_YEAR** — le "stock" qui a
déjà produit le `BEM_Schedules_4split_2022.csv` verrouillé est donc le fichier **entier non
filtré** : 29 502 lignes, **23 115 SIM_HH_ID uniques**. Ce script réutilise exactement le même
stock (même fichier, même absence de filtre) pour que les produits historiques reposent sur la
même population que 2022/2030.

### 🔴 Choix retenu pour le pic retail — `ref_peak=None` (self-normalisant), PAS le correctif 2030

Les années historiques n'ont **aucun levier de bande**. `build_retail_product_2022()` est le
chemin `ref_peak=None` — c'est **le chemin correct ici**, pas un raccourci : il n'y a rien à
annuler puisqu'aucun rééchelonnage de bande n'existe en amont. Appliquer mécaniquement le
correctif `ref_peak=<base_peak>` du Défaut 1 aurait été une mauvaise application (ce correctif
existe pour un problème — annulation d'un levier de bande — qui n'existe pas ici).

### 🔴 Choix délibéré : le rake Phase-8B de Leg-2 N'EST PAS porté

`rake_cycle()` de Leg-2 bascule indépendamment, colonne par colonne, les lignes `IS_SYNTHETIC==1`
de `hom30` puis `wrk30` vers la marginale observée du cycle. L'audit 2J→3J (MEMORY.md) a identifié
que cette bascule indépendante colonne-par-colonne est **précisément le mécanisme** qui a produit
le bug de conflit mutex hom30/wrk30 dans le pipeline 2 canaux — c'est pour ça que `check_mutex()`
(H8) existe : "Leg-2's Step-7 validator had no mutex check". Porter ce même mécanisme sur un
**troisième** canal indépendant (`ret30`) aurait probablement reproduit la même classe de bug,
en pire.

**Décision retenue** : pool = lignes `IS_SYNTHETIC==0` (observées) uniquement par cycle, et le
bloc ACT+HOM+WRK+RET de la ligne appariée est copié **en un seul bloc** (pas colonne par colonne)
— une vraie ligne de journal est mutex-cohérente par construction, et une copie en bloc préserve
cette cohérence. **Vérifié, pas supposé** : `check_mutex()` tourne sur le pool, sur l'assemblage,
et sur le résultat complété, pour chacune des 3 années — **0 conflit à chaque fois** (voir logs
ci-dessous). Conséquence : pools plus petits que le rake de Leg-2 (2005 : 5 184 lignes obs. /
2010 : 3 963 / 2015 : 4 112) mais largement suffisants — la cascade à 4 paliers résout 100 % des
29 502 lignes de stock à chaque année (voir table des paliers ci-dessous).

### Exécution — logs réels (première passe, `--year all`)

| Année | Pool observé | Paliers (T1→T4 restant) | check_mutex (pool / assemblé / complété) | Résidentiel | Office | Retail |
|---|---|---|---|---|---|---|
| 2005 | 5 184 lignes | 27 617→1 885→1 547→338→300→38→38→0 | 0/0/0 conflit | GATE PASS, 1 109 520 lignes | GATE PASS, 144 lignes | GATE PASS, 288 lignes, pic=0,9500 |
| 2010 | 3 963 lignes | 27 126→2 376→2 102→274→241→33→33→0 | 0/0/0 conflit | GATE PASS, 1 109 520 lignes | GATE PASS, 144 lignes | GATE PASS, 288 lignes, pic=0,9500 |
| 2015 | 4 112 lignes | 27 135→2 367→2 129→238→226→12→12→0 | 0/0/0 conflit | GATE PASS, 1 109 520 lignes | GATE PASS, 144 lignes | GATE PASS, 288 lignes, pic=0,9500 |

Complétion jour-type (donor-draw) identique en comptage pour les 3 années (DDAY_STRATA vient du
stock, inchangé) : 15 222 HH WD-only → Weekend (18 167 lignes-membre), 5 540 HH WE-only → Weekday
(5 948 lignes-membre) → 53 617 lignes-personne complétées par année, avant `convert()`.

### md5 + row counts (9 produits, seed=42)

| Fichier | md5 | Lignes |
|---|---|---|
| `BEM_Schedules_4split_2005.csv` | `ac93709ed003fb2491fead288c96c3e2` | 1 109 520 |
| `office_presence_multiplier_2005.csv` | `5c5ba09bf336bb21230e1ea5451e77f5` | 144 |
| `retail_presence_multiplier_2005.csv` | `7da83f87ef1ddd452224e8e562c4f49a` | 288 |
| `BEM_Schedules_4split_2010.csv` | `bb3d365174d636b4fcd1d871876920ba` | 1 109 520 |
| `office_presence_multiplier_2010.csv` | `95c98a066789afc60f7b6cc0f8f984a6` | 144 |
| `retail_presence_multiplier_2010.csv` | `eca3416c90df6dc990739a4822afe701` | 288 |
| `BEM_Schedules_4split_2015.csv` | `a2048afc927186256535c8ea233de105` | 1 109 520 |
| `office_presence_multiplier_2015.csv` | `3278c9111ba983293401a0fd992bf417` | 144 |
| `retail_presence_multiplier_2015.csv` | `158c26d0aa50a092193198ecc6c3343a` | 288 |

### Déterminisme — vérifié, pas supposé

Script relancé intégralement une seconde fois (`--year all --skip-compare`) : les 9 md5 ci-dessus
sont **identiques** entre les deux passes (comparaison directe des sorties md5 imprimées par le
script, avant/après). Fichiers `*_BAK_2026-07-28.csv` créés par `atomic_write()` lors de la 2e
passe supprimés après vérification (bruit, pas des livrables).

### 🔴 Vérification Défaut-2 — colonnes CONSOMMÉES, pas md5, pairwise sur les 4 scénarios

Colonnes vérifiées : résidentiel `Occupancy_Schedule`+`Metabolic_Rate`
(`eSim_bem_utils/integration.py:379-380`), office `AT_WORK_fraction`
(`commercial_integration.py:240-249`), retail `multiplier` (`commercial_integration.py:252-263`).
**Aucun Δ = 0 sur aucune des 6 paires, sur aucun des 3 canaux** — les 4 scénarios (2005, 2010,
2015, 2022) sont bien 4 scénarios distincts au niveau BEM :

| Paire | Résid. `Occupancy_Schedule` max\|Δ\| (lignes diff.) | Résid. `Metabolic_Rate` max\|Δ\| | Office `AT_WORK_fraction` max\|Δ\| (lignes diff.) | Retail `multiplier` max\|Δ\| (lignes diff.) |
|---|---|---|---|---|
| 2005 vs 2010 | 1,0000 (421 825/1 109 520) | 175,00 (711 851/1 109 520) | 0,0842 (143/144) | 0,4725 (155/288) |
| 2005 vs 2015 | 1,0000 (423 059/1 109 520) | 175,00 (710 905/1 109 520) | 0,0692 (144/144) | 0,7582 (154/288) |
| 2005 vs 2022 | 1,0000 (419 437/1 109 520) | 175,00 (700 491/1 109 520) | 0,0566 (144/144) | 0,4580 (155/288) |
| 2010 vs 2015 | 1,0000 (427 725/1 109 520) | 175,00 (723 808/1 109 520) | 0,0918 (143/144) | 0,7548 (154/288) |
| 2010 vs 2022 | 1,0000 (424 212/1 109 520) | 175,00 (712 747/1 109 520) | 0,0523 (144/144) | 0,5621 (156/288) |
| 2015 vs 2022 | 1,0000 (419 614/1 109 520) | 175,00 (705 459/1 109 520) | 0,0724 (144/144) | 0,4614 (154/288) |

Retail pic (`multiplier`) = **0,9500 exact** sur les 3 années (attendu : `ref_peak=None`,
self-normalisant, aucun levier — cf. gate `run_retail_gates(..., retail_scenario=None)`).

### Produits 2022/2030 existants — inchangés, vérifié

md5 des 14 fichiers `outputs_step7/` (4 résidentiel, 2 office, 4 retail, 4 hôtel) recalculés
**avant** et **après** l'exécution complète du nouveau script : **identiques dans les 14 cas**.
Le nouveau script n'écrit que dans `Step8_docs/outputs_step8/historical_schedules/`, jamais dans
`Step7_docs/outputs_step7/`.

### Non vérifié / jugements assumés

- **Rake Phase-8B non porté** (voir ci-dessus) — décision documentée, pas une omission. Si le
  manager veut récupérer les lignes `IS_SYNTHETIC==1` des cycles historiques, il faudra concevoir
  un rake conscient du mutex à 3 canaux, pas porter celui de Leg-2 tel quel.
- **NOCS/LFTAG (donc archétype office / statut emploi) ne sont PAS ré-tirés par cycle** — hérité
  tel quel de `demo_assemble()` de Leg-2 (seul le bloc journal ACT+HOM+WRK+RET est substitué, les
  attributs de stock — dont NOCS/LFTAG — restent ceux du stock 2022/multi-cycle figé). Ce n'est
  pas un nouveau choix : c'est le comportement déjà présent dans le précédent Leg-2, simplement
  reconduit tel quel.
- **Pas de check de continuité longitudinale** (val §0.4 du précédent Leg-2, ex. "2005 ≤ 2010 ≤
  2015 ≤ 2022 progressif") n'a pas été porté — hors scope explicite de la tâche (§C ne demande que
  la génération + vérification Défaut-2, pas un rapport de validation complet). Les écarts
  observés ci-dessus (jusqu'à 0,09 sur `AT_WORK_fraction`, jusqu'à 1,00 sur `Occupancy_Schedule`)
  n'ont pas été interprétés substantivement — seule leur non-nullité a été vérifiée.
- **Fichiers `_BAK_*` créés par `atomic_write()`** lors de re-runs restent une source de bruit
  disque potentielle si le script est relancé plusieurs fois sans nettoyage manuel — comportement
  hérité de Step-7, non modifié ici.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

---

## Progress Log — 2026-07-28 (employé) : Défaut `residential_common` fermé — `classify_tag2()` distingue enfin les 2 sous-populations, comme son propre docstring le promettait

**Tâche** : `3rdJ_08_implementation_improvements.md` (table des points ouverts, items #3 et #4) +
défaut trouvé par le manager sur `classify_tag2()`. LOCAL uniquement, aucun EnergyPlus lancé,
aucun accès cluster.

### 1. Vérification empirique AVANT tout changement

Comptage direct des objets `Space` (regex sur le champ `Tag 2`, pas eppy — évite toute dépendance
IDD pour ce premier passage) sur les 2 IDF v242 réels, réunis localement sous
`3J_docs_occ_nTemp/Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/CAN_MTL/` :

| Tour | `HighriseApartment Apartment` (résid. occupé) | `HighriseApartment Corridor` | `HighriseApartment Office` | **Total "residential" actuel** | Total `Space` (avec plénums sans Tag-2) |
|---|---|---|---|---|---|
| **Tall** | 27 | 2 | 1 | **27 + 3 = 30** | 164 (160 avec Tag-2 + 4 plénums nus) |
| **SuperTall** | 41 | 3 | 1 | **41 + 4 = 45** | 256 (250 avec Tag-2 + 6 plénums nus) |

**Chiffres du manager confirmés exacts pour Tall (27 + 3 = 30).** Pour SuperTall, comme
anticipé, les comptes diffèrent : **41 + 4 = 45** (pas 30). Tall = 164 Spaces matche le
recensement AUDIT-W déjà verrouillé (`30 résid / 33 bureau / 9 commerce / 25 hôtel /
63 service_MEP = 164`, job 1169582/1169584) — reconstruit ici colonne par colonne :
office=33 (9 OpenOffice+14 ClosedOffice+4 Conference+2 Classroom+2 Dining+2 Restroom), retail=9,
hotel=12+13=25 (guestroom+support), service_mep=63, résid=30, +4 plénums nus = 164. ✅

Le défaut est bien réel et bien celui décrit : `_CHANNEL_OF_TAG2` (ancien code, L124-126) mappait
`TAG2_RESIDENTIAL | TAG2_RESIDENTIAL_COMMON` **tous les deux** sur `"residential"` — aucune Space
n'était perdue (elles restent comptées), mais le sous-total occupé (27) et le sous-total commun
non-injecté (3) n'étaient **jamais distinguables** en aval, alors que le docstring de
`classify_tag2()` promettait déjà `residential_common` comme valeur de retour possible depuis le
23/07. Le test `channel in ("residential", "residential_common")` du dispatch loop (L640 avant
édition, ~L653 après) était donc du code mort — `residential_common` ne sortait jamais de
`classify_tag2()`.

### 2. Correctif — `eSim_bem_utils/commercial_integration.py`

- **L137-141** : `_CHANNEL_OF_TAG2` — boucle unique qui mappait les deux ensembles sur
  `"residential"` scindée en deux boucles ; `TAG2_RESIDENTIAL_COMMON` mappe maintenant sur
  `"residential_common"`, exactement ce que le docstring de `classify_tag2()` (L154-156, inchangé)
  documentait déjà. Changement de **4 lignes**, aucune autre ligne touchée dans la fonction.
- **L48-61** (docstring de module) : la note du 23/07 affirmant qu'« aucun prototype IDF mixte
  Tag-2-routable n'existe dans ce repo » — **fausse**, le recensement Tag-2 mesure le contraire
  depuis le 28/07 (AUDIT-W, PROBES) — a induit un agent en erreur une fois (item ouvert #4).
  Corrigée : nouvelle note 2026-07-28 en tête, avec les chiffres du recensement Tall (164/30/33/
  9/25/63) et pointeur vers AUDIT-W (9P/1W/0F) + PROBES (23P/0W/2F) comme preuve que le module a
  bien été exercé contre le prototype réel. L'ancienne note est conservée intégralement en
  dessous, marquée PÉRIMÉE, pour la provenance — rien supprimé, seulement corrigé.
- **L726-742** (`assert_wiring()` docstring, item ouvert #3) : annonçait W2+W3, ne codait que W2.
  **Décision : corriger le docstring, ne PAS implémenter W3 ici.** Justification (une ligne) : W3
  est déjà implémenté, testé et **PASS-prouvé** dans `3rdJ_08W_audit_wiring.py` Block 5 (lignes
  298-360, `_representative_baseline_name`/`_schedule_profile`), qui a besoin **à la fois** de
  l'IDF source pré-injection (pour retrouver le baseline qu'un canal remplace) et de l'IDF injecté
  — deux IDF que la signature actuelle d'`assert_wiring(idf, ...)` (un seul IDF) ne peut pas
  porter ; dupliquer la logique ici contre une signature qui ne peut pas la porter aurait recréé
  exactement le piège « docstring qui contredit le code » (item #4) sous une autre forme. Le
  docstring dit maintenant explicitement « W2 ONLY », avec renvoi vers l'implémentation W3 réelle.

Aucune ligne de `inject_residential()`, `inject_mixed_use()` (hors docstring), des loaders, des
builders `Schedule:Compact`, ou de la logique retail/hotel/office n'a été touchée.

### 3. Consommateurs de `classify_tag2()` — recherche exhaustive, AUCUN ne casse

Recherche `grep -rn classify_tag2` sur tout le repo : 2 consommateurs Python hors module lui-même,
tous deux déjà câblés pour ce changement exact avant même qu'il soit fait :

- **`3rdJ_08P_probe_driver.py`** (`channel_hourly.csv`) : `CHANNEL_AGG` (L204-210) contient déjà
  `"residential": {"residential", "residential_common"}` — le mapping fin→agrégat re-fusionne les
  deux dans la même colonne `residential_*` de `channel_hourly.csv`, **exactement comme
  `office_support`→`office` et `hotel_support`→`hotel` le font déjà** pour des Spaces jamais
  injectées non plus. Le runbook (`3rdJ_08_simulation_4split.md` L275) documentait déjà ce choix
  d'agrégation avant que le défaut soit fermé. **Aucune Space ne peut tomber dans `unknown`** :
  `_FINE_TO_AGG.get(fine)` résout `"residential_common"` vers `"residential"`, pas vers `None`.
- **`3rdJ_08W_audit_wiring.py`** : `agg` dict (L171-177) fait `counts["residential"] +
  counts["residential_common"]` — même remarque, déjà pré-câblé. `EXPECTED_CENSUS["residential"]
  = 30` (L53, « informative only -- NEVER used to force a PASS/FAIL ») reste correct après le
  correctif car c'est la somme qui est comparée.

**Aucun fix requis dans ces deux scripts.** Ils avaient été écrits en anticipant ce correctif
exact (commentaires + structure de données déjà en place), ce qui a été vérifié en lisant le code,
pas supposé.

### 4. Conservation des comptes — preuve numérique, avant/après, 2 tours

Script `verify_census_conservation.py` (scratch), charge le module AVANT (reconstruit depuis mon
propre `Read` de session, avant édition) et APRÈS (fichier édité) via `importlib`, applique la
même logique d'agrégation que les 2 consommateurs ci-dessus, sur les vrais Tag-2 des 2 IDF :

| Tour | AVANT (fin) | APRÈS (fin) | AVANT (agg) | APRÈS (agg) | Total brut | Conservé ? |
|---|---|---|---|---|---|---|
| Tall | `residential=30` (pas de `residential_common`) | `residential=27, residential_common=3` | `residential=30, ..., total=164` | `residential=30, ..., total=164` | 164 | ✅ **True** |
| SuperTall | `residential=45` | `residential=41, residential_common=4` | `residential=45, ..., total=256` | `residential=45, ..., total=256` | 256 | ✅ **True** |

Le total agrégé (`residential+office+retail+hotel+service_mep+unknown`) est **identique
avant/après et égal au compte brut de `Space`** dans les deux tours — aucune Space ne disparaît
de la comptabilité, elle change seulement de sous-catégorie fine à l'intérieur du même agrégat
`residential`.

### 5. Preuve d'injection inchangée — result dict + md5 IDF, AVANT vs APRÈS

Reconstruit le fichier `commercial_integration.py` AVANT édition (texte exact de mon `Read` en
tout début de tâche, ce repo n'étant pas un dépôt git) dans le scratchpad, chargé via
`importlib.util` sous un nom de module distinct pour éviter toute collision avec la version
éditée. Injection complète (office+retail+hotel+résidentiel, seed=42) sur
`TallBuilding_..._Z6_v242.idf` réel (CSV Step-7 2022 réels), sortie vers 2 fichiers IDF distincts :

```
=== RESULT DICT EQUALITY ===
IDENTICAL: True

=== OUTPUT IDF MD5 ===
before: 1f2ffa816e69c18a07335264d6fd4e5e
after:  1f2ffa816e69c18a07335264d6fd4e5e
IDF MD5 IDENTICAL: True

before/after office={'n_spaces': 6, 'n_lights': 6, 'n_equip': 6} retail={'n_spaces': 3, 'n_lights': 4, 'n_equip': 3}
  hotel={'n_spaces': 3, 'n_lights': 3, 'n_equip': 3}
  residential={'n_spaces': 27, 'n_households_drawn': 27, 'n_carriers_neutralized': 1, ...}
  fallback=[] ambiguous_n=0
```

Les 2 IDF de sortie sont **md5-identiques** (pas seulement "résultats équivalents") et le dict de
retour complet (y compris `residential.assignment`, seed=42, 27 ménages tirés dans le même ordre)
est **strictement identique** — le correctif de classification n'a **aucun** effet sur ce que
`inject_mixed_use()` écrit dans un IDF ou renvoie à l'appelant, comme prévu (seule la fonction
`classify_tag2()` change, et son seul appelant interne au dispatch loop teste déjà
`channel in ("residential", "residential_common")` depuis le 23/07 — code mort qui devient actif
sans changer de branche).

### 6. Compile-check

`py -3 -m py_compile eSim_bem_utils/commercial_integration.py` → exit 0.

### Non vérifié / hors scope

- Le biais de dilution décrit par le manager (le niveau NECB constant des 3 Spaces communes gonfle
  la colonne `residential` agrégée de `channel_hourly.csv`) **n'est PAS résolu** par ce correctif
  — il ne pouvait pas l'être sans changer la logique d'agrégation des 2 consommateurs, ce qui était
  hors du périmètre demandé (« classification/accounting/documentation seulement », « ne pas
  altérer le comportement d'injection »). Ce correctif rend la distinction fine
  `residential`/`residential_common` **visible et exploitable** (recensement Tag-2, futurs scripts
  d'attribution) là où elle était auparavant du code mort ; il ne change pas le choix
  d'agrégation déjà pris par `3rdJ_08P_probe_driver.py`/`3rdJ_08W_audit_wiring.py` de refusionner
  les deux pour `channel_hourly.csv` — ce choix est cohérent avec le traitement déjà appliqué à
  `office_support`/`hotel_support` (jamais injectés non plus, toujours fusionnés dans l'agrégat
  parent) et n'a pas été rouvert ici.
- SuperTall Corridor(3)+Office(1) = 4 « common » n'a pas été recroisé avec un audit AUDIT-W dédié
  SuperTall (seul Tall a un job AUDIT-W nommé dans le runbook) — le chiffre 45 vient uniquement du
  comptage direct de cette tâche, pas d'un second passage cluster.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

---

### 2026-07-28 (employee) — Campaign driver BUILT + dry-run tested LOCALLY. Campaign STILL NOT LAUNCHED.

**Scope executed:** implementation-improvements.md §C-bis/D task brief -- build the 56-cell
campaign table + local runner, dry-run all 56 cells, ONE short smoke run, settle the Calgary
climate-zone open item. **The 56-run campaign was NOT launched** (out of scope by explicit
instruction) -- only a 1-cell, 2-day smoke run was executed.

**Files added** (`Step8_docs/`, all `py -3 -m py_compile` clean):

| File | Role |
|---|---|
| `3rdJ_08D_campaign_cells.py` | Pure data module. `build_campaign_cells(repo_root)` derives the 56 cells programmatically (`BUILDINGS x CITIES x SCENARIOS` loop, never a hand-typed literal) and returns each cell with resolved absolute `idf`/`epw`/channel-csv paths plus a precomputed `missing_inputs` list. |
| `3rdJ_08D_campaign_driver.py` | Per-cell engine (`--cell 0-55 --engine local`). Loads `3rdJ_08P_probe_driver.py` via `importlib` and REUSES its `md5_file`, `_compute_inputs_hash`, `_check_inputs_hash_guard`, `_ensure_output_objects`, `_do_postprocess`, `_energyplus_provenance`, `_write_manifest`, `SQL_EXTRACTION_METHOD` verbatim -- zero duplication of the inject/simulate/postprocess mechanics. Adds only what's genuinely new: building/city-varying IDF+EPW resolution, and `--smoke-days N` (truncates the injected IDF's RunPeriod for a short end-to-end test; never used for a real cell). |
| `3rdJ_08D_campaign_local.py` | Windows orchestrator, same CLI shape as `3rdJ_08P_probes_local.py`. Loads that file via `importlib` and reuses its memory watchdog (`_committed_pct`/`_kill_active`/`_watchdog`, same module-level `_ACTIVE`/`_ACTIVE_LOCK`/`_ABORT`), `_cell_complete()`, and `_archive_stale()` **unmodified** -- one watchdog implementation, not two. `--workers` defaults to **6** (not cores-2), `--mem-abort` defaults to **80%**, both non-negotiable per the reference doc. |

**Strictly additive -- proved, not asserted:**

```
md5sum 3rdJ_08P_probe_driver.py 3rdJ_08P_probes_local.py 3rdJ_08P_probe_gates.py   # unedited by this task
py -3 3rdJ_08P_probes_local.py --dry-run
  === §P PROBE LOCAL | 7 cell(s) requested | INJ_HASH=cf69d508 | ... ===
    would run: cell 0 (baseline_necb) ... cell 6 (fallback_retail)
```

7-cell probe harness still enumerates its 7 cells correctly, untouched. (`INJ_HASH` here reads
`cf69d508`, not the `5670f602` recorded earlier in this log -- a concurrent session's
`classify_tag2()` residential/residential_common fix, entry immediately above, changed
`commercial_integration.py`'s md5 after that entry was written; both the probe and campaign
drivers pick this up dynamically, by design, so no action was needed here.)

**Dry-run: all 56 cells, 0 missing inputs.**

```
py -3 3rdJ_08D_campaign_local.py --dry-run
=== 3J Leg-3 Step-8 CAMPAIGN LOCAL | 56 cell(s) requested (of 56) | INJ_HASH=cf69d508 | ... ===
  ...
  56 cell(s) printed, 0 with a missing input.
```

Grouping (index order = building outer, city middle, scenario inner): cells 0-13 =
Tall/MTL, 14-27 = Tall/CLG, 28-41 = SuperTall/MTL, 42-55 = SuperTall/CLG, each block the same
14 scenarios (`Default_NECB, Y2022, B_cons, B_central, B_opt, Y2005, Y2010, Y2015,
sens_office_cons, sens_office_opt, sens_retail_cons, sens_retail_opt, sens_hotel_cons,
sens_hotel_opt`). Sample resolved paths verified by eye against §3/§C-bis of the reference doc
(IDF md5s, EPW filenames). Historical (`Y2005/Y2010/Y2015`) cells resolve against
`Step8_docs/outputs_step8/historical_schedules/` (the concurrent session's products landed
there **during this task**, not `Step7_docs/outputs_step7/` as the task brief guessed --
verified by `ls`, band=`observed` confirmed by reading the CSVs' own `BAND` column) and each
carries `hotel_deliberately_absent` (channel key omitted -- `inject_mixed_use()` already treats
an absent key exactly like a missing file: loud `FALLBACK_LOUD`/`[FALLBACK] hotel channel data
missing` banner, verified by reading `commercial_integration.py:593-598`, not assumed).

**Guard interaction (constraint 3) -- fresh tree, proved twice.**

1. `3rdJ_08D_campaign_local.py`'s `DEFAULT_OUTROOT` is `Step8_docs/campaign_local/`, a directory
   the probe harness never writes to (`Step8_docs/probes_local/`) -- by construction, no
   `INPUTS_HASH` collision with any pre-`INPUTS_HASH` legacy probe manifest is possible; the
   first campaign write goes into an outdir that has never existed, so
   `_check_inputs_hash_guard()`'s "no manifest.json yet -> no-op" branch is what actually fires.
2. Demonstrated live: running cell 3 twice (smoke run, then the identical command again) did
   **not** silently overwrite -- the second run correctly saw the first run's manifest
   (`rows=48`, smoke test) fail `_cell_complete()`'s hardcoded `rows == 8760` check (reused
   verbatim from the probe orchestrator) and archived it: `[archive] incomplete/stale outdir
   found -> archived to ...\B_central__Tall__MTL_STALE_20260728_204122 (never overwritten in
   place)`. This is a useful side effect of reuse-not-reinvent: a truncated smoke-test output can
   never masquerade as a complete campaign cell, with zero extra code.

**Smoke run (constraint: ONE short run only, not the campaign).**

`py -3 3rdJ_08D_campaign_local.py --cells 3 --workers 1 --smoke-days 2` -- cell 3 =
`B_central__Tall__MTL` (Tall building, Montreal, the 2030 central bundle; RunPeriod truncated to
Jan 1-2).

| Field | Value |
|---|---|
| Wall clock | **0.8 min (48 s)**, reported by the orchestrator; `time` wrapper measured 50.4 s real (incl. python/module-load overhead) |
| `ep_return_code` | 0 |
| `hourly_meters.csv` / `channel_hourly.csv` rows | 48 / 48 (== `expected_rows`, 2 days x 24 h) |
| `inject_mixed_use_result` n_spaces | office 6, retail 3, hotel 3 -- matches the AUDIT-W-verified Tall Tag-2 census, no fallback |
| `FALLBACK_LOUD` | `None` -- all 3 channels injected as configured |
| `PLATFORM` / `engine` / EnergyPlus | `win32` / `local` / `24.2.0-94a887817b` (same build as cluster) |
| `INPUTS_HASH` | `fdc5c095` (fresh -- this is the first time this exact channel-CSV set has been hashed) |

Full chain (inject -> ensure-outputs -> RunPeriod-truncate -> EnergyPlus -> SQL -> 2 CSVs ->
manifest) proven end-to-end on the CAMPAIGN driver specifically (not just the probe driver) for
the first time. **A 2-day (or design-day) run's wall-clock is NOT used to extrapolate a full-year
estimate below** -- EnergyPlus's fixed per-run costs (sizing, multi-iteration warmup-day
convergence) dominate a 2-day RunPeriod and would make any such extrapolation an overestimate
by a large, unquantified factor; the existing measured 15.9 min/run **annual** figure (SuperTall,
MTL, 1 worker, implementation-improvements.md) is used instead, as the task instructed.

**Cost estimate for the (not-yet-launched) 56-run campaign**, anchored on the 15.9 min/run
measured full-year figure, assumptions stated explicitly (none of these are separately verified
in this pass):

- Applies **15.9 min/run uniformly to all 56 cells** -- no Tall-vs-SuperTall differential is
  assumed (Tall is the smaller building, 26,750 vs 40,846 m², so this is likely a mild
  over-estimate for the 28 Tall cells, not an under-estimate).
- Applies the same figure to **CLG cells** as MTL (no Calgary annual run has been measured yet
  locally or on cluster -- flagged as an open verification item below, not assumed away).
- **Serial (1 worker):** 56 x 15.9 min = **890.4 min = 14.84 h**.
- **6 workers, ideal linear scaling:** 890.4 / 6 = **148.4 min = 2.47 h**.
- **6 workers, real (contention-adjusted):** implementation-improvements.md's own local-port
  measurement for a differently-sized 64-run set found real wall-clock ran **1.07x-1.43x** over
  the linear-scaling estimate (theoretical 2.8 h -> real 3-4 h). Applying the same factor range
  to 2.47 h theoretical: **~2.6-3.5 h real wall-clock** for the full 56-run campaign at
  `--workers 6`.
- RAM: previously measured ~525 MB/run x 6 concurrent ~= 3.1 GB, far under the 80% commit-charge
  watchdog ceiling on a 63.5 GB machine -- not expected to be limiting, consistent with the prior
  measurement.

**Calgary climate-zone verdict (open item #2) -- SETTLED, with numbers. File NOT renamed.**

Manager hypothesis under test: "_6B" (filename) vs. "6A" (`.stat`'s own ASHRAE-169-2021 calc) vs.
"Z7A" (IDF/runbook) are two different classification systems (NECB vs. ASHRAE-169), not a
conflict. **Verdict: confirmed in spirit, but with a genuine boundary-case nuance the "just two
systems" framing understates -- worth documenting, not renaming.**

1. **NECB climate-zone boundaries by HDD18** (confirmed via web search, cross-checked against
   this repo's own Montreal EPW as a calibration point): Zone 4 <3000, Zone 5 3000-3999, **Zone 6
   4000-4999, Zone 7A 5000-5999**, Zone 7B 6000-6999, Zone 8 >=7000.
2. **Montreal calibration check** (`CAN_QC_Montreal...716120_TMYx_6A.stat`): HDD18 = 4112
   (ASHRAE design-condition basis, 18.3 C) / 4100 (actual-weather-file basis, 18 C) -- solidly
   inside the 4000-4999 Zone-6 band, matching this repo's own `Z6` tag for Montreal. Confirms the
   boundary table and the read method are being applied correctly before trusting the Calgary
   number.
3. **Calgary Olympic Park EPW's own `.stat`**
   (`CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.stat`): HDD18 = **4933** (design-
   condition basis, 18.3 C) / **4852** (actual-weather-file basis, 18 C). **Both fall inside the
   NECB Zone-6 band (4000-4999)** -- 65-151 HDD, i.e. **1.3%-3.0%, below** the 5000 threshold that
   would make it Zone 7A. Re-deriving NECB zone directly from this file's own numbers gives
   **Zone 6, not Zone 7A** -- a close boundary call, not a clean match to either label.
4. **Official/government Calgary climate design data** (web search, city-of-Calgary building-code
   documentation, presumably the long-term Calgary Intl Airport (YYC) station normal, a
   *different* station and vintage than this TMYx file's Olympic-Park-Upper station):
   HDD18 ~= 5000 -- **right at the NECB 6/7A boundary**, on the Zone-7A side.
5. **ASHRAE-169-2021 is a genuinely different numeric scale** from NECB (different HDD/CDD
   combination criteria, IP-derived thresholds) -- the `.stat`'s own calculated "6A" tag and the
   filename's "_6B" token are ASHRAE-169 labels, not NECB ones, so their digit clash with the
   IDF's NECB "Z7A" is not on its face a contradiction. This part of the hypothesis holds.

**Conclusion:** the IDF/runbook's `Z7A` tag reflects Calgary's *canonical/official* NECB zone
assignment (a different, longer-record station than this specific downloaded EPW). This
particular TMYx EPW's *own* HDD18 sits marginally on the Zone-6 side of the same NECB boundary --
a genuine near-boundary case (Calgary is close enough to the NECB 6/7A line that station choice
and normal-vs-typical-year vintage can flip which side it lands on), not a data error and not
"just two unrelated systems" either. **Recommendation:** do not rename the EPW (not done here,
per instruction; its own ASHRAE self-tag is internally consistent). Document in the runbook that
(a) the campaign's CLG cells are labelled `Z7A` per the IDF/official designation, and (b) the
underlying weather file is a documented near-boundary case on the NECB scale -- worth a footnote
on any published MTL-vs-CLG severity comparison, not a blocking defect.

**Explicit list of what still blocks the 56-run campaign launch** (unchanged in kind from
implementation-improvements.md §"Le travail restant", reconfirmed after this task):

1. **Residential injector (OD-8R-L3, item B) -- still not implemented.** Every campaign cell
   built here, like every probe cell, has no `"residential"` key in `channels`; residential
   Spaces stay at NECB baseline in all 56 cells until this is built and wiring-audited.
2. **No Calgary annual run has ever been measured**, locally or on cluster (only MTL/SuperTall's
   15.9 min figure exists) -- the cost estimate above assumes CLG ~= MTL runtime, unverified.
3. **8A historical hotel gap is by design, not a blocker** (manager decision, documented above)
   -- listed here only so a future reader doesn't mistake the 3 hotel-absent cells for missing
   work.
4. **No cluster port of the campaign driver/table exists** -- `3rdJ_08D_campaign_driver.py`
   currently hard-refuses `--engine cluster` (`[FAIL] engine='cluster' not implemented`); this
   task's scope was LOCAL-only.
5. **The 56-run campaign itself has not been launched** -- by this task's explicit instruction,
   not a technical blocker; the driver/table/orchestrator are now dry-run-proven and smoke-tested,
   ready for a manager-authorized launch once items 1-2 above are closed.
6. Minor open items #1/#3/#4 from implementation-improvements.md (staff_shoulder_flag naming,
   W3 module-vs-validator split, stale docstring) remain untouched, out of this task's scope.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

## Progress Log — 2026-07-28 (employee): `residential_common` un-merged from `channel_hourly.csv` — own column, not folded into `residential`

**Task**: post-processing-only fix to `3rdJ_08P_probe_driver.py`'s `channel_hourly.csv` builder.
The earlier `classify_tag2()` fix (entry immediately above) restored `residential_common` as a
real, distinct return value, but `CHANNEL_AGG` still re-merged it back into `residential`, by
analogy with `office_support`→`office` and `hotel_support`→`hotel`. That analogy does not hold:
`office_support`/`hotel_support` Spaces **are** modulated by their channel's injection;
`residential_common` (corridors) is injected by **nobody** — the commercial MODULATE loop skips
it (`continue`, `commercial_integration.py` ~L640) and `inject_residential()` iterates only
`TAG2_RESIDENTIAL`. Folding an uninjected, constant-NECB Space into `residential` dilutes its
reported level relative to `office`/`hotel` (whose `*_support` counterparts genuinely are
injected) — a real bias for per-channel attribution. LOCAL only, no EnergyPlus run, no cluster
access.

### 1. Verified the merge before touching anything
Read `CHANNEL_AGG` (`3rdJ_08P_probe_driver.py`, then L204-210) and confirmed: `"residential":
{"residential", "residential_common"}`, feeding `_FINE_TO_AGG` (fine→agg), consumed at
`_build_zone_channel_map()` (L577-596) and the emitted-column list in `_write_channel_hourly_csv()`
(`channels = ["office", "retail", "hotel", "residential", "service_MEP"]`, old L667) — confirmed
`residential_common` had no column of its own. User's description matched the code exactly.

### 2. Change — file:line
- `3rdJ_08P_probe_driver.py` L204-215ish (`CHANNEL_AGG`): `"residential"` now maps only to
  `{"residential"}`; added a new `"residential_common": {"residential_common"}` entry, with an
  inline comment stating the office_support/hotel_support-vs-residential_common distinction and
  reasoning (see above).
- `3rdJ_08P_probe_driver.py` `_write_channel_hourly_csv()`, the `channels` list (was L667): now
  `["office", "retail", "hotel", "residential", "residential_common", "service_MEP"]` — one new
  column added, nothing removed, nothing reordered relative to the existing 5.
- `3rdJ_08D_campaign_driver.py` / `3rdJ_08D_campaign_cells.py`: **no CHANNEL_AGG copy exists in
  either file** (verified by reading both in full) — the campaign driver loads the probe driver
  via `importlib` (`_load_module(PROBE_DRIVER_PY, ...)`) and calls `_probe._do_postprocess()`
  verbatim, which internally calls the probe module's own (now-fixed) `_write_channel_hourly_csv`.
  It inherits the fix for free, exactly as anticipated in the task brief. No edit needed there.
- `3rdJ_08W_audit_wiring.py`: NOT changed. Its `agg` dict (L171-177) folds `residential_common`
  into `residential` too, but only for a printed Tag-2 **census count** (a diagnostic block,
  never written to `channel_hourly.csv` or any persisted artifact) — out of this task's scope
  (probe driver `channel_hourly.csv` builder only, per the handoff).

### 3. office_support / hotel_support decision
Left merged into `office` / `hotel` respectively — unlike `residential_common`, both `*_support`
sub-populations genuinely receive their channel's injected schedule (office_support Spaces get
the office MXU schedule, hotel_support get the hotel MXU schedule), so folding them costs no
information: the reported `office`/`hotel` level already reflects the injected condition end to
end, with no uninjected constant-baseline component hiding inside it.

### 4. Conservation proof (numbers)
Ran `--postprocess-only --engine local --force-inj-hash 5670f602` (existing probe cell 1,
`B_central`, `probes_local/campaign_5670f602/B_central/`) to regenerate `channel_hourly.csv`
against the fixed driver, using its own already-existing `run/eplusout.sql` (data unchanged, only
the post-processing column split changed). Compared the pre-edit CSV (saved aside) against the
regenerated one, `pandas`, 8760 rows both:

- Grand total over ALL columns, ALL cells: OLD = 2,616,480,845,543.054199; NEW =
  2,616,480,845,543.053711 — delta = -0.000488 (float64 rounding noise on a ~2.6e12 total,
  relative error ~2e-16, not a real difference).
- Per-metric residential split: `residential_people` OLD=385052.224461 vs NEW
  `residential_people + residential_common_people` = 385052.224461 (delta 0.0);
  `residential_lights` OLD=113,248,465,381.305237 vs NEW sum = same to the last printed digit
  (delta 0.0); `residential_equip` OLD=430,315,808,608.432190 vs NEW sum = 430,315,808,608.432129
  (delta -0.000061, same float noise).
- `office_*`, `retail_*`, `hotel_*`, `service_MEP_*` (9 columns): max|delta| OLD vs NEW = 0.0 for
  every one — byte-identical, untouched by this edit.
- New `residential_common_*` totals (not zero, not vanished): people=11,105.296307,
  lights=39,048,390,311.179530, equip=12,410,743,937.257278.
- New `residential_*` (apartments only) totals: people=373,946.928154,
  lights=74,200,075,070.125717, equip=417,905,064,671.174866. Sum with residential_common above
  reproduces the OLD combined totals to float precision. No Space's load vanished from the
  accounting; conservation holds.

### 5. `--postprocess-only` recovery proof + timing
Same command as above (`3rdJ_08P_probe_driver.py --cell 1 --postprocess-only --engine local
--outroot ./probes_local --force-inj-hash 5670f602`), run locally from a PowerShell/Bash shell,
timed with `time`: **wall-clock 14.508s real** (0.077s user / 0.030s sys — dominated by SQLite
read + eppy IDF reparse, not compute), well inside the ~40s recovery budget the INJ_HASH/
INPUTS_HASH design promises. `eplusout.sql` was never touched (no `run/` file's mtime changed
beyond what `--postprocess-only` itself writes: `hourly_meters.csv`, `channel_hourly.csv`,
`manifest.json`). Console confirmed `channel_hourly.csv: 8760 rows` and `mapped=5,045,760
unmapped=0 (of 5,045,760 report rows)` — same 0-unmapped result as before the edit (the 6
unmapped-tag-2 plenum Spaces reported are pre-existing/accepted, unrelated to this change).
`--force-inj-hash` was needed only because the probe cell's INJ_HASH predates the earlier
`classify_tag2()` fix (recorded manifest `INJ_HASH=5670f602`, live injector md5 now
`cf69d508`) — INJ_HASH intentionally does not move on a post-processing-only driver change, so
targeting the pre-existing outdir required pointing at its own recorded hash; this is expected
behaviour of the Defaut-3 path-hash design, not a new issue.

### 6. Gate check — `3rdJ_08P_probe_gates.py`
Read in full. It only ever reads columns named `f"{channel}_{metric}"` for `channel in
CHANNELS_COMMERCIAL = ("office", "retail", "hotel")` (P1, P4) plus a hardcoded `retail_*` list
(P4 reversion-identity block) — it never references any `residential*` column (P1's residential
leg is explicitly `"NOT EXERCISED — collapse rule unspecified"`, INFO-only, no column read). A
new `residential_common_*` column added to `channel_hourly.csv` is inert to every existing gate:
`pd.read_csv` picks it up as an extra column nobody selects. **No change needed, verified by
reading, not assumed.**

### 7. Compile check
`py -3 -m py_compile` on all four files (`3rdJ_08P_probe_driver.py`, `3rdJ_08D_campaign_driver.py`,
`3rdJ_08D_campaign_cells.py`, `3rdJ_08P_probe_gates.py`) — clean, no errors.

Net: 2 files touched (`3rdJ_08P_probe_driver.py` only — `CHANNEL_AGG` split + `channels` list),
0 files needed touching that didn't need it, injection behaviour untouched, no gate relaxed,
`--postprocess-only` recovery property verified intact (14.5s, not a re-simulation).

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

## Progress Log — 2026-07-28 (employee): residential channel wired into the CAMPAIGN cell table
(3rdJ_08D_campaign_cells.py) + channel-completeness gate added + smoke-tested LOCALLY. Campaign
STILL NOT LAUNCHED (only a `--smoke-days 2` single-cell run, per scope).

### 0. The defect (manager-verified)
`3rdJ_08D_campaign_cells.py` was built (see the "2026-07-28 (employee) — Campaign driver BUILT"
entry above) while the residential injector (OD-8R-L3) was still unimplemented.
`_bundle_channels()`/`_historical_channels()` returned office/retail(/hotel) only — no
`BEM_Schedules_4split_*.csv` was ever referenced. All 56 planned cells would have run with the 27
residential apartment Spaces at NECB baseline: the entire subject of this research absent from the
campaign, and `--dry-run` would have reported "0 missing inputs" because it only validates what is
listed, not what is omitted. Same failure shape as the retail `multiplier` defect (plausible,
silent, wrong).

### 1. Residential wired into every applicable scenario
`3rdJ_08D_campaign_cells.py`: `_bundle_channels()` (now takes a `residential_csv` arg) and
`_historical_channels()` (ditto) both append `"residential": {"csv": residential_csv, "seed": 42}`
(new module constant `RESIDENTIAL_SEED = 42`), matching the exact contract read from
`eSim_bem_utils/commercial_integration.py` — `inject_mixed_use()`'s docstring (:557-560):
`channels = {..., "residential": {"csv": "...", "seed": 42}}`, dispatched at :673-680 to
`inject_residential(idf, channels["residential"]["csv"], seed=channels["residential"].get("seed", 42), ...)`
(:423 signature). `Default_NECB` is untouched (`channels={}`, no residential key, no injection at
all — verified still the case after the edit).

All 8 residential product paths verified present on disk before wiring (`ls`, 2026-07-28):
- `Step7_docs/outputs_step7/BEM_Schedules_4split_2022.csv` (73,896,179 bytes)
- `Step7_docs/outputs_step7/BEM_Schedules_4split_2030_cons.csv` (73,975,101 bytes)
- `Step7_docs/outputs_step7/BEM_Schedules_4split_2030_central.csv` (73,970,363 bytes)
- `Step7_docs/outputs_step7/BEM_Schedules_4split_2030_opt.csv` (73,968,389 bytes)
- `Step8_docs/outputs_step8/historical_schedules/BEM_Schedules_4split_{2005,2010,2015}.csv`
  (73,885,807 / 73,901,604 / 73,909,754 bytes)

No path was missing. Column headers of all 3 product families verified identical and matching
`load_residential_pool()`'s `usecols` contract (`SIM_HH_ID, Day_Type, Hour, HHSIZE, DTYPE, BEDRM,
CONDO, ROOM, REPAIR, PR, MATCH_TIER, Occupancy_Schedule, Metabolic_Rate`) by reading the header row
of each file (`head -1`) — all three (2030_cons, 2022, 2005) byte-identical column sets.

### 2. 14-scenario x channel table (post-fix)
| # | scenario           | office | retail | hotel | residential | residential source |
|---|---------------------|:---:|:---:|:---:|:---:|---|
| 1 | Default_NECB        | – | – | – | – | none (pure NECB baseline, `channels={}`) |
| 2 | Y2022                | Y | Y | Y | Y | `BEM_Schedules_4split_2022.csv` |
| 3 | B_cons (2030)        | Y | Y | Y | Y | `BEM_Schedules_4split_2030_cons.csv` |
| 4 | B_central (2030)     | Y | Y | Y | Y | `BEM_Schedules_4split_2030_central.csv` |
| 5 | B_opt (2030)         | Y | Y | Y | Y | `BEM_Schedules_4split_2030_opt.csv` |
| 6 | Y2005 (historical)   | Y | Y | – (deliberate) | Y | `historical_schedules/BEM_Schedules_4split_2005.csv` |
| 7 | Y2010 (historical)   | Y | Y | – (deliberate) | Y | `historical_schedules/BEM_Schedules_4split_2010.csv` |
| 8 | Y2015 (historical)   | Y | Y | – (deliberate) | Y | `historical_schedules/BEM_Schedules_4split_2015.csv` |
| 9 | sens_office_cons     | Y (cons) | Y (central) | Y (central) | Y (**cons**) | `BEM_Schedules_4split_2030_cons.csv` |
| 10| sens_office_opt      | Y (opt) | Y (central) | Y (central) | Y (**opt**) | `BEM_Schedules_4split_2030_opt.csv` |
| 11| sens_retail_cons     | Y (central) | Y (cons) | Y (central) | Y (central) | `BEM_Schedules_4split_2030_central.csv` |
| 12| sens_retail_opt      | Y (central) | Y (opt) | Y (central) | Y (central) | `BEM_Schedules_4split_2030_central.csv` |
| 13| sens_hotel_cons      | Y (central) | Y (central) | Y (cons) | Y (central) | `BEM_Schedules_4split_2030_central.csv` |
| 14| sens_hotel_opt       | Y (central) | Y (central) | Y (opt) | Y (central) | `BEM_Schedules_4split_2030_central.csv` |

12 scenarios x 4 channels + Y2005/10/15 x 3 channels + Default_NECB x 0 = the 40/12/4 shape
reproduced exactly by the 56-cell `--dry-run` (§4 below).

### 3. Sensitivity-axis evidence — residential shares the office/WFH BAND axis (verified against
Step-7 source, not assumed)
Read `3J_docs_occ_nTemp/Leg3_4-split/Step7_docs/3rdJ_07_aug_to_bem_4split.py` end to end
(`BUNDLE_MAP`, `assemble_2030()`, the `--sens` build branches). Findings, file:line:
- `3rdJ_07_aug_to_bem_4split.py:358-359`: `assemble_2030(office_band, ...)` docstring — *"ported
  from Leg-2, keyed off the office/WFH BAND axis only"*. This is the ONLY function that produces
  the residential `BEM_Schedules_4split_2030_<bundle>.csv` product; its sole free parameter is
  `office_band`. There is no independent residential axis in the code.
- `3rdJ_07_aug_to_bem_4split.py:932`: block comment *"---- Residential + Office (share the
  office/WFH BAND axis) ----"* — the two products are built in the same code block, from the same
  `office_band` parameter.
- `3rdJ_07_aug_to_bem_4split.py:909-910` (default/no-`--sens` build): `chans = {"residential_office",
  "retail", "hotel"}` — residential and office are always members of the SAME channel set, never
  split.
- `3rdJ_07_aug_to_bem_4split.py:916-920` (`--sens office` build path): `chans = {"residential_office"}`;
  `office_states = [(b, off_central[b]["office_band"]) for b in ("cons", "opt")]` — for the office
  sensitivity, BOTH the residential file (for `office_band` in {conservative, fullyhybrid}) AND the
  office multiplier file are rebuilt together at :933-954, in the SAME branch.
- `3rdJ_07_aug_to_bem_4split.py:921-928` (`--sens retail` / `--sens hotel` build paths):
  `chans = {"retail"}` / `chans = {"hotel"}` ONLY — `"residential_office"` is absent from `chans`,
  so neither residential nor office is rebuilt for these axes; they remain at whatever the base
  (central/hybrid) run already produced.

Conclusion (matches the task brief's hypothesis): `sens_office_cons`/`sens_office_opt` swap
residential to the matching cons/opt bundle file alongside office (implemented in
`_build_scenarios()`, `sens_office_cons`/`sens_office_opt` blocks). `sens_retail_*`/`sens_hotel_*`
keep residential at `BEM_Schedules_4split_2030_central.csv` (implemented, same function). Verified
by inspection of the `--dry-run` output (§4) and the smoke-run manifest (§5): `sens_hotel_opt`'s
`channels_requested.residential.csv_path` resolves to `..._2030_central.csv`, not `..._opt.csv`.

### 4. Channel-completeness GATE — added, wired into `--dry-run`, fired and passed (verbatim)
Added `ALL_CHANNELS`, `DELIBERATE_CHANNEL_EXCEPTIONS`, `_expected_channels()`,
`validate_campaign_channels()` to `3rdJ_08D_campaign_cells.py`; called from inside
`build_campaign_cells()` right after the existing `assert len(cells) == 56` — so both
`3rdJ_08D_campaign_local.py` (`--dry-run` AND a real launch, which both call
`build_campaign_cells()` before doing anything else) and `3rdJ_08D_campaign_driver.py` (same) are
gated: there is no code path that reaches a built cell table without passing through this check
first. Only 2 documented exceptions: `Default_NECB` (no channels at all) and `Y2005`/`Y2010`/
`Y2015` (no `hotel` key). Any other scenario missing a channel from `{office, retail, hotel,
residential}` raises `AssertionError` naming the cell index, tag, scenario, missing channel(s), and
the full expected-vs-got sets.

**Fire demonstration** — temporarily stripped `"residential"` from the `Y2022` scenario's
`channels` dict (a 3-line reversible edit wrapping the existing `_bundle_channels(...)` call in a
dict comprehension that drops the `"residential"` key), ran `py -3 3rdJ_08D_campaign_cells.py`:

```
Traceback (most recent call last):
  File "...\3rdJ_08D_campaign_cells.py", line 455, in <module>
    cells = build_campaign_cells(REPO_ROOT)
  File "...\3rdJ_08D_campaign_cells.py", line 433, in build_campaign_cells
    assert not gate_failures, (
           ^^^^^^^^^^^^^^^^^
AssertionError: CHANNEL-COMPLETENESS GATE FAILED -- refusing to build the campaign table (defence in depth against a scenario silently missing a channel it is supposed to carry; see validate_campaign_channels()):
  cell 1 (Y2022__Tall__MTL): scenario 'Y2022' is missing channel(s) ['residential'] -- expected ['hotel', 'office', 'residential', 'retail'], got ['hotel', 'office', 'retail']
  cell 15 (Y2022__Tall__CLG): scenario 'Y2022' is missing channel(s) ['residential'] -- expected ['hotel', 'office', 'residential', 'retail'], got ['hotel', 'office', 'retail']
  cell 29 (Y2022__SuperTall__MTL): scenario 'Y2022' is missing channel(s) ['residential'] -- expected ['hotel', 'office', 'residential', 'retail'], got ['hotel', 'office', 'retail']
  cell 43 (Y2022__SuperTall__CLG): scenario 'Y2022' is missing channel(s) ['residential'] -- expected ['hotel', 'office', 'residential', 'retail'], got ['hotel', 'office', 'retail']
```
(exit code 1; correctly named all 4 Y2022 cells — one per building/city — since the defect was
introduced at the scenario level, upstream of the building/city loop.)

**Restore + pass demonstration** — reverted the 3-line edit, re-ran the same command:
```
built 56 cells against repo_root=C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main
cells with >=1 missing input: 0/56
```
(exit code 0; gate passed silently as part of `build_campaign_cells()`, no output of its own on
success by design — the "0/56 missing input" line is the pre-existing self-check's own output,
printed only because the gate didn't raise.)

### 5. 56-cell `--dry-run` (post-fix)
`py -3 3rdJ_08D_campaign_local.py --dry-run` — exit 0, 369 lines. Confirmed:
- `56 cell(s) printed, 0 with a missing input.` — every IDF/EPW/channel-CSV path referenced by
  every cell resolves on disk.
- Channel count per scenario (`grep`/`awk` over the dry-run output, 4 cells per scenario =
  2 buildings x 2 cities, matches expectation exactly):
  `Default_NECB`=0, `Y2022`=4, `B_cons`=4, `B_central`=4, `B_opt`=4, `Y2005`=3, `Y2010`=3,
  `Y2015`=3, `sens_office_cons`=4, `sens_office_opt`=4, `sens_retail_cons`=4, `sens_retail_opt`=4,
  `sens_hotel_cons`=4, `sens_hotel_opt`=4.
- Spot-checked `sens_office_cons__Tall__MTL` (cell 8) and `sens_office_opt__Tall__MTL` (cell 9) in
  the raw output: `channel residential` csv paths resolve to `BEM_Schedules_4split_2030_cons.csv`
  and `..._opt.csv` respectively (not `..._central.csv`) — the sensitivity-axis fix (§3) confirmed
  live in the actual cell table, not just in the source.

### 6. Smoke test — residential live, one cell
Ran `py -3 3rdJ_08D_campaign_local.py --cells 27 --workers 1 --smoke-days 2` (cell 27 =
`sens_hotel_opt__Tall__CLG`, residential channel present at `..._2030_central.csv` per §3/§5).
**Wall-clock: 50.9s** (PowerShell `Stopwatch`, includes Python startup + injection + EnergyPlus run
+ post-process; EnergyPlus's own reported run time was 33.03s). Exit 0.

Console evidence residential injection fired (`_logs/sens_hotel_opt__Tall__CLG.log`):
```
  [inject_residential] neutralized 1 SpaceList-level carrier PEOPLE object(s) referencing 'HighriseApartment Apartment' directly
  [inject_residential] 27 residential apartment Spaces <- 27 distinct households (seed=42), 54 Schedule:Compact objects created
  ...
  Injected residential: 27 apartment Spaces, 27 distinct households drawn, 1 SpaceList-level carrier(s) neutralized
```
`manifest.json`: `channels_requested.residential = {csv_path: ..."BEM_Schedules_4split_2030_
central.csv", csv_md5: "043e07271a500ab4f60809b1be2cb208", exists: true, seed: 42}`;
`inject_mixed_use_result.residential = {n_spaces: 27, n_households_drawn: 27,
n_carriers_neutralized: 1, assignment: {27 Space-name -> SIM_HH_ID pairs}}` — verified
programmatically that `len(assignment) == 27` and `len(set(assignment.values())) == 27`: 27
distinct households, no repeats, one per apartment Space, matching OD-8R-L3's no-replacement-draw
contract.

`channel_hourly.csv` (48 rows = `smoke-days 2` x 24h, matches `expected_rows`): `residential_people`
column non-zero and time-varying across all 48 hourly rows — min 19.0, max 70.0, 34 distinct
values (not a static baseline artifact): `[68.0, 68.0, 68.0, 68.0, 66.0, 70.0, 69.0, 64.0, 53.5,
46.5, 43.0, 43.0, 39.0, 29.0, 23.0, 30.0, 35.0, 48.5, 56.0, 62.0, 62.0, 61.0, 67.0, 68.0, 58.0,
58.0, 62.0, 62.0, 66.0, 66.0, 64.5, 60.0, 46.0, 34.0, 31.0, 19.0, 25.0, 24.0, 26.0, 27.0, 40.0,
41.0, 49.5, 54.0, 60.5, 61.0, 58.0, 58.0]`.

### 7. Compile check
`py -3 -m py_compile 3rdJ_08D_campaign_cells.py 3rdJ_08D_campaign_driver.py
3rdJ_08D_campaign_local.py` — clean, no errors.

### 8. Probe harness unaffected (strictly additive, proven)
`py -3 3rdJ_08P_probes_local.py --dry-run` re-run unchanged after all edits: still lists exactly 7
cells (`baseline_necb`, `B_central`, `var_office`, `var_retail`, `var_hotel`, `cycle_2022`,
`fallback_retail`), no residential channel present in any of them (probe harness scope is
unchanged by design — only the campaign driver/cell-table gained residential).

### 9. Files touched
- `3rdJ_08D_campaign_cells.py`: `_bundle_channels()`/`_historical_channels()` gained a
  `residential_csv` parameter; `RESIDENTIAL_SEED = 42` constant added; `_build_scenarios()` wires
  residential into all 13 non-`Default_NECB` scenarios (13 x `BEM_Schedules_4split_*.csv` paths,
  cons/opt swapped for `sens_office_*`, central for everything else per §3); new
  `ALL_CHANNELS`/`DELIBERATE_CHANNEL_EXCEPTIONS`/`_expected_channels()`/
  `validate_campaign_channels()` gate wired into `build_campaign_cells()`'s return path; module
  docstring updated (14-scenario table, sensitivity-axis evidence section).
- `3rdJ_08D_campaign_driver.py`: docstring only (the stale "residential is OUT" scope-boundary
  comment corrected — no code change, the driver already passed `cell["channels"]` through to
  `inject_mixed_use()` generically and needed no logic change for residential to arrive).
- Not touched: `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`,
  `eSim_dynamicML_mHead_alignment.py`, any Step-7 product CSV, `commercial_integration.py`,
  `3rdJ_08P_probe_driver.py`, `3rdJ_08P_probes_local.py`.

Co-Authored-By: Claude Sonnet 5 (employee session) <noreply@anthropic.com>

---

### 2026-07-30 (manager) — probes re-simulated on `_C_v2`, §P re-scored 32P/0W/0F, residential injector proven for the first time

Step-6 was re-opened and re-closed (bidirectional Stage B + weekend pooling); canonical 2030
deliverable is now `..._calibrated_mindwell_C_v2.csv` MD5 `5aa74f44` (predecessor `7c105ef3` kept
intact on disk — the pointer moved, never the file). Step-7 products rebuilt from it. Full decision
register in `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step5_6_7.md` (D-1…D-19).

**Correction to this log's own framing.** The §P scorecard closed at 25P/0W/0F on 2026-07-28 is
stale for **two independent reasons**, and "Step-7 changed `INJ_HASH`" is **not** one of them:
`INJ_HASH = md5(commercial_integration.py)[:8]` owns the output *path*; a product change moves
`INPUTS_HASH` only — that separation IS the Défaut-3 fix. What actually happened: (a) the injector
md5 moved `5670f602 → cf69d508` via the concurrent `classify_tag2()` residential fix (a **wiring**
change), and (b) the Step-7 2030 residential/office products changed. Cluster results stay under
`campaign_5670f602/`, the local re-run writes `campaign_cf69d508/` — paths self-separate, no
`--allow-stale-inputs` needed.

**Re-simulation + scorecard.** 7/7 cells `ok` exit=0, **27.7 min** total (12–18 min/cell, 6 workers,
watchdog armed, no memory event). **§P = 32P / 0W / 0F / 10 INFO.** The 7-point gain over the
cluster run is real: the **6 `INPUTS_HASH` gates** added by the Défaut-3 fix are exercised here for
the first time, plus one repaired gate.

**`P4 banner` — local-port gap, fixed and proven both ways.** It globbed `8P_probe_*_6.out`
(SLURM-only) unconditionally; the Windows orchestrator writes `<tag>.log`. The banner **was**
printed correctly (`_logs/fallback_retail.log:179`, with `office=6 retail=0 hotel=3;
fallback=['retail']`). Changed the **glob only** — the assertion is untouched, so no threshold was
relaxed (same distinction applied earlier to R.1/R.2/R.7: repairing what a gate *looks at* is
legitimate, moving what it *demands* is not). Seen PASS on the real log, seen **FAIL** with the
banner line removed, log then restored and md5 re-verified identical (`63f582aa…`).

**🔴 `inject_residential()` had never been executed — and this log's own smoke test masked it.**
Chased from the `P1 residential -- NOT EXERCISED` INFO line. Probes exclude residential **by
design** (`3rdJ_08P_probe_driver.py:12-14`), so `office=6 retail=0 hotel=3` in every probe cell is
correct — but it also means **the probe harness structurally cannot validate the channel that is
the subject of the research**. Compounding it: the end-to-end smoke test recorded above (`n_spaces`
office 6 / retail 3 / hotel 3, 20:41) **predates the residential wiring** in
`3rdJ_08D_campaign_cells.py` (20:51). That entry was accurate when written and stopped covering the
current code ten minutes later. The 56-run campaign would have been this code path's first
execution.

Verified before any long run (campaign smoke, 0.8 min): channels requested
`['office','retail','hotel','residential']`; residential **27 Spaces, 27 distinct households**
(seed 42 — one household per Space, per OD-8R-L3); **54** schedules
(`MXU_Residential_Occ/Met_HH<id>`); `n_carriers_neutralized=1` (2J Bug A per-zone carrier fix
live); `fallback=[]`, `ambiguous=[]`. **§B (residential injector) is CLOSED** — the "specified, not
implemented" status in `3rdJ_08_implementation_improvements.md` §B is superseded.

**§C also closed, via the consumed columns rather than md5** (Test-method #1). Historical products
read `step7.AUG` (the Step-5 observed frame filtered by `CYCLE_YEAR`), **never** the Step-6
calibrated deliverable — so `_C_v2` does not stale them. Era axis verified **alive on all three
channels**: office `AT_WORK_fraction` 143–144/144 bins differ (max|Δ| 0.052–0.092), retail
`multiplier` 154–156/288 (max|Δ| 0.458–0.758), residential `Occupancy_Schedule` **48/48** bins
(max|Δ| 0.046–0.095). Note the residential annual means agree to within 0.005 across eras — a check
on annual totals would have declared the axis dead. The era signal is in the **shape**.

**Open, for the user (not a blocker):** within the historical arm, 2005/2010/2015 are built from
`IS_SYNTHETIC == 0` pools (`3rdJ_08A_...py:228`, deliberate) while the **2022** product is built
from the **unfiltered** Step-5 stock. In the frame itself the synthetic share is flat (~44–45% on
all four cycles), so the `0% → 44.6% → 100%` ladder in Défaut 4 is a **filter choice**, not a
property of the data. Harmonising would make the era arm composition-homogeneous but would
invalidate the 2022 product, its freshly regenerated Step-7 report and the `cycle_2022` probe — a
method call, not a bug fix.

Next: one **full-annual Calgary cell** (CAN_CLG has never been exercised; 28 of 56 cells depend on
it), then the 56-run campaign. Open item #2 (Calgary EPW `_6B` vs IDF `Z7A`) is already settled
with numbers above — near-boundary NECB 6/7A case, file deliberately not renamed.

Files changed: `3rdJ_08P_probe_gates.py` (P4 glob only). Not touched: any Step-7 product CSV,
`commercial_integration.py`, `3rdJ_08P_probe_driver.py`, `3rdJ_08P_probes_local.py`,
`3rdJ_08D_campaign_*.py`, the Step-6 deliverables.

## Progress Log — 2026-07-30 (manager) : première cellule annuelle Calgary, campagne 56 runs lancée, D-20

**Ligne 11ter close.** Cellule 17 `B_central__Tall__CLG` — première exécution de l'IDF `CAN_CLG`
(28 des 56 cellules en dépendent) et premier run **annuel complet** de la campagne.
**6,6 min** (1 worker), `hourly_meters` et `channel_hourly` à **8760** lignes, `ep_return_code=0`,
EnergyPlus « Completed Successfully », **0 Severe**, `fallback=[]`, `ambiguous=[]`, `banner_lines=[]`,
4 canaux injectés (office 6 / retail 3 / hotel 3 / **résidentiel 27 Spaces, 27 ménages distincts**).

Deux points de méthode dans cette vérification :

1. **La tâche de fond est revenue avec un stdout VIDE malgré `exit=0`.** Le statut ne prouvait rien ;
   tout a été re-dérivé du manifeste et de `eplusout.err`.
2. **Le manifeste ne consigne pas le chemin EPW.** Une cellule `CLG` lancée par erreur avec le fichier
   météo de Montréal produirait un manifeste d'apparence identique. Seul le log ferme la question —
   `epw=…CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw`, périodes de dimensionnement
   « CALGARY-CANADIAN.OLYMPIC.PARK.UPPER ». **Amélioration à retenir : ajouter l'EPW au manifeste.**

**Le bandeau final annonce « 105 267 351 Warning ».** C'est le cumul *récurrent* d'EnergyPlus compté
par pas de temps, pas 105 M problèmes : le fichier ne contient que **478** lignes `** Warning **`
distinctes, dominées par du dimensionnement bénin (débit d'air minimal de zone 75,
`GetOAControllerInputs` 62, `CalcEquipmentFlowRates` 47, `SizeWaterCoil` 39). 0 Severe.

**Calgary n'est pas plus lente que Montréal.** 6,6 min seule vs 15,5–18,3 min/cellule à 6 workers
sur les probes → facteur de contention ≈ 2,7×, pas de surcoût climatique. L'hypothèse « même chiffre
pour CLG que pour MTL » de la doc est donc sûre et l'estimation 2,6–3,5 h tient.

### 🔴 D-20 — le canal résidentiel pilote les PERSONNES seulement

Trouvé dans les **colonnes** de `channel_hourly.csv`, pas dans le manifeste, qui est propre. Le
décompte de valeurs distinctes sur l'année trahit le câblage : office `nuniq(people)=nuniq(equip)=46`,
retail `37=37`, hotel 192/156 — signature d'un canal MODULATE. Résidentiel : people **33**, lights
**12**, equip **5**, c'est-à-dire les niveaux NECB de base. Confirmé à la source :
`inject_residential()` n'émet que des objets PEOPLE et son dict de retour n'a pas de clés
`n_lights` / `n_equip` (`eSim_bem_utils/commercial_integration.py:588`).

**C'est `OD-7D`, verrouillé et documenté** dans le docstring de la fonction, et la prémisse tient :
le produit résidentiel Step-7 est à **13 colonnes** (`Occupancy_Schedule`, `Metabolic_Rate`), et
**Leg-2 a le même schéma** — donc pas une régression entre jambes ; le « 17 colonnes » des vieilles
notes est de lignée 2J.

**Conséquence = réserve de manuscrit, pas correctif.** L'occupation commerciale atteint l'énergie par
**trois** voies (métabolique → CVC, éclairage, prises), la résidentielle par **une**. Toute
comparaison inter-canaux de la sensibilité énergétique à l'occupation est structurellement
défavorable au résidentiel — le sujet de la recherche. Les comparaisons **intra-canal** (bandes,
villes, époques) ne sont pas affectées : l'asymétrie y est en mode commun.

**Campagne 56 runs LANCÉE** — 6 workers, watchdog mémoire 80 %, reprise activée (55 à exécuter, la
cellule 17 réutilisée). Détail complet et registre de décisions dans
`improvements/3rdJ_L3_improvements_step5_6_7.md` (D-20, ligne 11ter, ligne 12).

### 2026-07-31 — 🔴 Défauts 5/6/7 : le jeu de sorties ne pouvait pas porter le §8E ni le Step 9 (CORRIGÉ, campagne re-simulée)

Trouvé en préparant le Step 9, **avant** que le moindre EUI n'ait été calculé — donc aucun résultat
publié n'est en cause. Détail complet et preuves dans `3rdJ_08_implementation_improvements.md`
(Défauts 5, 6, 7) ; résumé chronologique ici.

1. **Défaut 5 — 53,5 % de l'énergie de site rapportée à zéro.** `REQUIRED_METERS` demandait les noms
   d'avant EnergyPlus 9.4 (`Gas:Facility`, `Heating:Gas`, `InteriorEquipment:Gas`,
   `WaterSystems:Gas`), qui **n'existent plus** en 24.2. EnergyPlus a averti quatre fois
   (`eplusout.err:916-919`) ; le zéro-remplissage de `_write_hourly_meters_csv` a transformé
   « absent » en « 0,0 ». Le tableau *End Uses* du même run donne **13 884,91 GJ de gaz** (ECS
   7 726,75 + chauffage 4 082,08 + buanderie hôtel 2 076,08). Trois usages finaux électriques
   manquaient aussi (éclairage extérieur, rejet et récupération de chaleur = 1 388,64 GJ, soit les
   11,52 % d'écart de fermeture).
2. **Défaut 6 — variables de zone non multipliées.** Σ(variables de zone) = **25,4 %** du compteur
   d'installation ; `Σ(zone × Zones.Multiplier) / compteur = 1,000000`. Les multiplicateurs
   {1,4,7,8,9,10,28,70} diffèrent **par canal**, donc l'erreur ne s'annulait pas dans les parts.
3. **Défaut 7 — surfaces documentées fausses.** Tall mesuré : 72 623,1 m² (= ABUPS exactement),
   bureau 44,65 % / hôtel 24,91 % / résidentiel 22,40 % / **retail 5,53 %** de l'occupiable, contre
   « 24,4 % » pour trois canaux au document. Service/MEP 21,4 % du brut, pas ~52 %.

**Correctifs livrés.** 15 compteurs (2 totaux + 13 usages finaux) ; `Zones.Multiplier` appliqué à la
source ; `Zone Air System Sensible Cooling/Heating Energy` ajoutés (sans quoi la répartition horaire
pondérée par la charge de dr_L3-10 était incalculable), plus `Zone Gas Equipment NaturalGas Energy`
et `Water Use Equipment Heating Energy` → `dhw_hourly.csv` ; deux gates de fermeture (`fuel_closure`,
`channel_closure`) **vues échouer sur le vrai défaut** puis sur un manque injecté de 5 %, et passant
sur un jeu complet ; `OUTPUT_SCHEMA_HASH` intégré à l'empreinte de reprise (sans lui, corriger les
compteurs laissait les 56 cellules « faites » et la reprise les aurait sautées) ; échec de fermeture
= échec de **cellule**, visible dans `campaign_status.csv`.

**§8E écrit** (`3rdJ_08E_aggregate_4split.py`) — il n'existait pas ; il refuse d'agréger une cellule
dont les fermetures échouent. **Step 9 écrit** (`Step9_docs/3rdJ_09_activityDrivenLoads_4split.py`).

**Re-simulation** dans `campaign_local_v2/` (arbre précédent intact). Cellule témoin avant lancement :
0 compteur absent, `NaturalGas:Facility` = 13 884,9 GJ concordant avec *End Uses*, 5 fermetures à
0,000000 %, 47/47 équipements ECS résolus, et `Electricity:Facility` **identique** au run précédent —
contrôle de régression : ajouter des objets `Output:*` ne perturbe pas le modèle. Coût : 7,1 min/cellule
contre 6,6, soit ~8 %.

**La leçon, à garder.** La gate §6b-4 (« Σ compteurs d'usage final ≈ `Electricity:Facility` ») était
écrite depuis 2J Bug B et **jamais implémentée**. Une gate déclarée dans un document et absente du
code est pire qu'une gate manquante : elle occupe la place de celle qui aurait attrapé le défaut.
