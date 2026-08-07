# Appendix D — Documented Deviations and Corrections

*Source:* `methodology_assessment_and_paper_skeleton.md` §Q2 deviations table; `05_censusLinkageGSS.md` §Deviations from spec; `09_activityDrivenLoads.md` §9.4–9.5; `08_simulation.md` §Sub-step 8G; `writing/resources/2nd_Occ_Journal_BuildInstructions.md` §Appendix D spec

Each entry describes: what the deviation is, why it was needed, how it was resolved, and whether it affects any reported result.

---

## D1 — Derived Apartment SHEU Targets (MidRise / HighRise)

**What:** NRCan SHEU 2019 publishes household-level electricity intensity targets (kWh/hh·yr) for broad dwelling-type categories. The SingleDetached total (12,694 kWh/hh·yr, with appliance share ~3,700 kWh and lighting 1,262 kWh) is directly published. However, the split-out values for MidRise apartment and HighRise apartment appliance/equipment end-use sub-categories are **derived from the SHEU aggregate** rather than directly tabulated for these sub-types.

**Why needed:** Step 9 requires per-dwelling per-end-use SHEU targets as calibration anchors for the activity-driven load model. Using a single national target for all dwelling types would ignore the well-documented lower energy intensity of multi-unit buildings (shared walls, smaller floor area, less heating). SHEU publishes total household intensities by dwelling type; end-use breakdowns at the apartment level require additional derivation.

**How resolved:** Per-dwelling SHEU totals used as anchors (kWh/hh·yr):
- SingleDetached: 12,694 (published); appliances ~3,700 / lighting 1,262
- OtherDwelling (attached): ~10,750 (published SHEU approximate); appliances 3,139 / lighting 1,100
- MidRise apartment: 7,417 (published SHEU); appliances 2,166 / lighting 736
- HighRise apartment: 6,583 (published SHEU); appliances 1,922 / lighting 736

The equipment kWh targets (3,139 / 2,166 / 1,922) and the apartment lighting target (736 kWh) are derived by scaling the SingleDetached reference fractions down proportionately to the published SHEU per-dwelling total. These are model-grade derived values, not directly tabulated SHEU end-use columns for each dwelling sub-type. See D8 for the fridge gross/net correction applied on top of these targets.

**Effect on reported results:** Applies to all Step-9 SHEU calibration scalars for non-SingleDetached archetypes. The SHEU gate (±15%) is tested against these derived targets; all 48/48 cells pass (max deviation equip +2.33%, light +2.63%). Reported as an explicit SI deviation per paper §4.2.

---

## D8 — Multi-Unit Fridge Gross/Net Correction

**What:** For the OtherDwelling (attached / row-house) archetype, the EnergyPlus IDF contains a `refrigerator1` object hard-coded as an always-on internal load (flat 24/7). This means the IDF already accounts for fridge energy independently of the activity-driven Step-9 schedule injection.

**Why needed:** If Step 9 also injects the fridge as part of the baseload (which includes 448 kWh/yr from SHEU), the refrigerator contribution is double-counted: once from the IDF object, once from the Step-9 BASELOAD_W schedule.

**How resolved:** The net SHEU target used for activity-driven calibration is:

SHEU_EQUIP_KWH_NET = 3,700 − 448 = **3,252 kWh** (SingleDetached reference)

The Step-9 BASELOAD_W (130 W flat) does not include the IDF's always-on `refrigerator1` object. Verified: SHEU_EQUIP_KWH_NET = 3,252 kWh in production code. The analogous correction for OtherDwelling uses the same principle (gross SHEU target minus IDF-accounted refrigerator UEC) to set the net calibration target.

**Effect on reported results:** Affects the Step-9 calibration scalar for equipment (appliances). Without this correction, the equipment scalar would be over-estimated by ~448/3700 ≈ 12% for the SingleDetached archetype. The correction was applied before the SHEU gate check; all 48/48 cells pass. Related to Deviation R4 below.

---

## R1 — Lighting Definition: Binary Occupied-and-Awake, No Daylight Gate

**What:** The as-built lighting model in Step 9 is:

`lighting(t) = binary [occupied-and-awake at slot t] × SHEU_lighting_scalar`

There is **no daylight gate** (i.e., no suppression of lighting when irradiance exceeds a threshold). The original design specified a daylight-gated model where lighting was active only when both (a) occupied-and-awake and (b) the time-of-day was within a dark/low-irradiance window.

**Why needed / what changed:** Investigation finding R1 (2026-06-08, documented 2026-06-10): the shipped production code uses the occupied-and-awake binary without a daylight gate. The daylight-gated formulation was the design intent but was not implemented in the production version. Any paper or SI text must describe the occupied-and-awake formulation as the implemented model.

**How resolved:** The occupied-and-awake binary is derived from the `hom30` (presence) channel and the activity code (code 5 = Sleep → not awake). Lighting weight = 1.0 for all active-at-home activity codes; 0 for Sleep, Travel, Purchasing, Community (all away or inactive). Annual total anchored to SHEU lighting target via calibration scalar f_light.

**Effect on reported results:** The omission of the daylight gate slightly overestimates daytime lighting load (the model does not zero out lighting during daylight hours in summer). However, because the annual total is anchored to SHEU via scalar f_light, the overestimate in daytime slots is compensated by the scalar and does not affect the annual total. The load-shape peak timing (evening peak) is robust to this simplification because the dominant lighting driver is evening occupancy, not midday presence. SHEU 48/48 cells pass. Documented as SI correction R1.

---

## R4 — Fridge Gross/Net Correction (Production Code)

**What:** Companion to D8. The gross SHEU equipment target for SingleDetached is 3,700 kWh/hh·yr. The production code applies a net target of 3,252 kWh (= 3,700 − 448) to avoid double-counting the always-on IDF `refrigerator1` object.

**Why needed:** Same as D8 — the IDF already embeds the fridge as a hard-coded internal load.

**How resolved:** SHEU_EQUIP_KWH_NET = 3,700 − 448 = 3,252 kWh, applied uniformly in `09_activityDrivenLoads.py` before computing the calibration scalar. The gross 3,700 kWh figure is the SHEU published total; the 448 kWh deduction is the SHEU/CEUD T16 published fridge UEC.

**Effect on reported results:** Same as D8. Scalar is correctly set; all SHEU gates pass.

---

## Step 5 — MARSTH NaN ×183 and LFTAG NaN ×3,906 Handling

**What:** In the Step-4 augmented diary pool (`augmented_diaries.csv`, 192,183 rows), two conditioning variables contain NaN for a subset of rows:
- **MARSTH (marital status) NaN: 183 rows** (61 observed + 122 synthetic; the 1:2 ratio reflects IS_SYNTHETIC amplification — the 61 observed rows originate from 61 real GSS respondents with missing marital status).
- **LFTAG (labour force activity) NaN: 3,906 rows** (1,302 observed + 2,604 synthetic; same amplification pattern, originating from ~1,302 real GSS respondents with missing labour force status).

**Why needed / what happened:** The Step-5 statistical matching uses a tiered match scheme. MARSTH is a required key for Tier 1 (exact match on all 7 keys). LFTAG is a required key for Tier 1 and Tier 2. Pool rows with NaN in tier-required keys cannot be placed in those tiers.

**How resolved:** The `_build_index()` function applies `dropna(subset=keys)` before indexing each tier. This means:
- MARSTH-NaN rows (183): excluded from Tier 1 only; eligible for Tier 2 (AGEGRP, SEX, LFTAG, PR + DDAY) and below.
- LFTAG-NaN rows (3,906): excluded from Tier 1 and Tier 2; eligible for Tier 3 (AGEGRP, SEX + DDAY) and Tier 4 (FailSafe).

The full-run tier distribution confirms FailSafe = 0% (all 286,537 Census agents matched in Tier 1–3), so LFTAG-NaN rows were successfully absorbed by Tier 3 rather than degraded to FailSafe. This is documented as paper §4.2 deviation.

**Effect on reported results:** No Census agent was left unmatched (FailSafe = 0%). The 3,906 LFTAG-NaN rows do not distort the final 144,507-household BEM frame, as Tier 3 still provides a demographically plausible match on age, sex, and day-type. The MARSTH and LFTAG NaN rates are low (183/192,183 = 0.095%; 3,906/192,183 = 2.03%) and are retained as documented pipeline deviations in paper §4.2.

---

## 8G — DX-Coil Sizing Fix (OtherDwelling × Kelowna 5B × 2010)

**What:** One EnergyPlus run in the Step-8 6,000-run campaign failed with a deterministic sizing fatal error: the OtherDwelling archetype × Kelowna (climate zone 5B) × 2010 occupancy schedule triggered an EnergyPlus DX cooling coil autosizing failure.

**Why needed:** The Kelowna 5B climate is drier and warmer than the MTL-set IDF was calibrated for; combined with the 2010 occupancy schedule (moderate cooling demand), the autosizing algorithm produced a Gross Rated Sensible Heat Ratio (GRSR) that failed the EnergyPlus sizing check. This is a one-off climate × archetype × year interaction, not a systemic code defect.

**How resolved:** Sub-step 8G fix (job IDs 954296/954300): changed the OtherDwelling DX coil sizing parameter from `autosize` to a fixed Gross Rated Sensible Heat Ratio of **0.75**. This is within the physically plausible range for Canadian residential DX systems and resolves the sizing fatal without altering the thermal envelope or occupancy schedule.

**Effect on reported results:** EUI impact: ≤ 0.013 kWh/m² for this single run (negligible relative to inter-archetype and inter-year variability). The fix was included in the v2 corrected campaign final scorecard (6,000/6,000 runs, 24 PASS / 0 WARN / 3 INFO / 0 FAIL). No reported headline metric is materially affected.
