# Residential & Office Parallel Occupancy Pipeline (2-Channel Split)

### Longitudinal Occupancy-Driven Energy Demand in Canadian Residential and Commercial Buildings (2005–2030)

**Scope.** This document describes the *2-channel* extension of the existing residential GSS → BEM pipeline, adding a parallel **Office (AT_WORK)** channel that shares the same Conditional Transformer backbone but is injected into commercial IDFs (PNNL Tall / SuperTall, NECB17 CZ 6 / 7A) under different physics rules.

**Companion file.** `4-channel_split.md` extends this further to Retail and Hotel.

**Date created.** 2026-05-20 | **Audience.** GSSCanada / eSim 2026 team.

---

## AIM
Reuse the existing Conditional Transformer (Step 4) and Model 2 forecaster (Step 6) to produce two parallel occupancy channels:

1. **AT_HOME** (residential, already implemented) → drives apartments / single-detached zones via per-household People, Lights, Equipment, DHW and HVAC-setback schedules.
2. **AT_WORK** (new) → drives office zones via a *workforce-presence multiplier* applied on top of ASHRAE 90.1 / NECB17 baseline densities.

The Residential channel **replaces** baseline schedules; the Office channel **modulates** them. This asymmetry is the core design choice.

---

## 1. CHANNEL DEFINITIONS

| Channel | Source | Presence flag | Building target | Injection mode |
|---|---|---|---|---|
| Residential | GSS Episode, `LOCATION == 300` | `AT_HOME` (binary, per 30-min slot) | HighRise/MidRise apartment + SingleD | Replace baseline schedules with per-household TUS curves; `Number_of_People = HHSIZE` |
| Office | GSS Episode, `LOCATION ∈ {workplace codes}` | `AT_WORK` (binary, per 30-min slot) | PNNL Tall / SuperTall **office zones only** (Tag 2 ∈ {OpenOffice, ClosedOffice, Conference, Dining, Classroom, Restroom}) | Multiply ASHRAE/NECB People + Lights + Equipment schedules by GSS-derived workforce-presence vector; keep code-compliant peak densities |

> **PNNL Tall/SuperTall floor-area share** (parsed from `BEM_Setup/Buildings/CAN_CLG` and `CAN_MTL`):
> - Office = 30.3 % of occupiable area (SuperTall), 24.4 % (Tall)
> - Residential apartments = 24.1 % (SuperTall), 24.4 % (Tall)
> - Remaining 45–50 % of occupiable area = Hotel + Retail (deferred to `4-channel_split.md`)
> - Service / MEP / Circulation = ~52 % of *gross* floor area — **not** modulated by GSS

---

## 2. WHAT TO DO (high-level plan)

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Identify GSS workplace LOCATION codes per cycle (2005 / 2010 / 2015 / 2022) | `workplace_codes.yml` |
| 2.2 | Add `AT_WORK` derived column to the merged Episode dataset | updated `merged_episodes.csv` |
| 2.3 | Re-export HETUS 30-min wide format with both AT_HOME and AT_WORK channels | `hetus_30min.csv` (96 → 144 cols) |
| 2.4 | Add a second decoder head (or second output channel) to the Step-4 Conditional Transformer | shared encoder, 2 binary output heads |
| 2.5 | Build NOCS × Industry → office-archetype lookup (replaces Census dwelling linkage for the Office channel) | `office_archetype_lookup.csv` |
| 2.6 | Extend Model 2 forecasting to track WFH-rate trend explicitly (post-COVID signal) | `forecasted_AT_WORK_2030.csv` |
| 2.7 | Write a new BEM injection helper `inject_office_schedules()` that multiplies ASHRAE/NECB schedules by the AT_WORK multiplier | `eSim_bem_utils/office_integration.py` |
| 2.8 | Add IDF-level dwelling-vs-office routing (use Tag 2 to choose which channel to apply per Space) | extension of `validate_idf_compatibility()` |

---

## 3. HOW TO DO IT (implementation detail per task)

### 3.1 Workplace LOCATION codes

GSS Episode `LOCATION` is currently filtered to `== 300` (Home). Workplace is encoded by separate codes that vary per cycle. Build a per-cycle YAML:

```yaml
# workplace_codes.yml
2005: [610, 611, 612, 613]    # confirm against GSS PUMF documentation
2010: [610, 611, 612, 613]
2015: [110, 111, 112]         # 2015 redesign renumbered LOCATION
2022: [110, 111, 112]
```

**Validation:** for each cycle, `AT_WORK == 1` slots must (a) be non-zero only for respondents with `LFTAG ∈ {employed, self-employed}`, and (b) align with their `HRSWRK` total hours per week. Flag respondents where the diary `AT_WORK` hours diverge from `HRSWRK` by > 50 %.

### 3.2 Derive AT_WORK in the merged dataset

Mirror the `AT_HOME` derivation step in the existing pipeline:

```python
ep['AT_WORK'] = ep['LOCATION'].isin(WORKPLACE_CODES[cycle]).astype(int)
# AT_HOME and AT_WORK are mutually exclusive only in well-behaved diaries;
# do NOT enforce mutual exclusion — third places (commute, errands) are
# legitimately neither.
```

### 3.3 HETUS 30-min export with two channels

After the existing 144→48 slot downsampling, export a wider matrix:

```
hetus_30min.csv columns:
  occID, CYCLE_YEAR, DDAY_STRATA, COLLECT_MODE,
  ACT_1..ACT_48,        # 14-category activity tokens
  HOME_1..HOME_48,      # binary AT_HOME tokens
  WORK_1..WORK_48       # binary AT_WORK tokens  ← NEW
```

Majority-vote rule for AT_WORK aggregation: identical to AT_HOME (3 consecutive 10-min slots → 30-min; ties broken by presence = 1 > 0).

### 3.4 Transformer with two output heads

Reuse the Step-4 Conditional Transformer encoder unchanged. Add a second decoder head:

```
ENCODER (shared)
  Input slot token = [occACT (14), AT_HOME, AT_WORK, 9 × co-presence]  → 13 features
  Conditioning    = [demog, DDAY_STRATA, CYCLE_YEAR, COLLECT_MODE,
                     NOCS, COW, HRSWRK]                                ← NEW for Office

DECODER (two heads, shared cross-attention)
  Head 1: 48 activity tokens + 48 AT_HOME tokens + 9 × 48 co-presence (existing)
  Head 2: 48 AT_WORK tokens  ← NEW
```

Loss = `α₁ × residential_losses + α₂ × BCE(AT_WORK, target)`. Recommended `α₂ = 0.5` to start; tune on a validation set so AT_WORK JS divergence per stratum < 0.02.

### 3.5 NOCS × Industry → office-archetype lookup

Census dwelling linkage (Step 5) does not apply to office zones. Replace it with a NOCS × Industry classification step:

| Bucket | NOCS codes (illustrative) | Office archetype |
|---|---|---|
| Knowledge / professional | 1, 2 (management, business/finance) | OpenOffice + ClosedOffice mix, 9-to-5, low evening |
| Public sector / health / education | 3, 4 (health, education, gov) | OpenOffice + Classroom + Restroom, regular hours |
| Sales / customer-facing | 6 (sales / services) | mixed-hours, weekend non-zero |
| Trades / production | 7, 8, 9 (trades, manufacturing, transport) | not office → exclude from this channel |

Output: a per-respondent `office_archetype_ID` carried alongside the AT_WORK schedule into the BEM step.

### 3.6 Forecast 2030 with WFH-rate signal

In `Model 2 — Progressive Fine-Tuning`, the **2015 → 2022 DRIFT_MATRIX** for the AT_WORK channel will explicitly capture the COVID WFH jump. Add a derived scalar `WFH_RATE = mean(AT_HOME during business hours | LFTAG == employed)` per cycle, and surface it as a model output:

```
2005  WFH_RATE ≈ 0.05–0.08
2010  WFH_RATE ≈ 0.07–0.10
2015  WFH_RATE ≈ 0.10–0.13
2022  WFH_RATE ≈ 0.30+        ← COVID step change
2030  WFH_RATE = forecast      ← Model 2 output
```

The 2030 forecast for the Office channel **must** be reported with WFH-rate sensitivity bands (e.g., 0.25 / 0.35 / 0.45) because this single scalar dominates the office EUI trajectory.

### 3.7 BEM injection: multiplier instead of replacement

The residential pipeline does:

```
schedule_value(t) = presence(t) × default(t) + (1 − presence(t)) × baseload
```

The office pipeline does **not** replace ASHRAE/NECB schedules. Instead, it multiplies:

```
office_schedule(t) = ASHRAE_baseline(t) × workforce_multiplier(t)
                     where workforce_multiplier(t) = AT_WORK_fraction(t)
```

`AT_WORK_fraction(t)` is the GSS-derived population-level fraction of employed respondents who are at work at hour `t`, weighted by `WGHT_EPI`. Pseudocode (`eSim_bem_utils/office_integration.py`):

```python
def inject_office_schedules(idf, at_work_vector, archetype):
    OFFICE_TAG2 = {'OpenOffice', 'ClosedOffice', 'Conference',
                   'Dining', 'Classroom', 'Restroom'}
    for space in idf.idfobjects['SPACE']:
        if space.Tag_2 not in OFFICE_TAG2:
            continue
        zone = space.Zone_Name
        # Find People, Lights, ElectricEquipment objects for this zone
        # Keep Number_of_People per floor area as-is (NECB17 default)
        # Multiply schedule references by AT_WORK_fraction(t)
        modulated = baseline_schedule(t) * at_work_vector[t]
        write_schedule_compact(idf, zone, modulated, archetype)
```

> **Do NOT** set `Number_of_People = HHSIZE` for office zones — the count comes from NECB17 per m² density, not from the GSS respondent.

### 3.8 IDF routing

Extend the existing `validate_idf_compatibility()` to dispatch per-Space:

```python
for space in idf.idfobjects['SPACE']:
    if 'apartment' in space.Tag_2.lower():
        residential_inject(space, household)
    elif space.Tag_2 in OFFICE_TAG2:
        office_inject(space, at_work_vector)
    elif space.Tag_2 in HOTEL_OR_RETAIL_TAG2:
        skip()              # left to 4-channel_split.md
    else:
        leave_baseline()    # service / MEP / circulation
```

---

## 4. VALIDATION PLAN

| Layer | Check | Target |
|---|---|---|
| LOCATION mapping | AT_WORK rate per cycle per LFTAG | Employed full-time: 0.30–0.45 of waking hours; retired: < 0.02 |
| Transformer | JS(AT_WORK_synthetic, AT_WORK_observed) per stratum | < 0.02 |
| Forecast | 2022 WFH_RATE prediction (from W_2015_ft) vs observed | within ±0.05 |
| BEM injection | Office EUI delta Default vs 2022 (Calgary CZ 7A) | non-zero and directionally consistent with WFH jump |
| Reproducibility | Same code reproduces the Image-#1 pipeline end-to-end on HH 4893 + a single NECB17 office zone | bit-for-bit match within E+ numerical noise |

---

## 5. INPUTS, OUTPUTS, FILE PATHS

| Stage | Input | Output |
|---|---|---|
| 2.1 | GSS Episode raw files | `eSim_occ_utils/configs/workplace_codes.yml` |
| 2.2–2.3 | harmonized GSS Episode + Main | `0_Occupancy/processed/hetus_30min.csv` (with HOME + WORK channels) |
| 2.4 | `hetus_30min.csv` + conditioning vector | model checkpoint `W_2005`, `W_2010_ft`, `W_2015_ft`, `W_2022_ft` |
| 2.5 | Census + GSS | `0_Occupancy/processed/office_archetype_lookup.csv` |
| 2.6 | Model 2 + scenario features | `0_Occupancy/forecasts/at_work_2030.csv` |
| 2.7 | per-cycle aggregated AT_WORK + ASHRAE/NECB IDF | modulated `Schedule:Compact` blocks written into `BEM_Setup/Buildings/CAN_*/*.idf` |
| 2.8 | IDF + per-space Tag 2 | per-Space dispatch log |

---

## 6. KEY DESIGN DECISIONS

| Decision | Rationale |
|---|---|
| Share encoder between Residential and Office channels | The encoder learns universal time-of-day / day-of-week structure; only the output projection is channel-specific. Saves ~½ the parameters and gives consistent latent representations across channels. |
| Office channel modulates (not replaces) ASHRAE/NECB baseline | Preserves code-compliant peak densities (W/m², people/m²) required for code-of-record comparisons; injects the *temporal* GSS signal where it matters. |
| `Number_of_People = HHSIZE` does NOT apply to office zones | Office headcount is governed by NECB17 per m² density (typically 18.6 m²/person for OpenOffice), not by GSS household composition. |
| Use Tag 2 (not Tag 1, not Space Type) as the routing key | PNNL Tall/SuperTall prototypes leave Space Type empty; Tag 2 carries the human-readable function string used by OpenStudio Standards. |
| WFH rate exposed as an explicit model-output scalar | A single dominant lever for the 2030 office EUI forecast; makes sensitivity bands trivial to compute (re-run with WFH ∈ {0.25, 0.35, 0.45}) without retraining. |
| Mutual exclusion AT_HOME ⊕ AT_WORK is NOT enforced | Diary slots can legitimately be neither (commute, errands, third places). Forcing exclusion would corrupt both channels. |
| Service / MEP / Circulation left on baseline | These ~52 % of gross floor area have no occupant-driven demand worth modeling; GSS has nothing to say about elevator shafts. |
| Residential pipeline unchanged | The Office channel is *additive*: residential outputs are bit-identical to the pre-2-channel pipeline, so this work can ship without re-running the residential paper figures. |

---

## 7. GRAPHICAL ABSTRACT PROMPT

Used to generate `Residential-Office_Pipeline.png`. Paste into a web-based image-generating LLM (e.g., GPT-4o image, Gemini 2.x, Claude image-gen via web).

```
Create a clean, academic graphical abstract titled
"Longitudinal Occupancy-Driven Energy Demand: Residential & Commercial
Parallel Pipeline (GSS Canada 2005–2030)" in a horizontal landscape layout,
flat isometric infographic style, muted scientific palette
(navy, teal, warm orange accents), thin sans-serif labels,
no photoreal humans.

Structure as TWO parallel horizontal tracks sharing a common DATA SOURCE
on the far left and converging into a single OUTPUT panel on the far right.

LEFT (shared source):
  - Icon of Statistics Canada GSS Time-Use cycles 2005 / 2010 / 2015 / 2022
  - Below it: Canadian Census PUMF 2006 / 2011 / 2016 / 2021
  - Arrow labelled "LOCATION codes split"

TOP TRACK (Residential, label it in teal):
  1. Episode -> AT_HOME (LOCATION = 300)
  2. HETUS 48-slot diary (30-min resolution)
  3. Conditional Transformer -> 3 DDAY_STRATA per respondent
  4. Census-GSS probabilistic linkage -> dwelling archetype
     (single-detached / MidRise / HighRise apartment)
  5. EnergyPlus injection: Number_of_People = HHSIZE,
     per-household People + Lights + Equipment + DHW + HVAC setback
  6. Small icon: MidRise apartment building

BOTTOM TRACK (Commercial, label it in warm orange):
  1. Episode -> AT_WORK (LOCATION = workplace codes)
  2. Same HETUS 48-slot diary, AT_WORK channel
  3. SAME Conditional Transformer (shared weights, dual output head)
  4. NOCS x Industry linkage -> commercial archetype
     (Office / Retail / Education / Mixed-use)
  5. EnergyPlus injection: ASHRAE 90.1 / NECB17 baseline densities
     MODULATED by GSS workforce-presence multiplier;
     plug-loads, lighting, HVAC setback follow
  6. Small icon: Tall + SuperTall commercial buildings (Calgary / Montreal)

BETWEEN THE TWO TRACKS (centered):
  A vertical band labelled "Model 2 - Progressive Fine-Tuning + 2030
  Forecast" with DRIFT_MATRIX_0510 / 1015 / 1522 stacked as 3 small
  heatmap thumbnails. Show the COVID 2015->2022 shift as a highlighted
  arrow (WFH rate jump on commercial; AT_HOME 63% -> 70.6% on residential).

RIGHT (converging output panel):
  - Title: "UBEM-Ready Annual Schedules, 2005-2030"
  - Small isometric Canadian city block mixing residential MidRise
    and commercial Tall buildings, each emitting a stylized hourly
    schedule curve in their track color
  - Below: small legend "EnergyPlus Schedule:Compact - 30-min - Weekday
    / Saturday / Sunday - per Climate Zone (5A / 5B / 5C / 6A / 6B / 7A)"

Visual rules:
  - Flat 2D + light isometric mix, no 3D rendering
  - Use icons, not photos
  - All text horizontal and legible at thumbnail size
  - Clear left-to-right flow with arrows
  - Top track teal, bottom track warm orange,
    shared elements in navy, accents in soft gold
```
