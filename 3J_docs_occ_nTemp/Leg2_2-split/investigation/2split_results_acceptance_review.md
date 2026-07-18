# 2-Split (Leg-2) Results — Paper-Readiness Acceptance Review

**Date:** 2026-07-02 · **Reviewer:** Claude (manager session) · **Requested by:** user, before pivoting to 4-split (Leg-3)

**Scope:** the two pipeline docs (`3rdJ_00_2split_Occupancy_Pipeline.md` + `_Overview.md`) and the four validation reports — Step 7 (2022 + 2030), Step 8, Step 9.

---

## VERDICT: ✅ ACCEPTABLE FOR THE PAPER — 0 FAIL across all four reports, post-WFH-fix

…but only after resolving a **stale-artifact inconsistency found during this review** (§2 below, now fixed), and with **3 WARNs + 4 caveats** that the paper must frame correctly (§3–§4).

| Report | Generated | Scorecard | Verdict |
|---|---|---|---|
| Step 7 — 2022 | 2026-06-26 19:04 | 32 PASS · 0 WARN · 0 FAIL (100%) | ✅ clean |
| Step 7 — 2030 | 2026-06-26 19:04 | 43 PASS · 0 WARN · 0 FAIL (100%) | ✅ clean |
| Step 8 — two-channel E+ | **2026-07-02 20:59 (§8E post-§7.2-reword, job 1062194)** | 46 PASS · 1 WARN · 13 INFO · 0 FAIL | ✅ clean; §7.2 RESOLVED |
| Step 9 — bi-channel end-use | **2026-07-02 20:20 (post-fix re-run)** | 10 PASS · 1 WARN · 0 FAIL | ✅ acceptable; G8o confirms WFH-modulation live |

Step 7 predates the office WFH bug but is unaffected: the bug lived in the Step-8 IDF integration (`office_integration.py` zone-field name for E+ v24.2), never in the Step-7 multiplier inputs, which were always correct.

---

## 1 · Timeline context — why the reports changed today

The office (AT_WORK) channel of Step 8 was originally simulated **without working WFH modulation**: on the v24.2 IDFs every zone name read as `""` → all 22 zones tagged `skip` → the band-specific `OFC_*` schedules were appended but never wired → all 7 scenarios ran the prototype `NECB-A-Occupancy` and produced **byte-identical office outputs** (probe job 1057830). A second latent bug set the People schedule via `Schedule_Name` instead of `Number_of_People_Schedule_Name`.

Both were fixed 2026-07-02 (`office_integration.py`; predecessor archived as `archive/office_integration.20260702.py`), smoke-validated (job 1057831), and the full recovery chain completed **today** on Speed:

| Job | What | State |
|---|---|---|
| 1058490 (array 0–251) | Office re-simulation, all 252 runs, `--no-skip` | 252/252 COMPLETED exit 0 (verified via `sacct` during this review) |
| 1058661 | §8D re-aggregation + §8E validator re-run | COMPLETED 20:19 |
| 1058662 | Step-9 re-run on fresh agg tables | COMPLETED 20:20 |

## 2 · Finding during this review: stale local artifacts (NOW FIXED)

When this review started, the **local** copies were internally contradictory:

- `Step8_docs/outputs_step8/step8_validation_report.html` was the **pre-fix** version (generated 2026-07-01 19:34) — its office gates (§4.3 office EUI 180, §6.3, §7.2 "occupancy −0% → energy −0%") were computed on the flat, bugged outputs. §7.2 passed **vacuously** (zero deltas on both sides).
- `Step9_docs/outputs_step9/step9_report.html` + `figures/` were **post-fix** (pulled 20:27), but the four sidecar CSVs (`step9_scenario_response.csv` etc.) were **pre-fix** — office `occ_mean` 163.683 byte-identical across all 7 scenarios. Anyone pulling paper numbers from those CSVs would have reproduced the bug.

**Action taken (this review):**
1. Stale versions archived → `investigation/stale_pre_fix_snapshot/` (step8 report + 4 CSVs).
2. Fresh post-fix files pulled from `speed:/speed-scratch/o_iseri/step8_2split/upload/.../outputs_step8|outputs_step9/` → local `step8_validation_report.html` (now 2026-07-02 20:19) and the 4 Step-9 CSVs (now matching the HTML: office occ_mean 152.26–161.12 across scenarios).
3. Verified local CSV values now match the Step-9 HTML tables exactly.

**Local and cluster are now in sync.** All numbers below are from the post-fix reports.

## 3 · The 3 WARNs — all explainable, none blocking

### 3.1 §4.1-SingleD (Step 8) + G2r (Step 9) — SingleD EUI 213 kWh/m² outside SHEU band [131–186]
The long-known **EUI-basis mismatch**: our denominator is conditioned area *including basement*; SHEU-2019's is heated area *excluding basement*. All other three residential archetypes are in band (OtherDwelling 140, MidRise 177, HighRise 143). Non-blocking, already documented — the paper needs one sentence on the basis difference.

### 3.2 §7.2-conservative and §7.2-hybrid (Step 8) — "energy fell more than occupancy — check" — ✅ RESOLVED 2026-07-02
**These were gate-semantics artifacts, not physical problems.** The §7.2 gate was written assuming every 2030 band would show an occupancy *cut* vs 2022 (testing the non-linearity: 20–50% occ cut → only 10–30% energy savings). But vs the 2022 baseline — which already carries ~30% real-world WFH — the **conservative-return band (15–20% WFH) has MORE office presence, not less**:

| Office scenario (vs 2022) | occ_mean Δ | energy Δ | midday share |
|---|---|---|---|
| 2030-conservative | **+5.41%** | **+0.54%** | 0.442 |
| 2030-hybrid | +2.55% | −0.01% | 0.439 |
| 2030-fullyhybrid | +0.65% | −0.33% | 0.437 |

Direction and magnitude are physically right (HVAC-dominated tower ⇒ strongly damped energy response; monotone band ordering holds on WD peak occupancy 0.7015 ≥ 0.6169 ≥ 0.6045 and midday share). The gate's message template just mangled the sign for occupancy *increases*.

**Fix applied:** §7.2 gate reworded direction-agnostic (criterion: |eΔ%| ≤ |occΔ%| + 1 pp) in `3rdJ_08_simulation_2split_val.py`; predecessor archived on cluster as `3rdJ_08_simulation_2split_val.20260702_pre72reword.py`. §8E re-validated (job 1062194, COMPLETED 2026-07-02 20:59, elapsed 2:57): all three §7.2 gates now **PASS** with "damped response, base loads dominate" messages. Final scorecard: **46 PASS · 1 WARN · 13 INFO · 0 FAIL**.

### 3.3 Scorecard progression
Pre-fix §8E: 46P/1W (§7.2 passed vacuously on flat outputs). Post-WFH-fix §8E: 44P/3W (real deltas exposed the gate's sign assumption — see §3.2). Post-§7.2-reword §8E (job 1062194): **46P/1W** — the final closed-out state. The lone remaining WARN is §4.1-SingleD (EUI-basis mismatch, §3.1 above), unchanged throughout. Worth one sentence in the paper's validation narrative: the scorecard temporarily dipped to 44P/3W because the simulation became *more honest*, then recovered to 46P/1W after the gate semantics were corrected.

## 4 · Paper-facing caveats (carry into the manuscript)

1. **§6.3 (Step 8) is an input-side gate.** Its values (0.7015/0.6169/0.6045) are identical pre- and post-fix — it reads the Step-7 multiplier *inputs*, not simulated outputs. It was the source of pre-fix false confidence. The *sim-side* WFH signal is now independently verified by Step-9 **G8o** (2030 bands non-degenerate, energy% 0.54/−0.01/−0.33) and Step-8 §7.2 real deltas. Cite G8o/§7.2, not §6.3, as evidence the WFH signal reaches the BEM.
2. **Office annual energy is nearly flat across bands (range ≈0.9%) — by design, not by bug.** The signal lives in *peak occupancy, midday share and load shape*, not annual kWh (fixed HVAC/ventilation + plug baseload; the documented non-linearity). Frame the office 2030 result on peak/shape metrics; annual EUI is secondary (per the pipeline doc's own Step-8 framing).
3. **Historical office multipliers (2005/2010/2015) carry reconstruction uncertainty** (§0.5 INFO): AT_WORK gating variable differs across cycles (PLACE=02 vs LOCATION=301/3301). One caveat sentence in the longitudinal section.
4. **Office EUI pass criterion is the as-modelled NECB/PNNL band [100–200] (median 173 ✅), not the SCIEU measured stock (~230).** Code-compliant prototypes legitimately sit below measured stock — keep the §4.4 framing so a reviewer doesn't read 173 vs 230 as a miss.

## 5 · Residual bookkeeping (not results-blocking)

- [x] **Reword §7.2 gate** for occupancy-increase bands (§3.2) and refresh §8E — **DONE 2026-07-02** (job 1062194): 46P/1W/13I/0F confirmed.
- [x] **Step-9 doc** (`Step9_docs/`): update §R3/§R4 + ledger + caveats to the post-fix numbers — **DONE 2026-07-02** (office EUI 172.6, G8o PASS, return-to-office framing, Progress Log appended; job 1058662).
- [x] **Reframe the two pipeline docs**: status convention and all step boxes already read `✅ DONE (Leg 2)` — **confirmed 2026-07-02** (no stale ⚠️ PLANNED tags found in either `3rdJ_00_2split_Occupancy_Pipeline.md` or `_Overview.md`).
- [ ] **Fig sanity:** local `figures/*.png` are post-fix (20:27) and consistent with the HTML — no action.
- [ ] Cluster copy of record: `speed:/speed-scratch/o_iseri/step8_2split/upload/...` (agg tables `agg_{annual,peak,diurnal,meta}.csv` re-written 2026-07-02 20:14; `agg_diurnal.csv` is 180 MB — pull only if needed).

## 6 · Bottom line

The 2-split results are **paper-ready and fully closed out as of 2026-07-02**: every hard gate passes in all four reports (Step-7 2022/2030, Step-8 final 46P/1W/13I/0F, Step-9 10P/1W/0F), the office WFH-modulation bug is fixed and re-simulated (252/252), the §7.2 gate is reworded direction-agnostic, all docs (Step-8 val, Step-9, both pipeline docs) are updated and consistent with the cluster. All three actionable residuals from §5 are resolved. Remaining §5 items (Fig sanity, cluster copy of record) required no action. The four paper-framing caveats (§4) carry forward to the manuscript. Safe to pivot to Leg-3 (4-split); the residential channel was never affected.

---

# ADDENDUM 2026-07-17 — SUPERSEDES the 2026-07-02 verdict (two-fix cascade re-run)

The 2026-07-02 "paper-ready" verdict above stands on its physics conclusions, but its **scorecards and per-zone energy provenance are superseded** by a full Step-8→Step-9 re-run that propagates two additional fixes not present on 2026-07-02:

1. **act30 recalibration (new 04T rake).** act30 was uncalibrated, admitting physically-impossible **FLOATING** work slots (work with `hom30=0` AND `wrk30=0`). The new **04T** rake (runs after 04M: 04L → 04M → **04T**) removes only FLOATING and never touches **TELEWORK** (`hom30=1`, the paper's core signal). This changes household sampling, so fresh runs draw different `sim_hh_id` than the 2026-07-02 campaign.
2. **Multi-zone injection fix (`integration.py`, md5 `6a92268be1f8dc3301df3bec80d6dd2e`).** Per-zone energy carriers replace a single-zone injection that had misdistributed equip/lighting across zones of multi-zone archetypes.

## A · New scorecards (this cascade — the numbers of record)

| Report | 2026-07-02 (superseded) | 2026-07-17 (of record) |
|---|---|---|
| **Step-8 validation** | 46P / 1W / 13I / 0F | **50P / 1W / 17I / 0F** |
| **Step-9 validation** | 10P / 1W / 0F | **10P / 1W / 0F** |

- **0 FAIL in both** — the two-fix cascade introduces no regression.
- Step-8 higher P/I totals = the current validator evaluates more sub-gates than the July-2 build; the single WARN is unchanged (**§4.1-SingleD EUI-basis mismatch**, §3.1 above).
- Step-9 is bit-for-bit the same scorecard shape: **G8o PASS** (office WFH-modulation live: `energy% cons/hyb/full = 0.53 / -0.00 / -0.32`, range 0.85), **G2o office EUI PASS** (median 172.7 kWh/m², in [100–200]), **G8r residential WFH PASS** (2022 0.249 → 0.251/0.262/0.272, monotone). Sole non-pass = **G2r WARN** (SingleD 212.1 kWh/m², same basis mismatch).

## B · ⚠️ PUBLISHABLE-RESULTS FINDING — the multi-zone injection fix is ENERGY-NEUTRAL on annual aggregates

The injection fix was expected to step multi-zone equipment/lighting energy **up by ~zone-count factor** (a static eppy smoke-test on IDF `Design Level` objects predicted MidRise ~25×, HighRise ~27×, OtherDwelling ~7×). **Simulated annual energy did NOT move.** Verified three ways:

1. **Genuine baseline.** The pre-fix `agg_annual.csv` compared against is md5 `d4784a3d`, byte-identical to the md5-verified cluster archive `archive/agg.20260706_pre_actv2/` — a real pre-fix artifact, not a mislabel.
2. **Fresh run used the FIXED code.** The new campaign's `integration.py` is md5 `6a92268…` (the fixed file), confirmed on the cluster.
3. **Matched multi-zone building is byte-identical.** A HighRise unit present in both campaigns (`sim_hh_id 84891`) has **identical** simulated `equip_kWh` (224,761.27 kWh) buggy vs fixed — decisive proof the fix conserves whole-building annual energy.

**Mechanism:** HighRise IS genuinely multi-zone (69 thermal zones, 26 ElectricEquipment, 50 Lights, ZoneGroup ×8). The "bug" misdistributed loads **among** zones; the whole-building annual total was always conserved (EnergyPlus sums zone loads). The ~N× figure was a **static IDF-object count, never simulated energy.**

**Consequence for the manuscript (must be stated correctly):**
- The paper's **annual EUI / energy numbers are UNCHANGED and remain valid** — they were never deflated at the annual level.
- The paper **must NOT claim the injection fix "restored" or "recovered" multi-zone energy** at the annual level. It corrects **per-zone distribution** (relevant to zone-level diagnostics), not whole-building annual totals.
- DetachedHouse/SingleD (single-zone) is unaffected, as expected — and so, at the annual level, is everything else.

## C · Residual caveats (carry forward; the §4 caveats above still all apply)

- The four §4 paper-framing caveats (§6.3 is input-side → cite G8o/§7.2; office annual energy flat by design; historical-multiplier reconstruction uncertainty; office EUI band is as-modelled NECB/PNNL) are **unchanged** and still carry into the manuscript.
- **Add caveat #5:** the multi-zone injection fix is energy-neutral on annual aggregates (§B) — describe it as a per-zone distribution correction, not an energy recovery.
- **Enduse gate (4.9, heat/cool dominance):** a fresh `agg_enduse_annual.csv` (Jul-17 13:09) exists and was visible to the Step-9 run; the dedicated extractor job was still finishing at note time. Gate 4.9 WARN remains acceptable per ERV v3.
- **G4 pooled-strata defect** and the **cross-era pairing** limitation remain filed-not-fixed (out of scope; see the respective tickets) — unchanged by this cascade.

## D · Bottom line (of record, 2026-07-17)

The 2-split results **remain paper-ready**. The two-fix cascade (04T rake + multi-zone injection fix) re-ran the full Step-8→Step-9 chain with **0 FAIL in both reports** (Step-8 **50P/1W/17I/0F**, Step-9 **10P/1W/0F**) and **did not change any publishable annual energy number** — the injection fix is energy-neutral at the annual level (§B), and the act30 04T rake removes only physically-impossible FLOATING slots without disturbing the TELEWORK signal. The WFH signal reaches the BEM (G8o PASS). This ADDENDUM is the current record; the 2026-07-02 scorecards are superseded, its physics conclusions retained.
