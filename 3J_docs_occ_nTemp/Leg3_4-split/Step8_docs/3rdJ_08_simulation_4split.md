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
