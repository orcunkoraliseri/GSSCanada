# Audit: which 2J (single-channel) fixes apply to 3J Leg-2 (2-split)?

**Compiled:** 2026-07-15
**Purpose:** reference notes only — no code was changed by this pass. Cross-checks every major bug/fix recorded in the 2J master log against the 3J Leg-2 (two-channel: residential + office/WFH) codebase's own forked files, to tell a future adaptation session exactly what still needs porting, what's already fixed, and what's a *new*, 3J-specific problem the 2J log never covered.
**Source of the 2J side:** [`2J_docs_occ_nTemp/improvement-planning/2J_improvements_master_log.md`](../../../2J_docs_occ_nTemp/improvement-planning/2J_improvements_master_log.md)
**Why a full recheck was needed, not a copy-paste:** 3J Leg-2 does not share code files with 2J — it has its own fully forked copies of every relevant script (`3rdJ_05_censusLinkage_2split.py`, `3rdJ_04L_joint_rake_2split.py`, `3rdJ_07_aug_to_bem_2split.py`, `Step8_docs/eSim_bem_utils_3J/integration.py`), each forked at a different point in time, so each 2J fix could independently be present, absent, or partially addressed.

**Pipeline scope confirmed:** 3J Leg-2 covers the same **2005–2022 GSS cycles + 2030 forecast** as 2J (not a reduced subset), so year-scoped 2J bugs are in-scope by default unless shown otherwise.

---

## Summary table

| # | 2J issue | 3J Leg-2 status | Priority for adaptation session |
|---|---|---|---|
| 1 | 2005 `PR` census-linkage disjointness (region-tier fix) | ✅ **Already fixed** | None — verify only |
| 2 | Un-raked activity channel (act30 in 2J; act30+office in 3J) | ⚠️ **Partially addressed, worse in 3J** — occupancy is jointly raked (better than 2J), but activity is fully un-raked with a documented **61.12% work-activity/AT_WORK=0 mismatch**, already flagged internally with a proposed fix | 🔴 **HIGH** |
| 3 | +4h diary→clock offset (`07_aug_to_bem.py`) | ✅ **Already fixed** (ported explicitly, dated 2026-06-08) | None — verify only |
| 4 | Multi-zone equipment/lighting injection bug (`integration.py`) | ❌ **Same bug confirmed present, unfixed** | 🔴 **HIGH** |
| 5 | Heating/cooling dominance metering artifact (ERV false-cooling) | ✅ **Already fixed — 3J did this FIRST**, 2J's fix was ported *from* 3J's investigation | None — this is 3J's own prior work |
| 6 | Household frame-size consistency (144,507→144,465 in 2J) | ❓ **Unclear / not checked** — no explicit frame-size number found in the 3J pipeline docs read | 🟡 Needs a dedicated follow-up check |

---

## 1. 2005 `PR` census-linkage disjointness — ✅ Already fixed

**2J finding (for reference):** 2005 GSS diaries used a legacy 5-region `PR` coding disjoint from the Census SGC codes used by 2010/2015/2022, causing 2005 to fail linkage almost entirely (~9% match share vs. 30% pool share) until a `REGION_FOLD` crosswalk was merged into the matching tier.

**3J status:** the equivalent script, [`Step5_docs/3rdJ_05_censusLinkage_2split.py`](../Step5_docs/3rdJ_05_censusLinkage_2split.py), already applies a `_PROVINCE_TO_REGION` remap inside `load_augmented_pool()`, **before** the Tier-1/2/3/4 matching keys are built:

```python
_PROVINCE_TO_REGION: dict[int, int] = {
    1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6,   # already grouped — identity
    10: 1, 11: 1, 12: 1, 13: 1,            # Atlantic
    24: 2,                                  # Quebec
    35: 3,                                  # Ontario
    46: 4, 47: 4, 48: 4,                   # Prairies
    59: 5,                                  # British Columbia
    60: 6, 61: 6, 62: 6,                   # Northern Canada
}
```

This was applied as part of a 2026-06-23 fix (per the script's own `.md`), **independently of and before** 2J's own July-9 fix. No porting needed — recommend only a quick spot-check confirming 2005's matched share is now reasonable (2J's post-fix reference: ~15.76%; 3J's exact number not separately re-derived in this pass).

---

## 2. Un-raked activity/office channel — 🔴 HIGH priority, worse than 2J's version

**2J finding (for reference):** raking only the binary AT_HOME channel left the 14-category activity channel un-calibrated, producing a +12.3pp weekday paid-work over-fire and 10–15% equipment/lighting shape errors — fixed via a joint rake (`_rake_categorical_slot()`) conditioned on stratum×slot×LFTAG.

**3J status — genuinely more advanced in one respect, and worse in another:**
- **Better than 2J's original:** [`Step4_docs/3rdJ_04L_joint_rake_2split.py`](../Step4_docs/3rdJ_04L_joint_rake_2split.py) already jointly rakes **both** binary occupancy channels (`hom30` AT_HOME **and** `wrk30` AT_WORK) together with mutual exclusion — this is a genuine improvement 2J never had (2J only ever raked one binary channel).
- **Same limitation as 2J's pre-fix state, left explicitly undone:** the script's own header says outright — *"Activity (act30_\*) and COP columns are carried forward untouched from R5."*
- **🚩 Already internally documented as a real, more severe problem than 2J's version:** a design-assessment report already sitting in the repo — [`Step4_docs/deepResearch/dr_S4-02_posthoc_calibration_raking_REPORT.md`](../Step4_docs/deepResearch/dr_S4-02_posthoc_calibration_raking_REPORT.md) — measures **Work activity when `AT_WORK=0` at 61.12%** (vs. 16.36% observed) — a "CRITICAL FAIL" semantic-consistency break (synthetic people "doing work" while marked as not at their workplace), compared to 2J's milder +12.3pp over-fire. That report already proposes two paths forward: (1) publish with the 61.12% discordance as a documented caveat, or (2) implement a **hard-lock priority-based rake** (constrain work activities to `wrk30=1` slots before raking the residual slots) — essentially the 3J-specific version of 2J's Task B fix, adapted for two binary channels instead of one.
- **What 2J's actual fix (`_rake_categorical_slot()`, conditioned per stratum×slot×LFTAG, applied within hom30=1/0 subsets) offers as a starting point:** the same conditional-factorization approach could likely extend to a 3-way split (hom30=1 / wrk30=1 / neither) rather than requiring a full joint IPF — worth handing to the adaptation session as a concrete starting design, not a from-scratch problem.

**Recommendation for the adaptation session:** treat this as the single most consequential 3J-specific gap — it's already self-diagnosed with numbers, and a design report with a candidate fix already exists in-repo. This is arguably higher priority than porting the multi-zone injection fix, since it affects every downstream table's activity-shape and paid-work claims for the office channel.

---

## 3. +4h diary→clock offset — ✅ Already fixed

**2J finding (for reference):** `07_aug_to_bem.py` originally reshaped the 48-slot diary positionally instead of resampling by real clock hour, injecting all schedules 4 hours early relative to the EnergyPlus weather clock.

**3J status:** [`Step7_docs/3rdJ_07_aug_to_bem_2split.py`](../Step7_docs/3rdJ_07_aug_to_bem_2split.py) already has the fix, explicitly ported and dated:

```python
# FIX 2026-06-08 (4h diary->clock offset, ported from 2J):
# GSS diary slots are 4 AM-origin (slot 1 = 04:00). Roll +4h so Hour 0 = real midnight,
# matching the EPW weather clock. Without this, schedules inject 4h early vs weather.
occ24 = np.roll(occ24, 4, axis=1)
met24 = np.roll(met24, 4, axis=1)
```

The same `np.roll(..., 4)` pattern is applied to the office/`wrk30` channel too (line ~307). No porting needed — this fix already crossed over from 2J to 3J on 2026-06-08, a full month before 2J's own Step-7 report caught its own staleness. Good example of the cross-pollination already happening in the *other* direction (2J→3J here, vs. the ERV fix below going 3J→2J).

---

## 4. Multi-zone equipment/lighting injection bug — 🔴 HIGH priority, confirmed present and unfixed

**2J finding (for reference):** for multi-zone apartment archetypes (MidRise/HighRise/OtherDwelling), the SHEU-calibrated equipment/lighting carrier was injected into only the occupancy zone, while legacy objects were neutralized across *all* zones — collapsing whole-building electricity to ~1/N_units of its true value. Fixed in 2J by replicating the carrier across every zone that had a legacy object neutralized.

**3J status: the identical bug pattern is present, unfixed**, confirmed directly from [`Step8_docs/eSim_bem_utils_3J/integration.py`](../Step8_docs/eSim_bem_utils_3J/integration.py):

Neutralization loop — scoped to **all zones**:
```python
for _eo in list(idf.idfobjects.get('ELECTRICEQUIPMENT', [])):  # all objects, all zones
    ...
    try: _eo.Design_Level = 0.0
    ...
for _lo in list(idf.idfobjects.get('LIGHTS', [])):              # all objects, all zones
    ...
    try: _lo.Lighting_Level = 0.0
```

Carrier injection — scoped to **one zone only**:
```python
_ec = idf.newidfobject("ElectricEquipment")
_s9_set_zone(_ec, _s9_occ_zone)      # single zone only
...
_lc = idf.newidfobject("Lights")
_s9_set_zone(_lc, _s9_occ_zone)      # single zone only
```

The zone-scope mismatch (all zones neutralized, one zone re-populated) is exactly 2J's pre-fix pattern. Expected impact for 3J's multi-zone archetypes: whole-building equipment/lighting electricity undercounted by roughly 1/N_units (2J measured ~37–99x depending on archetype; 3J's own archetype mix would need re-measuring, but the mechanism is identical).

**Recommendation for the adaptation session:** the 2J fix (replicate the carrier across every zone that had a legacy object neutralized, `_s9_equip_zones`/`_s9_light_zones`, falling back to the occupancy zone only if empty) is a near-direct port — same function names/pattern exist in both files since `eSim_bem_utils_3J` was forked from `eSim_bem_utils_2J`. This is likely the most mechanically straightforward of the three open items, even though it's high-impact.

---

## 5. Heating/cooling dominance metering artifact (ERV false-cooling) — ✅ Already fixed, and 3J did it first

**2J finding (for reference):** apartment cooling energy implausibly rivaled/exceeded heating in cold climate zones; root cause was `Cooling:EnergyTransfer` counting thermostat-independent ERV ventilation air as "cooling" at zero electricity cost — not a real setpoint problem.

**3J status:** this investigation **originated in 3J**, not 2J. [`Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md`](../Step8_docs/investigation/step8_resid_heating_cooling_dominance_investigation.md) documents the full arc:
- **v1** (static IDF setpoint patch, `patch_apartment_cooling_setpoint.py`) — failed, bypassed by the schedule injector.
- **v2** (injector-level setpoint override, 28°C/40°C) — failed smoke test; DJF cooling stayed flat regardless of setpoint, which is what pointed to the ERV mechanism rather than the thermostat.
- **v3** (metric re-base, no re-simulation) — ✅ **executed and verified locally 2026-07-08**: re-based gate 4.9 onto true end-use energy (Cooling:Electricity vs. heating fuel) instead of `Cooling:EnergyTransfer`. Result: gate 4.9 = WARN not FAIL (CZ7A ratios: SingleD 0.20×, MidRise 0.67×, OtherDwelling 0.33×, HighRise 0.71×). Scorecard: 50 PASS / 2 WARN / 17 INFO / 0 FAIL.
- The setpoint-patch artifacts (`Buildings_MTL_v242_3Jfix/`) are kept for provenance but are runtime-inert since v3 abandoned the setpoint approach entirely once the ERV mechanism was confirmed.

No porting needed in this direction — if anything, 2J's Item 1/Item 2 (heating/cooling dominance investigation, end-use metric re-base) should cite **this** 3J investigation as the origin. Only remaining task (non-blocking, cosmetic): regenerate the full canonical HTML report once cluster compute returns — no re-simulation required.

---

## 6. Household frame-size consistency — ❓ Unclear, needs a dedicated follow-up

**2J finding (for reference):** a Step-5 region-tier relink + joint rake + 5H exclusion refresh shrank the population frame from 144,507 to 144,465 households (−42 HH/−52 persons), which needed propagating through Steps 7–9 and could silently invalidate a downstream campaign built on the older frame if missed.

**3J status:** not established in this pass — the pipeline-overview docs read (`3rdJ_00_2split_Occupancy_Pipeline.md`/`_Overview.md`/`2-channel_split.md`) mention a "frozen frame" concept for Step 8 (holding the household sample constant during simulation) but state no explicit household count or its provenance relative to 2J's linked population.

**Recommendation:** before any new 3J Leg-2 simulation campaign, have the adaptation session explicitly check what household count `3rdJ_05_censusLinkage_2split.py`'s current output actually produces, and whether any 3J-side BEM campaign was built on an older/stale count the way 2J's Step-8 campaign briefly was. This is a "verify it's not a problem" item, not a confirmed bug — don't treat it as equivalent priority to items 2 and 4 above without first checking.

---

## Recommended priority order for the adaptation session

1. **Multi-zone injection bug** (Item 4) — mechanically near-identical fix already exists in 2J's `eSim_bem_utils_2J/integration.py`; likely the fastest high-impact win.
2. **Un-raked activity/office channel, 61.12% discordance** (Item 2) — highest-impact open problem, but needs real design work (extending 2J's conditional-factorization approach to a 3-way hom30/wrk30/neither split, or implementing the hard-lock priority rake already proposed in `dr_S4-02_posthoc_calibration_raking_REPORT.md`).
3. **Frame-size consistency check** (Item 6) — quick verification, do before any new simulation campaign.
4. Items 1, 3, 5 — no action needed, verification-only if desired.

---

*This document is a reference/audit only — no 3J code was modified while producing it. Cross-reference: [2J master improvement log](../../../2J_docs_occ_nTemp/improvement-planning/2J_improvements_master_log.md).*
