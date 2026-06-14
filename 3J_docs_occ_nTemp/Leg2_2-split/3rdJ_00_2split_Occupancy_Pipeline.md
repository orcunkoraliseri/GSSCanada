# Residential + Office Two-Channel Occupancy Pipeline for BEM/UBEM
### Longitudinal Occupancy-Driven Energy Demand in Canadian Residential & Commercial Buildings (2005–2030)
#### Leg 2 of 3 — adds a parallel Office (AT_WORK) channel on top of the completed Residential pipeline

---

## AIM
Extend the existing GSS → BEM residential occupancy pipeline (Leg 1) into a **two-channel generator** that produces, side by side, a **Residential (AT_HOME)** channel and an **Office (AT_WORK)** channel from the same GSS Canada Time-Use cycles (2005–2022), augmented via the same Conditional Transformer backbone and forecast to 2030. The residential channel **replaces** baseline BEM schedules; the office channel **modulates** code-compliant densities. This asymmetry is the central design choice of Leg 2.

> **Three-leg roadmap.** **Leg 1 = Residential (AT_HOME)** — COMPLETE, shipped as the 2nd Journal. **Leg 2 = 2-channel split (Residential + Office)** — *this document*, the middle step where we learn the split process. **Leg 3 = 4-channel split (+ Retail + Hotel)** — the 3rd-Journal target, documented separately.
>
> **Status convention.** Residential sub-steps reuse Leg-1 machinery and are tagged **✅ DONE (Leg 1, unchanged)**. The Office delta is tagged **⚠️ PLANNED (Leg 2)**. This is a planning document — no code is written or run in this step. Numbers and thresholds are sourced from `00_research_synthesis.md` and `00_GSS_split_suitability_audit.md`; the format mirrors the Leg-1 pair `00_GSS_Occupancy_Pipeline.md` / `_Overview.md`.

---

## STEP 1 — DATA COLLECTION & COLUMN SELECTION
*Reuse Leg-1 column set; add the office employment-gating variables.*

### 1A. GSS Main File Variables — Office gating additions

The residential Main-file selection (occID, SURVYEAR, SURVMNTH, PR, HHSIZE, AGEGRP, SEX, MARSTH, KOL, ATTSCH, NOCS, LFTAG, COW, HRSWRK, CMA, POWST, TOTINC, weights) is reused unchanged from Leg 1. Office requires the following additional employment-gating variables, whose raw names differ per cycle:

| Unified role | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 (GSSP) | Office use |
|---|---|---|---|---|---|
| Main activity last week | `MAR_Q100` | `ACT7DAYS` | `ACT7DAYS` | `ACT7DAYC` | Confirm respondent was working (vs student/retired) |
| Worked last week (Y/N) | via `MAR_Q100` | `WKLTWE` | `MRW_D40B` | `MRW_D40B` | Gate AT_WORK to employed |
| Labour-force status | `LFSGSS` | `LFSGSS` | derived | derived | Exclude retired/unemployed |
| Hours worked / week | `WKWEHR_C` | `WKWEHR_C` | `WHWD140C` / `WHW_D141` | `WHWD140G` | Cross-check diary AT_WORK hours |
| Class of worker | `MAR_Q172` | `MAR_Q172` | `WET_120` * | `WET_120` | NOC×NAICS archetype (Step 5) |
| Occupation (NOC) | `SOC91C10` | `NOCS2006_C10` | `NOC1110Y` | `NOCLBR_Y` | Office vs non-office bucket |
| Industry (NAICS) | `NAICS2002_C16` | `NAICS2007_C16` | `NAIC12CY` | `NAIC22CY` | Office vs non-office bucket |
| Telework / WFH | — | `MAR_Q190` | `WTI_130` | `TLWK_01A–D`, `TLWK_02G` | Isolate WFH from physical office |

> `*` `WET_120` (class of worker) is suppressed in the 2015 PUMF — fall back to NOC/NAICS for archetype assignment that cycle. Source: `00_GSS_split_suitability_audit.md` §A.

### 1B. GSS Episode File Variables

The episode selection is reused unchanged from Leg 1 (occID, EPINO, DDAY, start/end, startMin/endMin, duration, occACT→14 categories, occPRE, 9 co-presence cols, weights). The key fact for Leg 2:

| Derived flag | Source | Logic | Availability |
|---|---|---|---|
| `AT_HOME` | `occPRE` | `occPRE == 1` → 1 | All cycles ✅ DONE (Leg 1) |
| `AT_WORK` | `occPRE` | `occPRE == 2` → 1 | All cycles ⚠️ PLANNED (Leg 2) |

> **Key finding (audit §A).** `occPRE` already carries the harmonized 18-category location scheme on **every episode row in all four cycles**. AT_WORK is therefore *already present in the data* — no new survey variable is needed. The only build work is tiling it into the per-slot arrays (Step 3).

---

## STEP 2 — DATA HARMONIZATION
*Confirm `occPRE == 2` = workplace across all four cycles; handle the WFH coding wrinkle.*

### 2A. AT_WORK location-code crosswalk

`occPRE == 2` is the harmonized "workplace" code. The raw location values it is built from differ per cycle (already mapped by the Leg-1 harmonizer `02_harmonizeGSS.py`):

| Unified | 2005 (C19) | 2010 (C24) | 2015 (C29) | 2022 (GSSP) | Status |
|---|---|---|---|---|---|
| `occPRE == 2` (workplace) | `PLACE = 02` "Work place" | `PLACE = 02` | `LOCATION = 301` "At work or school" | `LOCATION = 3301` "At work or school" | ✅ Confirmed all cycles |

> **Work-vs-school gating (2015/2022).** In 2015/2022 the raw code conflates work and school. Isolate true workplace by gating on the Step-1A employment variables (must be working last week, employed labour-force status). 2005/2010 codes are workplace-only and need no gating. Source: audit §2.

### 2B. WFH coding wrinkle (the one harmonization subtlety)

> **2022 paid-work-at-home is coded `LOCATION = 3300 (home)`, not work** — so the raw "at work" share looks suppressed (≈6.1% vs ~7%+ pre-COVID), while 17.4% of employees teleworked from home that week (audit §5). **For an office-zone BEM this is exactly correct**: a WFH worker is physically absent from the office, so the office channel should *not* count them. The WFH signal is recovered separately via `TLWK_01A` (2022) / `WTI_130` (2015) / `MAR_Q190` (2010) and fed to the Step-6 forecast, not the office presence channel.

---

## STEP 3 — MERGE & TILING (THE ONE REAL BUILD DELTA)
*Tile AT_WORK into the 48-slot arrays. This is the only genuinely new data-engineering work in Leg 2.*

### 3C. The slot-tiling gap

The Step-3C tiler currently expands **only `AT_HOME`** into the 144→48 per-slot arrays the Transformer consumes (`act30_*`, `hom30_*`). `occPRE` — and therefore AT_WORK — lives only at the **episode** level and never reaches the slot grid.

> **The gap, plainly.** Every episode row already knows "this person was at work from 09:00–17:00." But the model only ever sees the *home* track tiled across the 48 half-hour slots. Leg 2 must tile the *work* track the same way. Source: audit §6.

### 3E. Option B — list-driven tiling (recommended fix)

We do **not** invent new machinery. The repo already ships a **9-channel list-driven tiler** for co-presence — `tile_copresence_to_30min` in `03_mergingGSS.py:821–944` — that does exactly this for nine binary channels in one pass. Point it at the occupancy channels:

```python
# Before the tiling loop, derive the binary work track (mirrors AT_HOME):
episodes_sorted["AT_WORK"] = (episodes_sorted["occPRE"] == 2).astype(float)
BINARY_CHANNELS = ["AT_WORK"]      # Leg 3 will append "AT_RETAIL", etc.

# Reuse the proven co-presence pattern, unchanged in shape:
#   COP_COLS list ............................. 03_mergingGSS.py:821–824
#   4 AM-origin slot math (startMin-240)%1440 . 03_mergingGSS.py:889
#   binary majority vote  sum_present >= 2 ..... 03_mergingGSS.py:903–918
#   column naming  f"{col}30_{i:03d}" .......... 03_mergingGSS.py:924
# → emits WORK30_001 .. WORK30_048
```

| Decision | Choice | Rationale |
|---|---|---|
| Empty-slot fill | leave `NaN` then ffill/bfill like AT_HOME | Keeps work track consistent with the home track the model already trusts |
| Binary encoding | use **1/0** (match AT_HOME), not co-presence's 1/2 | One encoding across both occupancy channels → no head-specific decoding |
| Output routing | **conservative variant**: clone the tiler to a *separate* CSV; leave the residential Phase F/H path bit-identical | Zero risk to the published residential results; the office channel is purely additive |

> **Verdict (audit §9.6).** "Option B is fully applicable and low-risk. We are not inventing machinery — we are pointing an existing 9-channel list-driven tiler at the occupancy channels." Effort: small-to-medium; risk: low.

---

## STEP 4 — MODEL 1: MULTI-HEAD CONDITIONAL TRANSFORMER
*Shared encoder (reuse J3) + a second output head for AT_WORK. The new machinery is the multi-head training discipline, not the wiring.*

### Architecture

```
ENCODER (shared — reuse J3 6-layer, d_model 384)
  Input slot token = [occACT (14-cat), AT_HOME, AT_WORK, 9 × co-presence]
  Conditioning     = [demog, DDAY_STRATA, CYCLE_YEAR, COLLECT_MODE,
                      NOCS, COW, HRSWRK]              ← NEW for Office

DECODER (multi-head, shared cross-attention)
  Head 1 (existing): 48 activity + 48 AT_HOME + 9 × 48 co-presence
  Head 2 (NEW):      48 AT_WORK tokens (binary)
```

### Mandatory multi-head machinery (not optional)

Naïve equal-weight multi-head training collapses to a smoothed mean and kills peaks — this is the named **COP peak-collapse failure mode** we already hit in Leg 1. Synthesis Part C requires, as **Leg-2 build work, not tuning afterthoughts**:

- **Dynamic loss weighting** — SLAW (O(1), scales to many heads) or homoscedastic uncertainty weighting. *Replaces equal weighting; non-optional.*
- **PCGrad gradient surgery** — neutralises gradient conflict / negative transfer between the home and work heads.
- **Diversity-preserving loss** (not MSE-only) — MSE multi-head training smooths away the diurnal peaks.
- Note the **exposure-bias** risk in the autoregressive activity arm — the mechanism behind inference-time drift; evaluate open-loop, never by training loss alone.

### Office diurnal targets the synthetic AT_WORK must reproduce

*Source-verified 2026-06-13 against `deepResearch_Resources/Empirical Occupancy Profile Analysis.pdf` (peak/trough table) — numbers below are quoted from the report, not assumed.*

| Day type | Peak window | Peak fraction | Trough |
|---|---|---|---|
| Weekday | 09:30–11:30 & 14:30–16:30 | 0.50–0.55 (private) / 0.75–0.80 (open-plan) | lunch dip 12:00–13:30 → 0.25–0.35; **true peak ≈ 15:00**, not 17:00; night 0.02–0.05 |
| Saturday | 10:00–14:00 | 0.05–0.10 | else < 0.02 |
| Sunday | 11:00–13:00 | < 0.05 | else < 0.01 |

> **Weekly shape — two regimes (attribute carefully).** Pre-COVID / general sensor data (INL): **Monday highest**, Friday lowest (depart ~30 min earlier), Tue–Thu indistinguishable. Post-COVID hybrid (Kastle, `Office Occupancy vs. WFH Trends.pdf`): **Tue–Thu peak, Mon/Fri light**; peak-day ≈ 62% of Feb-2020, weekly avg ≈ 52–55%; ~25% of desks never used. Use the **hybrid** regime for the 2022/2030 channel and the Monday-peak regime for 2005–2015. ASHRAE Schedule AA assumes 95–100% → over-predicts presence by **46% (private) / 12% (open-plan)** (Empirical report). These are validation targets, not training inputs.

---

## STEP 5 — ARCHETYPE LINKAGE
*Residential keeps the Census linkage; Office swaps in a NOC × NAICS lookup.*

### Residential — ✅ DONE (Leg 1)
Reuse the Census-GSS probabilistic linkage (K-means archetypes → Random Forest assignment → building-variable aggregation) unchanged.

### Office — ⚠️ PLANNED (Leg 2)
Census dwelling linkage does not apply to office zones. Replace it with a **NOC × NAICS → office-archetype lookup**:

| Bucket | NOC / NAICS family | Office archetype |
|---|---|---|
| Knowledge / professional | management, business/finance | OpenOffice + ClosedOffice mix, 9-to-5, low evening |
| Public sector / health / education | health, education, government | OpenOffice + Classroom + Restroom, regular hours |
| Sales / customer-facing | sales / services | mixed hours, weekend non-zero |
| Trades / production | trades, manufacturing, transport | **not office → excluded from this channel** |

Output: a per-respondent `office_archetype_ID` carried alongside the AT_WORK schedule into the BEM step.

---

## STEP 6 — MODEL 2: FORECAST 2030 + WFH
*Reuse progressive fine-tuning; add an explicit WFH scalar and report three sensitivity bands.*

The four-stage progressive fine-tuning (W_2005 → W_2010_ft → W_2015_ft → W_2022_ft with per-transition DRIFT_MATRIX) is reused from Leg 1. For Office, the **2015 → 2022 drift explicitly captures the COVID WFH jump**, surfaced as a derived scalar `WFH_RATE = mean(work-from-home during business hours | employed)`.

| Year | Canada WFH share | Note |
|---|---|---|
| 2019 | ~7% | pre-pandemic baseline |
| 2020 | ~40% | April 2020 lockdown |
| 2022 | ~30% (Jan) | COVID step change captured by DRIFT_MATRIX_1522 |
| 2023 | ~20% | partial return |
| **2030** | **forecast** | Model-2 output |

**2030 must be reported as three sensitivity bands** (synthesis Part G) — this single scalar dominates the office EUI trajectory:

- **Conservative Return** — WFH 15–20% (offices 80–85% filled)
- **Hybrid Equilibrium** — WFH ~30% (70% in office)
- **Fully Hybrid** — WFH ~40% (60% in office)

> **Energy is non-linear.** A 20–50% occupancy cut yields only ~10–30% energy savings — fixed HVAC/ventilation and a plug-load baseload never reach zero. The forecast must preserve this, not scale energy 1:1 with headcount.

---

## STEP 7 — BEM/UBEM INTEGRATION (MODULATE, NOT REPLACE)
*The core asymmetry: residential replaces baseline schedules; office multiplies code-compliant densities.*

**Residential (✅ DONE, Leg 1):** `schedule_value(t) = presence(t)·default(t) + (1−presence(t))·baseload`; `Number_of_People = HHSIZE`.

**Office (⚠️ PLANNED, Leg 2):** keep NECB17/ASHRAE peak densities intact for code-of-record comparability; multiply the *temporal* schedules by the GSS-derived presence multiplier:

```
office_schedule(t) = code_baseline(t) × AT_WORK_fraction(t)
```

Code-of-record peak densities (verified verbatim from `Building Energy Modeling Occupancy Standards.pdf` Table, 2026-06-13):

| Standard | Occupant density | LPD | Plug/receptacle | Weekday schedule |
|---|---|---|---|---|
| NECB 2017/2020 office | 25.0 m²/person (0.040 ppl/m²) | 10.0 W/m² | 7.5 W/m² | Sched A 0.85–0.95 (09:00–17:00), 0.05 overnight |
| ASHRAE 90.1 / PNNL office | 25.0 m²/person (0.040 ppl/m²) | 6.5 W/m² (varies by vintage) | 8.0 W/m² (~0.75 W/ft²) | 0.85–0.95 (08:00–17:00), 0.05–0.10 overnight |

Coupling parameters (verified verbatim from the same report — hard-code these):

| Channel | Formula | Parameters |
|---|---|---|
| Lighting | `L(t) = max(Lmin, η·O(t)·D(t))` | `Lmin = 0.10–0.20` of peak (egress/safety); auto-off 20 min after vacancy (ASHRAE 90.1-2022); `D(t)` = daylight dimming 0–1 |
| Plug loads | `P(t) = Pbase + (1−Pbase)·O(t)` | `Pbase = 0.15–0.30`; unoccupied draw can exceed 50% of peak — **never zero** |
| Schedule resolution | `Schedule:File`, `Minutes per Item = 30` | ⚠️ **Interpolate to Timestep** = deliberate decision: `Yes` averages → compounds peak loss; `No` preserves the 30-min block |

> **Tag-2 routing.** Per IDF Space: `apartment*` → residential replace; office tags (OpenOffice, ClosedOffice, Conference, Dining, Classroom, Restroom) → office modulate; Hotel/Retail tags → skip (Leg 3); service/MEP/circulation → leave baseline. **Do NOT set `Number_of_People = HHSIZE` for office zones** — headcount comes from NECB17 density, not the GSS respondent.

---

## STEP 8 — BEM SIMULATION
*Add office zones to the paired Monte-Carlo design.* ⚠️ PLANNED (Leg 2)

Extend the Leg-1 paired Monte-Carlo campaign (one archetype IDF × many sampled schedules, frozen frame, hold IDF + TMY weather, vary only occupancy) to the **PNNL Tall / SuperTall office zones**. Office floor-area share of occupiable area: ~30% (SuperTall) / ~24% (Tall). Outputs: 8760 office load profiles + MC bands, peak-hour shift, load-shape metrics; annual EUI secondary.

---

## STEP 9 — ACTIVITY-DRIVEN END-USE LOADS
*Office equipment + lighting driven by AT_WORK presence.* ⚠️ PLANNED (Leg 2)

Mirror the Leg-1 activity-driven load method on the office channel: equipment and lighting end-use intensity scaled by the AT_WORK presence track (with the Step-7 Lmin/Pbase floors). Calibrate magnitude against a commercial benchmark (NRCan SCIEU / NECB schedules) analogous to the SHEU calibration used for residential.

---

## VALIDATION PLAN
*Tiered gates from synthesis Part E — applied to the AT_WORK channel per day-type.*

| Tier | Metric | Threshold |
|---|---|---|
| **1 Distributional** | KL (arrival/departure) | < 0.05 |
| 1 | 1-Wasserstein / EMD on hourly presence CDF | < 0.05 |
| 1 | Presence-rate RMS error | ≤ 5 percentage points per day-type |
| **2 Structural** | Transition-matrix Frobenius/MAE (run-level) | < 0.05 |
| 2 | Dwell-time KS test | fail to reject H₀ (p > 0.05) |
| 2 | Autocorrelation MAE, lags 1–24 h | < 0.05 |
| **3 Downstream (ASHRAE G14)** | NMBE | monthly ±5%, hourly ±10% |
| 3 | CV(RMSE) | monthly 15%, hourly 30% |
| 3 | Peak demand + **timing shift** | magnitude ±15%; **timing ≤ 1 h** |

> **⚠️ Threshold provenance (audited 2026-06-13 against `Validating Synthetic Occupancy Schedules.pdf`).** Only some of these are literature values; the rest are project-chosen. **From ASHRAE Guideline 14 (cite the standard directly, not the report):** NMBE monthly ±5% / hourly ±10% ✅, and CV(RMSE) monthly 15% / hourly 30% (these are the standard G14 values — the report's cell was blank, so cite G14). **Confirmed in the report:** C2ST ≈ 0.5 ✅, dwell-time KS "fail to reject H₀" ✅, Pareto-frontier selection ✅, exposure-bias/open-loop eval ✅. **Project-chosen (NOT sourced — the report left these cells blank):** the `< 0.05` for KL / EMD / presence-RMS / transition-Frobenius / ACF-MAE, and peak magnitude ±15% / timing ≤ 1 h. Treat the last group as our own acceptance bar, set before tuning — do not cite them to the literature.
>
> **New gates vs Leg 1.** Add **EMD/Wasserstein** (JS saturates on disjoint supports), **transition-matrix + dwell-time KS** (catches "right marginals, impossible flips"), and **C2ST** (XGBoost real-vs-synthetic, target ≈ 50% accuracy). **Select models on the Pareto frontier of Wasserstein + ACF-MAE + downstream peak — never on a single composite score** (the composite misled us in Leg 1).

---

## KEY DESIGN DECISIONS

| Decision | Rationale |
|---|---|
| Share the encoder between Residential and Office | The encoder learns universal time-of-day / day-of-week structure; only the output head is channel-specific. Saves ~½ the parameters, consistent latent space. |
| Office **modulates**, Residential **replaces** | Preserves code-compliant peak densities (W/m², people/m²) for regulatory comparability while injecting the GSS *temporal* signal where it matters. |
| `Number_of_People = HHSIZE` does NOT apply to office | Office headcount is governed by NECB17 per-m² density, not GSS household composition. |
| AT_HOME ⊕ AT_WORK mutual exclusion **NOT** enforced | Diary slots can legitimately be neither (commute, errands, third places). Forcing exclusion corrupts both channels. |
| SLAW/UW loss weighting + PCGrad are **mandatory** | Equal-weight MSE multi-head training collapses peaks (the COP failure mode). These are Leg-2 build work, not tuning. |
| Conservative tiling variant (separate CSV) | Leaves the published residential Phase F/H path bit-identical → zero risk to Leg-1 results; office is purely additive. |
| WFH exposed as an explicit model-output scalar | A single dominant lever for the 2030 office forecast; sensitivity bands are a re-run, not a retrain. |
| Pareto model selection, never composite | The Leg-1 composite chose a 2/4-gate model; per-objective frontier is the lesson learned. |
| Residential pipeline unchanged | Leg 2 ships without re-running any Leg-1 residential figures. |

---

## OPEN DECISIONS (resolve before/within Leg 2)
*Carried from synthesis §C and the audit — listed here, not silently resolved.*

1. **MDLM vs Transformer.** Stay on the safe Rank-1 multi-head Transformer (this doc's baseline), or pilot the diffusion (MDLM) upside given prior HPT work? Decide before committing Leg-2 compute.
2. **Interpolate to Timestep (Step 7).** `Yes` (averages, compounds peak loss) vs `No` (preserves the 30-min block) — pick deliberately and document.
3. **Cross-use lunch transition.** Model office→retail lunch transitions from GSS diaries (potential novelty) or treat channels independently (simpler)? Leg 2 can defer the retail side but should decide how the office lunch dip is represented.
4. **Shared-vs-separate backbone ablation.** The shared-encoder claim needs a small internal ablation for reviewer defensibility before the Leg-3 paper.
5. **Image-locked numbers — RESOLVED 2026-06-13.** Peak densities / LPD / plug W/m² and the office diurnal fractions were verified verbatim from the source PDFs (Standards + Empirical reports) and are now in Steps 4 and 7. **Caveat that remains:** the *validation thresholds* in `Validating Synthetic Occupancy Schedules.pdf` were genuinely blank (never rendered) — so NMBE/CV(RMSE) must be cited to ASHRAE Guideline 14 directly, and the `< 0.05` / ±15% / ≤ 1 h gates are project-chosen, not literature (see Validation Plan provenance note).
