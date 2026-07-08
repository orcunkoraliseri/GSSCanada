# Step 8 — Apartment Cooling-Setpoint Fix: Implementation Plan (3J Leg-2, 2-split)

**Authored:** 2026-07-07 · **Status:** **FIX v3 VERIFIED LOCALLY (2026-07-08) — gate 4.9 = WARN not FAIL, as expected.** Speed cluster unavailable ~2 weeks from 2026-07-08; the two cluster jobs (extractor 1070074, validator 1070077) were cancelled and the same gate re-verified locally via a scoped 600-run subset. TRUE root cause found (investigation **§11**): the winter "cooling" is a **metering artifact** — `Cooling:EnergyTransfer` sums `Zone Air System Sensible Cooling Energy`, which counts cold ERV ventilation air (one thermostat-independent `ZoneHVAC:EnergyRecoveryVentilator` per apartment unit: 24 MidRise / 46 HighRise) as "cooling" at zero electricity. Mechanism A retired; no model change needed. Fix v3 = revert the v2 injector override + re-base §4/gate-4.9 on end-use energy (Cooling Electricity vs Heating fuel) via **re-aggregation of the persisted `eplusout.sql` files — NO re-simulation**. See "Fix v3" section below. History: v1 (IDF template patch) bypassed by injector; v2 (injector override) smoke-falsified across 24/28/40°C — which is what exposed the artifact.
**Basis:** `step8_resid_heating_cooling_dominance_investigation.md` (diagnosis independently
verified §7; Mechanism A directly confirmed by winter-cooling probe §8.1). Implements fix
**option 1** (seasonal cooling-setpoint relief) + **option 3** (heat-vs-cool dominance gate).
Fix **option 2** (per-CZ envelopes, Mechanism B) is explicitly **deferred** — recorded as a
paper limitation, not fixed here.

---

## Which pipeline step repeats (and which do not)

Per `3rdJ_00_2split_Occupancy_Pipeline_Overview.md`, Steps 1–7 are the **occupancy channel**
(GSS → schedules). The defect lives in the static residential prototype IDFs consumed only at
**Step 8** (`resolve_cell()` → `STEP8_BUILDINGS_DIR`); Step 7 writes schedule CSVs only (zero
`.idf` references, verified). Therefore:

| Step | Action |
|---|---|
| 1–7 (incl. 8A historical schedules) | **NOT repeated** — occupancy inputs unchanged, bit-identical |
| **8B residential campaign** | **REPEAT — subset only**: MidRise + HighRise = array indices **84–167** (84 cells = 2 arch × 6 cities × 7 scenarios × N=50 = **4,200 runs**). SingleD/OtherDwelling (indices 0–83) and the office campaign (252 runs) untouched. |
| 8D aggregation | REPEAT (full `--rebuild` — cheap, reads all runs) |
| 8E validation | REPEAT (with the new 4.9 dominance gate) |
| 9 end-use report | REPEAT (resid EUI/end-use tables shift) |

Paired-MC design is preserved automatically: the per-(arch×city) HH sampling is deterministic
(`--seed 42`), so the re-run regenerates the **same 50 HH IDs per cell**.

---

## Aim

Stop the MidRise/HighRise apartment prototypes calling mechanical cooling through the Canadian
winter (frozen year-round 24.0 °C cooling setpoint), re-simulate the affected half of the
residential campaign, and add a validator gate so heat/cool dominance regressions can never
again pass silently. Do it **without touching the shared 2J templates** (2J is submission-ready).

**NOT changed:** internal-load densities (2.15 W/m² lights, 5.0 W/m² equip — standard
ASHRAE-prototype values; lowering them would shift lights/equip electricity and EUI everywhere),
heating setpoint schedule, house IDFs, office channel, occupancy schedules.

---

## Phase 0 — winter cooling-relief value — RESOLVED: **1a**

Decision delegated to manager by user 2026-07-07; **1a chosen** (the recommendation). 1b
remains the pre-authorized fallback if the Phase-4 smoke gate fails — no further user
decision needed mid-run.

- **1a (CHOSEN):** seasonal 3-block schedule — `Through: 4/30` → **28.0 °C**,
  `Through: 9/30` → 24.0 °C (cooling season unchanged), `Through: 12/31` → **28.0 °C**.
  Residual winter cooling only if internal+solar gains push a zone past 28 °C — plausible
  comfort cooling in core zones, not a thermostat artifact.
- **1b (pre-authorized fallback):** full winter lockout (shoulder/winter blocks at 40.0 °C ≈
  cooling off). Escalate to this only if the Phase-4 smoke test still shows material DJF
  cooling under 1a (gate: DJF cooling < 10% of pre-fix values).

Day-type structure (Weekdays/Saturday/Sunday/design-days) is kept identical to the original
object; only the seasonal `Through:` split and winter values change.

---

## Steps

### Phase 1 — build the patched IDF set (local)
1. New dir `Step8_docs/Buildings_MTL_v242_3Jfix/`: copy all 4 residential IDFs from
   `2J_docs_occ_nTemp/BEM_setup/Buildings_MTL_v242/` (single-dir contract of `_find_one()`;
   houses stay byte-identical, the two `ASHRAE901_Apartment*` get patched).
2. Patch script `investigation/patch_apartment_cooling_setpoint.py`: text-level replacement of
   the one `Schedule:Compact, NECB-G-Thermostat Setpoint-Cooling` object (bounded header→`;`)
   in both apartment IDFs — text-level, not eppy, so the diff stays minimal and reviewable.
3. Verify: (a) grep spot-check per investigation §6 (`grep -A5 "NECB-G-Thermostat
   Setpoint-Cooling"` shows the seasonal blocks); (b) diff confirms ONLY that object changed in
   the apartments; (c) hash-compare confirms the 2 house IDFs are byte-identical to 2J's.

### Phase 2 — point 3J at the patched set (local, one line)
4. `eSim_bem_utils_3J/main.py:82` → `STEP8_BUILDINGS_DIR = .../Step8_docs/Buildings_MTL_v242_3Jfix`
   (+ comment citing this plan). Archive predecessor as
   `archive/main.20260707_preCoolfix.py` per repo convention. 2J's `main.py` untouched.

### Phase 3 — validator dominance gate, option 3 (local)
5. Archive `3rdJ_08_simulation_2split_val.py` predecessor, then extend `_gate_enduse_split()`
   with **gate 4.9-heat-dominance** (per-archetype, heating-dominated CZs 6A/6B/7A, from
   `agg_annual`): per archetype × CZ compute cooling_kWh / heating_kWh —
   **FAIL if ratio > 2.0 in 7A**, **WARN if ratio > 1.25 in any of 6A/6B/7A**. Unlike 4.6/4.7
   (PASS/WARN-only), this gate CAN fail — that is the point.

### Phase 4 — smoke test before committing to 4,200 runs (cluster, sbatch)
6. Upload `Buildings_MTL_v242_3Jfix/` + edited `main.py` to the scratch upload tree.
7. Two sbatch smoke jobs (`-t 7-00:00:00`, single-line `--wrap`), `--n 2`, out-dir
   `$SCRATCH/campaign_smoke`: `--arch MidRise --city Winnipeg_7A --scenario 2022` and the same
   for HighRise. (~4 E+ runs, minutes of compute.)
8. Pull the 4 `hourly_meters.csv` local (scp) and run `probe_winter_cooling.py` against them.
   **Gate to proceed:** DJF cooling collapses (target ≈ 0; accept < 10% of the pre-fix DJF
   values: MidRise 16,474 / HighRise 34,126 kWh) AND annual heating rises. If DJF cooling is
   still material → switch to Phase-0 option 1b and repeat the smoke.

### Phase 5 — full subset re-simulation (cluster)
9. Preserve pre-fix outputs for provenance (rename, don't delete):
   `mv $SCRATCH/campaign/MidRise__* $SCRATCH/campaign_precoolfix/` (idem `HighRise__*`).
   This also guarantees a clean re-run (no stale-mix with `cell_is_done`).
10. Submit a copy of `run_residential_array.sh` edited to `#SBATCH --array=84-167`
    (decode: `arch_idx = idx // 42` → MidRise 84–125, HighRise 126–167; everything else —
    seed 42, N=50, paths, SIF wrapper — unchanged). 84 tasks × 50 runs = 4,200 sims.
    Queue is currently saturated (`AssocGrpCpuLimit`) — expect a slow crawl; fire-and-forget.

### Phase 6 — downstream refresh (cluster, then sync local)
11. `run_aggregation.sh` with `--rebuild` (8D) → new `agg_*.csv`.
12. `run_validation.sh` (8E) → new scorecard incl. gate 4.9; then the Step-9 report job.
13. Re-run the winter probe on 5 fresh CZ7A samples per apartment archetype at campaign scale
    (same scp-down-and-run-locally pattern as §8) — belt-and-braces confirmation.
14. scp reports + agg CSVs local; archive predecessor HTMLs per convention.

### Phase 7 — documentation
15. Progress Logs: this plan, the investigation doc (§4 option-1 → APPLIED), Step-8/Step-9
    status docs, acceptance-review addendum (the "PAPER-READY, 0 FAIL" verdict predates this
    fix — re-affirm or amend). Update paper-facing numbers: §4 end-use shares, apartment EUI,
    any 2030 paired-delta magnitudes that shift.

---

## Expected result

- CZ7A apartment cooling/heating ratio drops from 5.3×/9.8× to **O(1)** (SingleD-like, per
  investigation §6 target); DJF apartment cooling ≈ 0; apartment annual heating rises from the
  implausible 5–9 kWh/m²/yr toward physically credible values (still Z6-envelope-limited —
  Mechanism B deferred).
- Scorecard: 0 FAIL including new gate 4.9; gates 4.6/4.7 still PASS; office gates unchanged.
- Houses (SingleD/OtherDwelling) bit-identical results — their runs are not repeated.
- §6 2022→2030 deltas re-checked: occupancy-signal direction expected unchanged, magnitudes may
  shift for apartment cells.

## Test method

Phase-gated, cheapest-first: Phase 1 = grep/diff/hash on IDFs; Phase 4 = 4-run smoke + probe
(hard gate before the 4,200-run spend); Phase 6 = before/after per-CZ×archetype heat/cool
table (investigation §1 vs new agg), full scorecard, campaign-scale probe re-run. If any
Phase-6 §4 benchmark gate (SHEU/EUI bands) newly FAILs, stop and report before touching docs —
that would be new information about the fix, not a doc task.

## Out of scope (recorded, not silently dropped)

- **Mechanism B** (one Z6 envelope for all 6 CZs) — deferred; cite as limitation.
- **OtherDwelling 1.6× skew** — borderline; monitored by new gate 4.9 (WARN band), no re-sim.
- **Office end-use meters** (gate 4.8-office INFO) — separate task, unchanged here.

## Risks

- §4 benchmark-band gates may shift as apartment EUI recomposes (more heat, less cool) —
  handled by the Phase-6 stop rule.
- Paper text citing pre-fix §4/§6 numbers must be re-cited after Phase 7.
- 2J/3J divergence: after this fix the two pipelines intentionally use different apartment
  IDFs — the new `_3Jfix` dir name and this plan are the provenance trail.

---

## Fix v2 — injector-level seasonal cooling override (2026-07-08, manager design review)

**Why v2 exists:** v1 (Phases 1–2 above, IDF-template patch) failed its smoke test — the patched
static schedule never reaches the simulation because `inject_setpoint_schedules()` in
`eSim_bem_utils_3J/integration.py` collapses whatever schedule it reads into one flat year-round
constant (full mechanism: investigation doc §9). The operative fix must therefore live in the
injector itself. Phases 3–7 of the original plan (gate 4.9, smoke gate, subset re-sim, downstream
refresh, docs) remain valid as written; only the *fix mechanism* (Phases 1–2) is superseded.

**Decision:** investigation §9.1 **option 2** (narrow opt-in override — the lean pick), with one
improvement over the sketch: instead of hand-rolling multi-`Through:` logic in
`_compact_setpoint()`, reuse the **existing `create_monthly_compact_schedule()` helper**
(`integration.py:592`), which already emits per-month `Through:` blocks in **Schedule:Compact**
and is already exercised at 3 lighting call sites (lines 1681/1799/2194+). This keeps option 3's
"reuse existing machinery" benefit *without* its downside (no Schedule:Compact → Schedule:File
delivery-mechanism change). Options 1 and 3 rejected for this cycle: option 1 rewrites the shared
path every archetype traverses (would force re-validating houses too); option 3 changes how
setpoints are delivered to E+, a mechanism never exercised for setpoints in this campaign.

### v2 mechanism (all changes in `eSim_bem_utils_3J/integration.py` only)

1. **Gating — in `inject_schedules()` (~line 1996 call site).** Detect the apartment archetypes
   from `os.path.basename(idf_path)` (case-insensitive substring `ApartmentMidRise` /
   `ApartmentHighRise` — matches the two ASHRAE 90.1 prototype filenames). When matched, pass a
   `cooling_seasonal_override` dict into `inject_setpoint_schedules()` and print a
   `[CoolFix] seasonal cooling override active (winter SP 28.0C, Oct–Apr)` provenance line into
   the run log. Filename gating (rather than plumbing a param through `main.py` /
   `3rdJ_08B_run_paired_mc.py`) means every code path that injects into an apartment IDF —
   campaign, smoke, one-offs — gets the fix uniformly, and NO file outside `integration.py`
   changes. Config lives in module-level constants near the top of the file
   (`COOLFIX_ARCH_SUBSTRINGS`, `COOLFIX_WINTER_COOL_SP = 28.0`, `COOLFIX_WINTER_MONTHS =
   {Jan,Feb,Mar,Apr,Oct,Nov,Dec}`) so the pre-authorized 1b fallback is a one-constant change
   (28.0 → 40.0).
2. **Schedule build — in `inject_setpoint_schedules()` (~line 1112).** New optional param
   `cooling_seasonal_override=None`. When `None` → behavior byte-identical to today (houses and
   any other archetype untouched — zero regression surface). When set (variant 1a semantics):
   the **cooling** schedule is built via `create_monthly_compact_schedule(new_cool_name,
   'Temperature', monthly)` where:
   - **Winter months (Jan–Apr, Oct–Dec):** flat **28.0** every hour, both Weekday and Weekend
     patterns. NOTE deliberately NOT "28.0 occupied / 27.0 absent" — the absence setback (27.0)
     must never sit *below* the seasonal relief value or absence would *increase* cooling;
     winter value = `max(COOLFIX_WINTER_COOL_SP, cooling_setback)` = 28.0 flat.
   - **Summer months (May–Sep):** exactly today's occupancy logic — active setpoint read from
     the template (`_read_constant_from_schedule` → 24.0) during occupied hours, 27.0 setback
     during absent hours, weekday/weekend from the same `_build_setpoint_schedule()` output as
     now. Cooling season unchanged, as Phase-0 variant 1a requires.
   - The **heating** schedule path is completely untouched (still `_compact_setpoint`).
3. **Guard.** `cooling_seasonal_override` combined with `use_schedule_file=True` → raise
   `ValueError`. The campaign runs the Schedule:Compact path (confirmed from the smoke `in.idf`);
   if anyone later flips to Schedule:File the fix must fail loudly, not silently drop.
4. **Autosizing.** `create_monthly_compact_schedule` assigns `SummerDesignDay WinterDesignDay`
   the Weekday pattern of the containing month: the summer design day (July) lands in a summer
   block → same 24.0/27.0 pattern as today → **cooling autosizing unchanged**; the winter design
   day sees cooling SP 28.0, irrelevant to heating sizing (heating schedule untouched). This
   removes v1's design-day-pinning problem entirely — no design-day fields are forced anywhere.

### v1 artifacts — keep, don't revert

`Buildings_MTL_v242_3Jfix/` + the `STEP8_BUILDINGS_DIR` repoint + gate 4.9 all stay. The template
patch is inert w.r.t. the thermostat (the injector replaces the schedule reference on every
DualSetpoint) but keeps the static template seasonally consistent with what gets injected, and
`_read_constant_from_schedule` still resolves the summer active SP to 24.0 from the patched file
(its design-day fields are pinned at 24.0 and sit last). Reverting would only churn the cluster
upload tree for zero behavioral difference. Gate 4.9 (Phase 3) is unchanged and still wanted.

### v2 verification ladder (cheapest first — step 1 would have caught v1 before any sim)

1. **Static injection check (new, locally):** small verify script generates one MidRise `in.idf`
   and one DetachedHouse `in.idf` through the normal `inject_schedules()` path. MidRise
   `CoolSP_HH_*` must show per-month `Through:` blocks — 28.0 all hours in winter months,
   24.0/27.0 occupancy pattern in summer months; `HeatSP_HH_*` single-block, unchanged.
   DetachedHouse `CoolSP_HH_*` must be the same flat single-block form as today (no-op proof).
2. **Local 4-run smoke** (2 MidRise + 2 HighRise, Winnipeg_7A, 2022, `--n 2 --seed 42`,
   fresh out-dir `campaign_smoke_v2` — do not mix with the failed v1 smoke outputs), then
   `probe_winter_cooling.py`. **Same gate as v1:** DJF cooling < 10% of pre-fix
   (MidRise 16,474 / HighRise 34,126 kWh) AND annual heating up AND no E+ severe/fatal.
   Run locally per user instruction (cluster queue saturated); light attended job (~3 min/run).
3. **Fallback 1b (pre-authorized, once):** if the smoke gate fails, set
   `COOLFIX_WINTER_COOL_SP = 40.0` (winter lockout) and repeat steps 1–2 once. If that also
   fails → STOP, manager re-diagnoses.
4. On smoke PASS: scp `integration.py` to the cluster upload tree, then Phase 5 (array 84–167,
   4,200 runs) → Phase 6 → Phase 7 exactly as originally written.

### v2 execution result — BOTH variants FAILED smoke (2026-07-08)

Phases A (injector code) and B (static injection check) executed and PASSed cleanly — the injected
`CoolSP_HH_*` schedules were independently verified correct (per-month `Through:` blocks, winter
flat at the live constant, summer unchanged) for both candidate winter setpoints. Phase C (4-run
local smoke) then FAILED for both:

| Variant | Winter SP | MidRise DJF cool | HighRise DJF cool | Gate (<10% of pre-fix) |
|---|---|---|---|---|
| pre-fix | 24.0°C | 16,474 kWh | 34,126 kWh | — |
| 1a | 28.0°C | 17,084 kWh (104%) | 34,157 kWh (100%) | FAIL |
| 1b (fallback, pre-authorized) | 40.0°C | 16,984 kWh (103%) | 34,157 kWh (100%) | FAIL |

0 Severe/Fatal across all 8 EnergyPlus runs. DJF cooling is statistically unchanged across three
different winter setpoints (24/28/40°C) despite confirmed-correct injection each time — the zone
`ThermostatSetpoint:DualSetpoint` cooling schedule this fix edits is **not the actual driver** of
the winter `Cooling:EnergyTransfer` total for these two archetypes. Full diagnosis, root-cause
discussion, and the unconfirmed DOAS/ventilation-coil lead: `step8_resid_heating_cooling_dominance_investigation.md`
§10. Per the runbook's stop rule (step 3 above), no further variant was attempted, Phase 5+ (cluster
upload, array submission) was **not** entered. `integration.py` currently has the full
`cooling_seasonal_override` mechanism wired end-to-end, with `COOLFIX_WINTER_COOL_SP` left at 40.0
(last-tested) locally — not uploaded to the cluster. Smoke evidence preserved in
`outputs_step8/campaign_smoke_v2/` (1a) and `outputs_step8/campaign_smoke_v2_1b/` (1b).

---

## Fix v3 — metric re-base (metering artifact; NO re-simulation) — READY (2026-07-08)

**Basis:** investigation §11 (read it first). `Cooling:EnergyTransfer` = Σ `Zone Air System
Sensible Cooling Energy` per zone (proven from `eplusout.mtd`) — net air-system sensible cooling
from ANY source. Each apartment unit has a thermostat-independent ERV; its post-heat-recovery
supply air is below room temperature all winter in cold CZs and is metered as "cooling" with the
compressor off. The §4 dominance anomaly is therefore a **metric choice problem, not a model
problem**: the fix acts on aggregation + validation only. The existing 25,200 campaign runs stay
valid; every run dir persists `eplusout.sql` (runner-guaranteed) whose `TabularDataWithStrings`
carries the annual ABUPS End Uses table (verified locally on the v2 smoke outputs: Cooling
Electricity 136.12 GJ / Heating Natural Gas 78.34 GJ for MidRise sample_001, Winnipeg 2022).

### Phase V3-A — revert the v2 injector override (local)

The v2 `cooling_seasonal_override` premise is falsified AND it is not harmless: the 40.0 lockout
measurably changed real shoulder-season compressor energy (annual cooling elec 136.12 → 118.48 GJ,
1a → 1b). It must not leak into any future run.

1. Archive current `eSim_bem_utils_3J/integration.py` → `archive/integration.20260708_coolfixInjector_v2_falsified.py`.
2. Restore `eSim_bem_utils_3J/integration.py` from `archive/integration.20260708_preCoolfixInjector.py`.
3. Verify: `py_compile` OK; `grep -c cooling_seasonal_override` = 0; restored file byte-identical
   to the pre-fix archive (hash compare).

v1 artifacts stay as-is: `Buildings_MTL_v242_3Jfix/` + the `STEP8_BUILDINGS_DIR` repoint are
runtime-inert (the injector rebuilds thermostat schedules from the last numeric field = 24.0 either
way) and are kept for provenance. Gate 4.9 is re-based in Phase V3-D, not removed. 2J untouched.

### Phase V3-B — cluster retention spot-check (login-safe, one `ls`)

Single command on the cluster: `ls` ONE campaign run dir (e.g. first sample of
`MidRise__Winnipeg_7A`, scenario 2022) and confirm `eplusout.sql` is present (expected — runner
persists it by design; `eplustbl.csv` may also be there but is not required). If the sql files are
missing, STOP and report — fallback is a subset re-sim with added `Output:Meter` objects, a
separate decision.

### Phase V3-C — End-Uses extractor (author local, run on cluster via sbatch)

New `investigation/extract_enduse_annual.py`, **stdlib-only** (os/glob/csv/sqlite3 — no pandas, no
env dependency). Walk `<campaign>/<cell>/sample_*/<year>/eplusout.sql`; per run query:

```sql
SELECT RowName, ColumnName, Value FROM TabularDataWithStrings
WHERE ReportName='AnnualBuildingUtilityPerformanceSummary'
  AND TableName='End Uses' AND RowName IN ('Heating','Cooling')
```

(query verified locally against a v2 smoke sql). Output one row per run to `agg_enduse_annual.csv`
(written next to the existing 8D agg tables): `cell, arch, city, cz, scenario, sample, hh_id,
heating_gas_GJ, heating_elec_GJ, cooling_elec_GJ, cooling_gas_GJ, heating_district_GJ,
cooling_district_GJ` (cz parsed from the city suffix; sample/hh_id from the dir name). Skip-and-log
unreadable sql files, print a `total dirs / parsed / skipped` tally. Submit via `sbatch` (7-day
walltime, fire-and-forget). ~25,200 sql files, IO-bound, minutes on a compute node.

Sanity gates on the output (checked next session or via the job log): row count ≈ number of run
dirs; heating fuel > 0 for every 7A residential run; cooling_elec > 0 for apartment runs;
MidRise__Winnipeg_7A 2022 cooling_elec in the ~100–180 GJ/run ballpark (smoke HH showed 136).

### Phase V3-D — validator re-base (edit local, upload, run on cluster)

Archive `3rdJ_08_simulation_2split_val.py` (dated), then:

1. **Gate 4.9-heat-dominance re-based**: read `agg_enduse_annual.csv`; ratio =
   `cooling_elec / (heating_gas + heating_elec + heating_district)` (site energy, GJ), per
   archetype × CZ 6A/6B/7A. Thresholds unchanged (FAIL > 2.0 in 7A, WARN > 1.25 in 6A/6B/7A).
   Expected outcome per the smoke evidence: MidRise 7A ≈ 1.7 → **WARN, not FAIL** — genuine
   prototype characteristic (dense ASHRAE internal gains + tight STD2022 envelope + ERV heat
   recovery), to be recorded as a paper-framing note.
2. **§4 report**: add an end-use table (heating fuel vs cooling electricity by archetype × CZ) from
   the new csv; relabel the existing ET-based rows as "air-system delivered sensible energy (incl.
   ventilation air)" so the two metrics can't be conflated again.
3. Upload, then submit the validator via `sbatch --dependency=afterok:<extractor job id>` so both
   run unattended in one submission pass. No polling.

### Phase V3-E — documentation + downstream

Progress Log rows here + investigation doc; after jobs finish (next session, user relays): scp
report + csv down, verify gates, refresh the acceptance-review addendum and any paper numbers that
cited ET-based cooling. **2J**: same artifact, same fix shape (re-aggregation only — its templates
were never broken); sequenced separately after 3J verifies.

### Out of scope (unchanged)

Mechanism B (single Z6 envelope) = paper limitation; prototype internal-gain cooling-heaviness
(~1.7× site energy in 7A) = paper framing, not a bug; office/houses aggregation untouched except
the shared §4 relabel.

---

## Progress Log

| 2026-07-08 (merged report — no plots lost) | User caught that `step8_validation_report_v3_section4_local.html` was missing every other section's plots (longitudinal trajectory, paired-Δ, seasonal diurnal, IDF round-trip, etc.) — correctly flagged as unacceptable data loss. Root cause: `--section 4` only runs `section4()`, so `write_html()` only ever had §4's gates/charts to render; sections 0/1/2/3/5/6/7 were never executed in that local session, not deleted. Rather than re-run the full validator locally (which would inject spurious §1 completeness FAILs — we only have a 600-run local subset, not the full 8,400+252-run campaign), pulled the **still-intact** last full real report straight off the cluster (`outputs_step8/step8_validation_report.html`, timestamp 2026-07-07 16:56 = job 1069196's output, confirmed untouched since the cancelled fix-v3 jobs never actually executed) as `outputs_step8/step8_validation_report_v3_full_baseline.html`. Wrote `investigation/merge_v3_section4_into_baseline.py` (stdlib `re`, exploits the validator's fixed per-section `<div id='sN'>` structure) to splice only the corrected §4 block (gate table + all 3 charts) and its §8-master-table rows into the baseline, recomputing the top-level scorecard tally (baseline counts − old §4 counts + new §4 counts) rather than leaving stale numbers. Verified: exactly one `id='sN'` div per section (0–8, no duplication), old inflated SingleD figure (908130.1) absent, corrected figure (958.1) present, gate 4.9/4.10 present, image count 15→16 (2 old §4 charts replaced by 3 new ones, all 13 other-section charts untouched). **Final scorecard: 50 PASS / 2 WARN / 17 INFO / 0 FAIL** (up from 50/1/16/0 — the +1 WARN is gate 4.9, the +1 INFO is gate 4.10; nothing else changed). Output: `outputs_step8/step8_validation_report_v3_merged.html` — this, not the section4-only file, is now the report to reference locally. | **MERGED REPORT COMPLETE — 50P/2W/17I/0F, all plots present, nothing lost** | `step8_validation_report_v3_full_baseline.html` (untouched cluster copy) and `step8_validation_report_v3_section4_local.html` (the raw §4-only patch source) kept alongside for provenance; `merge_v3_section4_into_baseline.py` is a one-off tool tailored to this validator's HTML structure, not a general merger — re-derive rather than reuse if the write_html() layout changes. |
| 2026-07-08 (chart + unit-bug follow-up) | User reviewed `step8_validation_report_v3_section4_local.html` and flagged cooling still looked much higher than heating. Root cause: the *existing* §4 chart (`_plot_enduse_split`, from the report-improvements item 2.3) plots `heating_ET_kWh`/`cooling_ET_kWh` from `agg_annual.csv` — the same ERV-contaminated air-system meter that gate 4.9 was re-based away from — so it never got the Fix v3 correction. Fixed by: (1) relabeling `_plot_enduse_split`'s axis/title to "air-system delivered sensible energy (incl. ventilation air)" so it's not mistaken for an end-use comparison; (2) adding a new companion chart `_plot_enduse_energy_split()` (heating fuel vs cooling electricity by archetype×CZ from `agg_enduse_annual.csv`) wired into the 4.9/4.10 gate block — this is the chart that should be cited for any heating/cooling-dominance claim. Archived predecessor first: `archive/3rdJ_08_simulation_2split_val.20260708_preV3plot.py`. **Also found and fixed a second, independent bug** while building this: both End-Uses extractors (`extract_enduse_annual.py` sqlite path, `extract_enduse_annual_from_tbl.py` csv path) assumed every archetype reports in GJ, but `OutputControl:Table:Style` differs by archetype family — SingleD/OtherDwelling (house prototypes) report in **kBtu**, MidRise/HighRise (apartment prototypes) in **GJ** — confirmed by diffing `eplustbl.csv` headers. Treating kBtu as GJ had inflated SingleD/OtherDwelling's absolute 4.10-table GJ figures ~950× (e.g. true 18.1 GJ heating misread as "18,137 GJ"); **the gate-4.9 ratio itself was unaffected** since the same bug scaled both heating and cooling for a given run identically, canceling out of the ratio. Both extractors now read the unit (`Units` column in sqlite; `[GJ]`/`[kBtu]` header suffix in csv) and convert to GJ. Re-ran the local 600-row extraction + `py 3rdJ_08_simulation_2split_val.py --section 4` after both fixes: same scorecard (7 PASS/2 WARN/4 INFO/0 FAIL, gate 4.9 still WARN with identical ratios), but 4.10's absolute GJ figures are now correct for all 4 archetypes, and the regenerated `step8_validation_report_v3_section4_local.html` has 3 charts embedded (EUI bands, relabeled ET-split, new true-end-use-energy split). Full narrative + before/after numbers: `step8_validation_report_improvements.md` (2026-07-08 entry) and investigation doc §12. | **CHART + UNIT BUG FIXED — verdict unchanged (WARN), absolute figures now correct** | Same outstanding item as before: canonical full-campaign HTML (all sections) still needs regeneration once the cluster is reachable, now also picking up the corrected extractor + new chart. |
| 2026-07-08 (V3-C/D re-run LOCALLY — Speed cluster unavailable ~2wks) | User: Speed cluster will be unavailable for a couple of weeks starting 2026-07-08 — cancelled both queued jobs (`scancel 1070074 1070077`, confirmed gone from `squeue`) and re-ran V3-C/V3-D entirely locally instead. Downloading the full campaign's `eplusout.sql` (41MB × 8,400 resid runs ≈ 345 GB) was infeasible, so scoped to exactly what gate 4.9 needs: scenario 2022, archetypes SingleD/MidRise/OtherDwelling/HighRise, CZ 6A/6B/7A (Montreal/Calgary/Winnipeg) — confirmed via `ls` counts this is N_MC=50 samples × 4 arch × 3 CZ = 600 runs. `eplustbl.csv` (the per-run annual-tables CSV EnergyPlus already writes) carries the identical End-Uses numbers as the sqlite query at a fraction of the size (~1.7MB vs 41MB). Bundled the 600 matching `eplustbl.csv` files into one tar on the login node (one-shot I/O op, not a lingering compute process — completed in seconds) and scp'd the single 600MB archive down instead of ~2,981-3,000 individual transfers, extracted locally into `outputs_step8/campaign_subset_v3_enduse/`. Authored `investigation/extract_enduse_annual_from_tbl.py` (local variant of the V3-C extractor: parses the eplustbl.csv "End Uses" table instead of querying eplusout.sql via sqlite3, same output schema) — dry-run against `campaign_smoke_v2/` gave an **exact match** to the sqlite-based extractor (MidRise sample_001 2022: heating_gas_GJ=78.34, cooling_elec_GJ=136.12). Ran it against the full 600-file subset → `dirs=600 parsed=600 skipped=0`, wrote `outputs_step8/agg/agg_enduse_annual.csv`. Ran the validator locally scoped to just the re-based section (`py 3rdJ_08_simulation_2split_val.py --section 4` — section4() only reads the `agg/` CSVs, not `STEP8_CAMP_DIR`, so no need to fake full-campaign presence locally): **Scorecard 7 PASS / 2 WARN / 4 INFO / 0 FAIL for §4.** Gate **4.9-heat-dominance = WARN, not FAIL** — CZ 7A (Winnipeg) ratios are all well under 1 (SingleD 0.20x, MidRise 0.67x, OtherDwelling 0.33x, HighRise 0.71x — heating properly dominates in the coldest zone, confirming the metering-artifact diagnosis); the WARN trigger is MidRise/HighRise in the milder 6A/6B zones (Montreal/Calgary) at 1.39–1.76x, a plausible prototype characteristic, not a regression. New gate 4.10 (end-use HTML table, heating fuel vs cooling electricity by archetype × CZ) renders correctly. The validator run overwrote `step8_validation_report.html` with this §4-only partial report (other sections never ran); renamed it to `step8_validation_report_v3_section4_local.html` so it isn't mistaken for the canonical full-campaign report (46P/1W/13I/0F, job 1062194) — that HTML's prior content is gone (reproducible, not unique data; the canonical numbers are already recorded in this Progress Log) and will need a fresh full-section regeneration once the cluster returns or the full campaign tree is re-synced locally. | **V3 GATE VERIFIED LOCALLY — WARN not FAIL, as expected. Cluster unavailable ~2wks; jobs 1070074/1070077 cancelled, not resubmitted.** | Next (once cluster is back or user requests otherwise): V3-E docs refresh; optionally re-run the full validator (`--section` omitted) against the complete campaign to regenerate the canonical HTML report with the new gate 4.9/4.10 baked in alongside all other sections. `agg_enduse_annual.csv` currently only has the 600-row gate-4.9 subset (2022 × 6A/6B/7A) — extend to the full 8,400 rows later via the sqlite-based `extract_enduse_annual.py` (cluster) if a complete end-use table is ever needed for other scenarios/CZs. |
| Date | Action | Status | Notes |
|------|--------|--------|-------|
| 2026-07-08 (employee execution — Phases V3-A→V3-D of `step8_coolfix_employee_prompt_v3_continuation.md`) | **V3-A (revert)**: archived the v2 injector to `archive/integration.20260708_coolfixInjector_v2_falsified.py`, then restored `eSim_bem_utils_3J/integration.py` from `archive/integration.20260708_preCoolfixInjector.py`. Verified: `py_compile` OK; `cooling_seasonal_override`/`COOLFIX_` → 0 matches; SHA-256 of restored file == SHA-256 of the pre-fix archive (byte-identical). v2 was never uploaded to the cluster, so nothing to clean up remotely. **V3-B (retention check)**: one `ls` two levels into `MidRise__Winnipeg_7A/sample_001_HH80741/2022/` on the cluster confirmed `eplusout.sql` present (plus bonus `eplustbl.csv`) — no fallback needed. **V3-C (extractor)**: authored `investigation/extract_enduse_annual.py` (stdlib-only: os/glob/csv/re/sqlite3), walking `<campaign>/<cell>/sample_*/<scenario>/eplusout.sql` and pulling `TabularDataWithStrings` End Uses rows for Heating/Cooling. Local dry-run against `campaign_smoke_v2/` (4 sql files) → `dirs=4 parsed=4 skipped=0`; exact gate match confirmed: MidRise sample_001 2022 = `heating_gas_GJ=78.34`, `cooling_elec_GJ=136.12`. scp'd to the cluster upload tree, submitted `sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "... python investigation/extract_enduse_annual.py > extract_enduse_annual.out 2>&1"` → **job 1070074**. **V3-D (validator re-base)**: archived `3rdJ_08_simulation_2split_val.py` → `archive/3rdJ_08_simulation_2split_val.20260708_preV3metric.py` (predecessor content reconstructed post-hoc via exact-string reversal of the two edits, then diff-verified against the live file to confirm the archive isolates only the intended v3 changes); edited: added `"enduse": "agg_enduse_annual.csv"` to `AGG_FILES`/`load_agg()`; re-based **gate 4.9-heat-dominance** to read `agg_enduse_annual.csv` (ratio = `cooling_elec_GJ / (heating_gas_GJ+heating_elec_GJ+heating_district_GJ)`, same thresholds — FAIL>2.0x 7A, WARN>1.25x 6A/6B/7A — label now says "end-use energy"); added new **gate 4.10-enduse-table** (HTML table, heating fuel vs cooling electricity by archetype × CZ, from the new csv); relabeled 4.6-heat-order/4.7-cool-floor messages to "Air-system delivered sensible energy (incl. ventilation air)" since those stay ET-based. `py_compile` OK on both the edited file and the archived predecessor; report HTML not regenerated locally. scp'd up, submitted `sbatch --dependency=afterok:1070074 -p ps --mem=16G -t 7-00:00:00 --wrap "... python 3rdJ_08_simulation_2split_val.py > step8_val_v3.out 2>&1"` → **job 1070077**. One `squeue -u o_iseri` confirmed 1070074 PENDING (`AssocGrpCpuLimit`) and 1070077 PENDING (`Dependency`) — chain registered correctly. No re-simulation anywhere; 2J untouched; `Buildings_MTL_v242_3Jfix/`/`main.py` untouched. | **V3 EXECUTED — extractor job 1070074 + chained validator job 1070077 queued** | STOP per prompt step 11. No polling. Next session (after user relays completion): scp `agg_enduse_annual.csv` + regenerated report down, check gate 4.9 (expected WARN ~1.7× in 7A, not FAIL — prototype characteristic, paper-framing note), then docs refresh (V3-E). |
| 2026-07-08 (manager — TRUE root cause + fix v3 authored) | Diagnosed from preserved v2 smoke evidence, zero new sims (investigation **§11**): `eplusout.mtd` proves `Cooling:EnergyTransfer` = Σ `Zone Air System Sensible Cooling Energy`; per-unit ERVs (24 MidRise / 46 HighRise, HX-only, thermostat-independent) deliver sub-room-temp air all winter → metered as "cooling" at zero electricity. Confirmations: DJF cooling ET flat across 24/28/40°C while annual Cooling *Electricity* responded (136.12→118.48 GJ, 1a→1b); peak cooling elec July 10; SingleD "clean" only because houses lack per-zone vent systems. Mechanism A retired. Fix v3 section authored above: V3-A revert injector override → V3-B one-`ls` sql retention check → V3-C stdlib sqlite End-Uses extractor over all 25,200 persisted `eplusout.sql` (query verified locally) → V3-D gate-4.9/§4 re-base to end-use metrics + chained `--dependency=afterok` validator run → V3-E docs. **NO re-simulation.** | **FIX v3 READY FOR EXECUTION** | Execute via the v3 continuation prompt (same employee session that ran v2): `step8_coolfix_employee_prompt_v3_continuation.md`. Expected gate outcome: 4.9 → WARN (~1.7× in 7A), a prototype characteristic, not FAIL. |
| 2026-07-08 (employee execution — Phases A-C of `step8_coolfix_employee_prompt.md` v2; BOTH 1a and 1b FAILED smoke) | Phase A (injector code) and Phase B (static injection check) executed and PASSed — `integration.py` gained the `cooling_seasonal_override` mechanism (module constants, `inject_setpoint_schedules()` param + guard, `inject_schedules()` filename gate; predecessor archived to `archive/integration.20260708_preCoolfixInjector.py`), independently verified correct via new `investigation/verify_coolfix_injection.py` for both candidate winter setpoints. Phase C (4-run local smoke) then **FAILED for both variant 1a (28.0°C) and the pre-authorized fallback 1b (40.0°C)** — DJF cooling stayed within ~100-104% of the pre-fix baseline regardless of setpoint. Full results table, code line refs, and root-cause discussion: "v2 execution result" subsection above. | **BLOCKED — both 1a and 1b FAILED smoke; injector-level setpoint fix does not move winter cooling** | STOP per session-boundary/fallback-exhausted rule (prompt Phase C step 10, Phase D not entered). Manager must re-diagnose the actual physical driver of winter `Cooling:EnergyTransfer` in these two archetypes (likely NOT the zone thermostat) before any further fix attempt or re-sim. No cluster jobs pending, no local jobs pending. Both smoke dirs (`campaign_smoke_v2/`, `campaign_smoke_v2_1b/`) preserved for provenance. |
| 2026-07-08 (manager design review — fix v2 chosen) | Fresh manager session reviewed investigation §9/§9.1 against the actual `integration.py` code (all §9 claims verified: `_read_constant_from_schedule` last-numeric-field read at line 1163-1179, flat single-block `_compact_setpoint` at 1189-1201, call site 1996, Compact path live in campaign since `use_schedule_file` defaults False). **Decision: §9.1 option 2, implemented by reusing the existing `create_monthly_compact_schedule()` helper (integration.py:592)** — already emits per-month Through: blocks in Schedule:Compact and is exercised at 3 lighting call sites, so no new multi-block builder and no Schedule:File delivery change. Gating by IDF filename inside `inject_schedules()` (substring ApartmentMidRise/ApartmentHighRise) → only `integration.py` changes; `main.py`, `3rdJ_08B_run_paired_mc.py`, houses, office all untouched. Winter (Jan–Apr, Oct–Dec) = flat 28.0 (max of relief SP and 27.0 setback — setback must never sit below the relief value); summer (May–Sep) = today's 24.0/27.0 occupancy logic unchanged. v1 artifacts (patched IDF dir, `STEP8_BUILDINGS_DIR` repoint, gate 4.9) kept — inert but consistent. New verification ladder adds a static injected-`in.idf` grep check that would have caught v1 pre-sim. Full spec: "Fix v2" section above. Employee prompt rewritten (v2); v1 archived as `archive/step8_coolfix_employee_prompt.20260707_v1_idfPatch.md`. Smoke to run LOCALLY per user (queue saturated). | **FIX v2 READY FOR EXECUTION** | Execute via `step8_coolfix_employee_prompt.md` (v2). Per user 2026-07-08: full-run GO is PRE-AUTHORIZED on smoke PASS — employee continues straight into Phase D (upload + array 84–167 submission) in the same session; stop point = after array submission (or after a 1b smoke FAIL). |
| 2026-07-07 | Plan authored (this doc) | PLANNED | Scope: Step 8B subset (array 84–167, 4,200 runs) → 8D → 8E → 9; Steps 1–7 + 8A + office untouched. Awaiting Phase-0 decision (1a recommended) + GO. |
| 2026-07-07 (later) | Phase-0 resolved: variant **1a** (user delegated the choice to the manager; recommendation ratified). 1b pre-authorized as smoke-gate fallback. Employee prompt authored: `step8_coolfix_employee_prompt.md`. | READY FOR EXECUTION | No code/IDF changed yet — execution starts when the employee prompt is spawned. |
| 2026-07-07 (execution) | Employee session executed Phases 1–4 of `step8_coolfix_employee_prompt.md`. **Phase 1**: new `Buildings_MTL_v242_3Jfix/` dir; `investigation/patch_apartment_cooling_setpoint.py` patched `NECB-G-Thermostat Setpoint-Cooling` in both apartment IDFs to variant 1a (28.0/24.0/28.0 seasonal, WinterDesignDay/SummerDesignDay held at 24.0 in all 3 blocks). Verified: grep spot-check shows seasonal blocks; diff = exactly 1 hunk per file (only that object changed); house IDFs SHA-256-identical to 2J originals. **Phase 2**: archived `eSim_bem_utils_3J/main.py` → `archive/main.20260707_preCoolfix.py`; `STEP8_BUILDINGS_DIR` repointed to `Buildings_MTL_v242_3Jfix`; `py_compile` OK; 2J's `main.py` untouched. **Phase 3**: archived `3rdJ_08_simulation_2split_val.py` → `archive/3rdJ_08_simulation_2split_val.20260707_preCoolfixGate.py`; added gate **4.9-heat-dominance** inside `_gate_enduse_split()` (per-archetype × CZ 6A/6B/7A, `cooling_ET_kWh_sum/heating_ET_kWh_sum`, FAIL >2.0x in 7A, WARN >1.25x in any of 6A/6B/7A, lists per-archetype 7A ratios); `py_compile` OK; report HTML NOT regenerated locally per instruction. **Phase 4**: wrote `run_coolfix_smoke.sh` (copy of `run_residential_array.sh`, `--array` removed, EPWRAP scaffolding kept, two sequential `3rdJ_08B_run_paired_mc.py` calls — `--arch MidRise`/`--arch HighRise`, `--city Winnipeg_7A --scenario 2022 --n 2 --seed 42 --mode standard --out-dir "$SCRATCH/campaign_smoke"`); scp'd the new IDF dir (recursive) + edited `main.py` + edited val script + the smoke script to the matching cluster upload-tree paths (verified landed via remote `ls`); submitted `sbatch run_coolfix_smoke.sh` → **job 1069308**, confirmed PENDING (`AssocGrpCpuLimit`, same queue state as other running jobs) via one `squeue -u o_iseri`. | **SMOKE SUBMITTED — job 1069308** | STOP per session-boundary protocol (prompt step 12). No polling. Resume at Phase 4b (step 13) once the user relays job 1069308 finished: scp the 4 `hourly_meters.csv` files local, run `probe_winter_cooling.py`, evaluate the smoke gate (DJF cooling < 10% of pre-fix MidRise 16,474 / HighRise 34,126 kWh, annual heating up, no E+ severe/fatal in the SLURM log). |
| 2026-07-08 (Phase 4b — SMOKE FAILED, mechanism-level blocker found) | User asked to cancel job 1069308 (cluster queue saturated for a while) and run the 4-run smoke test **locally** instead. `scancel 1069308` confirmed (queue empty). Ran all 4 EnergyPlus jobs locally (`tabletop1`, EnergyPlus 24.2 at `C:\EnergyPlusV24-2-0`, matching local Python 3.13 env) attended in the foreground — light job (~3 min/run), no risk to the box per [[local-runs-parsec-no-reboot]]. 4/4 succeeded. Ran `probe_winter_cooling.py` (`STEP8_CAMP_DIR=outputs_step8/campaign_smoke`) against the local outputs: **DJF cooling MidRise = 18,123 kWh, HighRise = 34,479 kWh — essentially unchanged from pre-fix (16,474 / 34,126), i.e. FAIL** (gate required <10% of pre-fix). Root-caused by inspecting the actual injected schedule in `sample_001_HH80741/2022/in.idf`: the `CoolSP_HH_80741` Schedule:Compact that the simulation actually uses is **flat 24.0°C for the entire year** (`Through: 12/31` / `For: Weekdays SummerDesignDay WinterDesignDay` / all 24 Until-hours = 24.0) — our seasonal 28/24/28 patch never reached the sim. Cause: `inject_setpoint_schedules()` in `eSim_bem_utils_3J/integration.py` (`_read_constant_from_schedule()`, ~line 1163) reads only the **single last numeric field** of the static schedule object as "the active cooling setpoint," then `_compact_setpoint()` (~line 1189) builds **one flat compact schedule for the whole year** (occupancy-based setback only — no seasonal branching at all). In the original file, `For: SummerDesignDay` is the last day-type block within every `Through:` group (verified: grep shows the repeating order Weekdays→Saturday→Sunday→WinterDesignDay→SummerDesignDay in each block) — and our patch script deliberately forces design-day types to 24.0 in *every* Through-block (required for HVAC autosizing, per Phase-1 spec). So the "last field" always resolves to 24.0, regardless of what the surrounding seasonal blocks say. **This bypass is structural, not variant-specific — variant 1b (40°C lockout) would hit the identical mechanism and fail the same way, since it preserves the same design-day-last / forced-24.0 structure.** Did NOT burn compute re-running 1b since the failure mode is provable from the code + the observed `in.idf` evidence, not sample noise. **Conclusion: this falsifies the FIX MECHANISM, not Mechanism A itself** (Mechanism A — frozen 24.0°C cooling driving winter internal-gain cooling — remains correctly diagnosed and independently confirmed). Editing the static IDF template alone can never work here; the real intervention point is the injector logic in `integration.py`, which must be taught to preserve (or itself apply) seasonal cooling setpoints instead of collapsing to one constant. Confirmed 2J has its own separate copy (`eSim_bem_utils_2J/integration.py`) — not shared code, so this doesn't automatically also break/fix 2J, but the same defect pattern should be checked there when 2J is sequenced. | **BLOCKED — needs re-diagnosis / injector redesign** | STOP. This is a manager-level design decision (changes Phase-1 scope from "isolated IDF-copy patch" to "shared injector-logic change" in `eSim_bem_utils_3J/integration.py`). Do not resume Phase 5 (full re-sim) until a new fix approach for the injector is designed and re-verified via a fresh smoke test. No cluster jobs pending; no local jobs pending. |
| 2026-07-08 (options sketched, handed to fresh manager) | Full failure diagnosis (root cause: `inject_setpoint_schedules()`/`_read_constant_from_schedule()` in `eSim_bem_utils_3J/integration.py` collapses any schedule to a single constant + flat year-round Schedule:Compact block, regardless of what the static IDF template says — see `step8_resid_heating_cooling_dominance_investigation.md` §9 for the full mechanism writeup) is now the primary reference doc for the next design pass. Three candidate injector-fix options sketched (§9.1 there), summarized here: **(1) General season-aware rewrite** — change `_read_constant_from_schedule()` to extract all `(Through-block, value)` pairs and `_compact_setpoint()` to emit multiple seasonal `Through:` blocks combined with the existing occupancy setback; touches the shared path every archetype uses; medium-high effort/risk; fully general (2J port free). **(2) Narrow opt-in override** — new optional param (e.g. `cooling_seasonal_override`) on `inject_setpoint_schedules()`, passed only for MidRise/HighRise cells; every other archetype's code path untouched when absent; low effort/risk; matches the runbook's already-narrow scope; current lean. **(3) Reuse `write_8760_schedule_csv_monthly()`** (already exists at ~line 501 of `integration.py`, built for month-varying lighting schedules, unused for setpoints so far) — build a seasonal×occupancy `monthly_data` dict and switch these two archetypes to `use_schedule_file=True`; least new code, but moves cooling-schedule delivery from Schedule:Compact to Schedule:File for these archetypes, a mechanism change worth a downstream sanity check. No option chosen, no code/IDF touched — user is taking this to a fresh Opus manager session to review the diagnosis + options in depth before committing to one. | **AWAITING MANAGER DESIGN REVIEW** | Read `step8_resid_heating_cooling_dominance_investigation.md` §9/§9.1 first — that's the deep-dive; this row is the summary. Once an option is chosen, redo Phase 1 (injector code, not just IDF copies) → fresh 4-run smoke test → re-evaluate the same gate (DJF cooling <10% of pre-fix 16,474/34,126 kWh) before resuming Phase 5. |
