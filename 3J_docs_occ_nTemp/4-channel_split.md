# 4-Channel Occupancy Pipeline for Mixed-Use Tall Buildings

### Residential / Office / Retail / Hotel — GSS-Derived Schedules for Canadian Tall & SuperTall Prototypes (2005–2030)

**Scope.** This document extends `2-channel_split.md` from two channels (Residential + Office) to **four channels** (adds Retail + Hotel). It is the implementation plan for driving the PNNL Tall and SuperTall mixed-use prototypes in `BEM_Setup/Buildings/CAN_CLG` and `CAN_MTL` with longitudinally consistent occupancy from GSS Canada Time-Use cycles 2005–2022, plus a 2030 forecast.

**Prerequisite.** `2-channel_split.md` must be implemented first. This doc is a *delta* on top.

**Date created.** 2026-05-20 | **Audience.** GSSCanada / eSim 2026 team.

---

## AIM
Drive the four occupiable functional uses inside the PNNL Tall and SuperTall prototypes with channel-specific occupancy signals, each routed by Space `Tag 2`:

| Channel | Source | Drives | Floor-area share (occupiable) |
|---|---|---|---|
| **Residential** | GSS `LOCATION == 300` → `AT_HOME` | HighRiseApartment zones | SuperTall 24.1 % · Tall 24.4 % |
| **Office** | GSS workplace LOCATION codes → `AT_WORK` | OpenOffice / ClosedOffice / Conference / Classroom / Dining / Restroom | SuperTall 30.3 % · Tall 24.4 % |
| **Retail** | GSS retail / services LOCATION codes + TUI_01 shopping activity → `AT_RETAIL` | Retail Retail / Retail Back_Space / Retail Point_of_Sale / Retail Entry | SuperTall 16.1 % · Tall 24.4 % |
| **Hotel** | Statistics Canada monthly hotel-occupancy statistics (NOT GSS) | LargeHotel GuestRoom 5/6/7 / Banquet / Cafe / Kitchen / Lobby / Laundry | SuperTall 29.5 % · Tall 26.8 % |

> Service / MEP / Circulation (~52 % of *gross* floor area) stays on ASHRAE 90.1 / NECB17 defaults — **not** modulated.

---

## 1. WHY HOTEL IS A SEPARATE DATA SOURCE

GSS samples Canadian residents at their place of residence. Canadian residents are not GSS-recorded as guests in their own city's hotels, and tourists / international guests are not in the GSS frame at all. Driving hotel zones from `LOCATION` codes would systematically under-estimate occupancy. We therefore route the Hotel channel through **Statistics Canada Tourism / Monthly Hotel-Occupancy statistics** (Table 24-10-0048-01 or successor) and use it as a seasonal multiplier on NECB17 hotel baseline schedules.

---

## 2. WHAT TO DO (high-level plan, delta over `2-channel_split.md`)

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Already covered by `2-channel_split.md` | Residential + Office channels working |
| 2.2 | Identify GSS retail / services LOCATION codes per cycle | extend `workplace_codes.yml` → `location_codes.yml` |
| 2.3 | Derive `AT_RETAIL` derived column from LOCATION + TUI_01 shopping activity | updated `merged_episodes.csv` |
| 2.4 | Add a third output head to the Conditional Transformer (AT_RETAIL) | shared encoder, 3 GSS heads |
| 2.5 | Pull and harmonize Statistics Canada hotel-occupancy monthly series (2005–2022) | `hotel_occupancy_monthly.csv` |
| 2.6 | Build a 12-month → 30-min seasonal Hotel multiplier from the StatCan series | `hotel_multiplier_lookup.csv` |
| 2.7 | Forecast 2030 hotel occupancy from the StatCan trend (classical time-series, not the Transformer) | `hotel_multiplier_2030.csv` |
| 2.8 | Extend `inject_office_schedules()` to `inject_commercial_schedules()` with channel dispatch on Tag 2 | `eSim_bem_utils/commercial_integration.py` |
| 2.9 | End-to-end run on `SuperTallBuilding_90.1-2019_6A_Buffalo_NECB17_Z6_v221.idf` (Montreal) and `…_Z7A_v221.idf` (Calgary) | one EUI table per scenario × climate × channel |

---

## 3. CHANNEL-BY-CHANNEL IMPLEMENTATION

### 3.1 Residential channel
Unchanged from the existing residential pipeline. Applied only to Spaces with `Tag 2 ∈ {HighriseApartment Apartment, HighriseApartment Corridor, HighriseApartment Office}`. `Number_of_People = HHSIZE`, blended-filter on Lights / Equipment / DHW, HVAC setback.

### 3.2 Office channel
Identical to `2-channel_split.md §3`. Applied only to Spaces with `Tag 2 ∈ OFFICE_TAG2` (see §4 below). Modulates ASHRAE/NECB baseline by `AT_WORK_fraction(t)`.

### 3.3 Retail channel (NEW)

**Source signal.** GSS `LOCATION` codes for retail / services + TUI_01 shopping-activity codes. Build the binary slot indicator:

```python
ep['AT_RETAIL'] = (
    ep['LOCATION'].isin(RETAIL_LOCATION_CODES[cycle]) |
    (ep['occACT'] == 'shopping')   # TUI_01 group: shopping & services
).astype(int)
```

**Why both LOCATION and activity?** Some cycles record "errands" with a LOCATION code (store / mall) but a generic activity (e.g., "personal services"); other respondents record only the shopping activity. The OR rule covers both encodings.

**Per-cycle population multiplier.**

```python
at_retail_fraction(t) = weighted_mean(AT_RETAIL[t] | WGHT_EPI)
```

This is the fraction of the GSS population that is in retail/services at hour `t`. It peaks around 11:00–14:00 weekdays and 12:00–16:00 weekends in pre-COVID cycles.

**BEM injection.** Multiply NECB17 retail baseline schedules (People, Lights, Plug-loads) by `at_retail_fraction(t)`. **Do not** scale People count — NECB density (e.g., 3.7 m²/person for retail sales) defines the design occupant load.

**Retail archetype routing.** PNNL prototypes use a single "Retail Retail" archetype. If you later separate (e.g., grocery vs general merchandise), introduce a `retail_archetype_ID` analogous to the office archetype lookup.

### 3.4 Hotel channel (NEW, non-GSS)

**Source.** Statistics Canada monthly hotel-occupancy rate by province. Schema:

```
hotel_occupancy_monthly.csv:
  YEAR, MONTH, PR, occupancy_rate (0–1), ADR_CAD, RevPAR_CAD
```

**Per-month → per-30-min conversion.** Hotel guests are typically present 18:00–10:00 (overnight stays) and partially during the day (business travelers, late checkouts). Use a fixed diurnal *shape* `s(t)` from the NECB17 hotel guest-room schedule, scaled by the monthly StatCan rate:

```
hotel_multiplier(t, month, PR) = s(t) × StatCan_occupancy_rate(month, PR)
```

`s(t)` is a unit-normalized 48-slot curve (max = 1.0) representing the diurnal pattern; the StatCan rate scales the amplitude per month per province. This gives the GuestRoom People + Lights + Equipment schedules a longitudinally consistent monthly variation without inventing a synthetic per-guest diary.

**Forecast 2030.** Classical time-series on the monthly StatCan series, NOT the Transformer. Recommended: SARIMA(1,1,1)(1,1,1,12) per province with COVID indicator (2020-03 to 2022-06). Output 12 monthly values for 2030 per province, then multiply by `s(t)`.

**Banquet / Cafe / Kitchen / Lobby zones.** Use NECB17 baseline schedules with no occupant modulation, OR a small day-of-week shape derived from `s(t)`. Default: leave on NECB baseline (these are amenity spaces, weakly coupled to room occupancy).

### 3.5 Conditional Transformer with 3 GSS heads

```
ENCODER (shared)
  Input slot token = [occACT (14), AT_HOME, AT_WORK, AT_RETAIL,
                      9 × co-presence]                   → 14 features
  Conditioning    = [demog, DDAY_STRATA, CYCLE_YEAR, COLLECT_MODE,
                     NOCS, COW, HRSWRK]

DECODER (three heads, shared cross-attention)
  Head 1: 48 activity + 48 AT_HOME + 9×48 co-presence (residential)
  Head 2: 48 AT_WORK    (office)
  Head 3: 48 AT_RETAIL  (retail)                        ← NEW
```

Hotel does **not** go through this model.

Loss = weighted sum of per-head losses; recommended `α_resid : α_work : α_retail = 1.0 : 0.5 : 0.3` based on signal magnitude. Tune so each per-head JS divergence < 0.02 per stratum.

---

## 4. PER-SPACE ROUTING TABLE (PNNL Tall / SuperTall Tag 2 → channel)

| Tag 2 (verbatim from IDF) | Channel | Injection |
|---|---|---|
| `HighriseApartment Apartment` | Residential | per-household TUS, `Number_of_People = HHSIZE` |
| `HighriseApartment Corridor`, `HighriseApartment Office` | Residential (common areas) | residential multiplier only on Lights |
| `OpenOffice`, `ClosedOffice` | Office | NECB baseline × `AT_WORK_fraction(t)` |
| `Conference`, `Classroom`, `Dining`, `Restroom` | Office (support) | same as Office |
| `Retail Retail`, `Retail Back_Space`, `Retail Point_of_Sale`, `Retail Entry` | Retail | NECB retail baseline × `AT_RETAIL_fraction(t)` |
| `LargeHotel GuestRoom5`, `GuestRoom6`, `GuestRoom7` | Hotel | NECB hotel baseline × `hotel_multiplier(t, month, PR)` |
| `LargeHotel Banquet`, `Cafe`, `Kitchen`, `Lobby`, `Laundry`, `Storage`, `Corridor`, `Retail` | Hotel (support) | NECB baseline only (no modulation in v1) |
| `Corridor`, `Storage`, `Elec/MechRoom`, `Elevator Shaft`, `Elevator Lobby`, `Plenum Space Type`, `Main Electrical`, `Main Mechanical`, `Elevator Machine Room` | Service / MEP / Circulation | NECB baseline, **no modulation** |

> **Implementation note.** The dispatch is `Tag 2 == "<literal>"`, not a substring match. The `HighriseApartment Office` Space (1 in SuperTall, 1 in Tall) is intentionally routed to the **Residential** channel because it serves the apartment block, not the commercial office tenants.

---

## 5. HOW TO INJECT (`commercial_integration.py` skeleton)

```python
RESIDENTIAL_TAG2 = {'HighriseApartment Apartment',
                    'HighriseApartment Corridor',
                    'HighriseApartment Office'}
OFFICE_TAG2 = {'OpenOffice', 'ClosedOffice', 'Conference',
               'Classroom', 'Dining', 'Restroom'}
RETAIL_TAG2 = {'Retail Retail', 'Retail Back_Space',
               'Retail Point_of_Sale', 'Retail Entry'}
HOTEL_GUESTROOM_TAG2 = {'LargeHotel GuestRoom5',
                        'LargeHotel GuestRoom6',
                        'LargeHotel GuestRoom7'}
# everything else: leave baseline

def inject_mixed_use(idf, channels, building_meta):
    """
    channels = {
        'AT_HOME':   per-household TUS data (existing residential pipeline),
        'AT_WORK':   48-slot population fraction, per CYCLE_YEAR,
        'AT_RETAIL': 48-slot population fraction, per CYCLE_YEAR,
        'HOTEL':     hotel_multiplier(t, month, PR) lookup table,
    }
    building_meta = {'PR': 'AB' | 'QC', 'climate_zone': '6A' | '7A', ...}
    """
    for space in idf.idfobjects['SPACE']:
        tag2 = space.Tag_2
        if tag2 in RESIDENTIAL_TAG2:
            inject_residential(idf, space, channels['AT_HOME'])
        elif tag2 in OFFICE_TAG2:
            modulate_baseline(idf, space, channels['AT_WORK'], baseline='necb_office')
        elif tag2 in RETAIL_TAG2:
            modulate_baseline(idf, space, channels['AT_RETAIL'], baseline='necb_retail')
        elif tag2 in HOTEL_GUESTROOM_TAG2:
            modulate_baseline_monthly(
                idf, space, channels['HOTEL'],
                baseline='necb_hotel_guestroom',
                month_index=building_meta['month'],
                province=building_meta['PR']
            )
        else:
            pass  # leave NECB baseline untouched
```

`modulate_baseline()` rewrites the referenced `Schedule:Compact` (or `Schedule:File`) by `new(t) = baseline(t) × multiplier(t)`, keeping People / Lights / Equipment density fields unchanged.

---

## 6. CLIMATE-ZONE ROUTING

The two cities both use NECB17 but different climate zones:

| File | Climate zone | EPW |
|---|---|---|
| `CAN_CLG/*Z7A_v221.idf` | 7A (Calgary) | `CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx.epw` |
| `CAN_MTL/*Z6_v221.idf` | 6A (Montreal) | `CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx.epw` |

Confirm via `eSim_bem_utils/config.resolve_epw_path()` — already wired (per `OccIntegrationFramework.md` Task 8 / Session 8). Geometry is identical between CLG and MTL versions (verified by IDF parser: 40,846 m² / 26,750 m² match exactly), so the only differences should be climate-driven EUI deltas.

---

## 7. VALIDATION PLAN

| Layer | Check | Target |
|---|---|---|
| LOCATION mapping | per-cycle AT_RETAIL rate (weekday, 12:00–14:00) | 0.06–0.10 (matches Canadian retail employment + shopper share) |
| Transformer | JS(AT_WORK), JS(AT_RETAIL) per stratum | < 0.02 each |
| Hotel pre-COVID | StatCan QC + AB monthly occupancy 2015–2019 vs reconstructed multiplier | mean absolute error < 0.05 |
| Hotel COVID dip | 2020-04 occupancy reconstruction | recovers the StatCan low without overshoot |
| BEM | end-to-end run of `SuperTallBuilding_…_Z6.idf` Default vs 2022 (Montreal) | EUI delta is positive (more occupancy → more demand) and dominated by Office + Hotel bands |
| Floor-area sanity | reported per-channel EUI shares | match the parsed occupiable shares within ±2 pp |

---

## 8. INPUTS, OUTPUTS, FILE PATHS

| Stage | Input | Output |
|---|---|---|
| 2.2–2.3 | harmonized GSS + `location_codes.yml` | `hetus_30min.csv` with HOME + WORK + RETAIL channels |
| 2.4 | `hetus_30min.csv` + conditioning vector | model checkpoints `W_2005`, …, `W_2022_ft` (3-head) |
| 2.5 | StatCan Table 24-10-0048-01 | `0_Occupancy/external/hotel_occupancy_monthly.csv` |
| 2.6 | NECB17 hotel guest-room schedule + StatCan rates | `0_Occupancy/processed/hotel_multiplier_lookup.csv` |
| 2.7 | StatCan series → SARIMA | `0_Occupancy/forecasts/hotel_multiplier_2030.csv` |
| 2.8 | IDF + per-Space Tag 2 + four channel multipliers | modulated `Schedule:Compact` blocks in `BEM_Setup/Buildings/CAN_CLG/*.idf` and `CAN_MTL/*.idf` |
| 2.9 | Modulated IDFs + EPW | `eplusout.sql` per scenario; per-channel EUI report |

---

## 9. KEY DESIGN DECISIONS

| Decision | Rationale |
|---|---|
| Four channels, not one unified "occupant" channel | Each end-use has a distinct underlying population (household members at home, workforce at work, customers in retail, guests in hotel). Conflating them would smear the longitudinal signal that the whole project depends on. |
| Hotel sourced from StatCan tourism stats, not GSS | GSS frame excludes hotel guests by construction. Substituting GSS data here would systematically under-occupy hotel zones. |
| Office / Retail / Hotel modulate, do not replace, NECB schedules | Preserves code-of-record peak densities (W/m², people/m²) for regulatory comparability; injects only the *temporal* GSS signal. |
| Residential alone replaces baseline | Residential is per-household and idiosyncratic — peak densities are not regulated the same way; per-household replacement is the right semantic. |
| Tag 2 is the per-Space routing key | PNNL Tall/SuperTall prototypes leave `Space Type` blank; `Tag 2` is the human-readable function string carried by OpenStudio Standards. Verified by parsing both IDFs. |
| Service / MEP / Circulation (52 % gross) left on NECB baseline | No occupant-driven demand worth modeling; GSS has no signal for elevator shafts or mech rooms. |
| Hotel forecast uses SARIMA, not the Conditional Transformer | The Transformer is conditioned on individual-respondent demographics; hotel occupancy is a population-aggregate time series. Classical SARIMA is the right tool and adds negligible compute. |
| WFH-rate sensitivity bands required for the Office channel | A single dominant lever for the 2030 office EUI; sensitivity bands (e.g., WFH ∈ {0.25, 0.35, 0.45}) defuse the reviewer challenge "what if WFH normalizes?". |
| Geometry-identical CLG and MTL IDFs run as a 2-city sweep | Verified identical floor areas (40,846 / 26,750 m²); EUI deltas isolate the climate signal, holding occupancy + geometry constant. |
| 4-channel pipeline is additive on 2-channel | If retail or hotel data are unavailable for any cycle, the missing channel falls back to NECB baseline; the rest of the pipeline still produces valid output. |
| Residential channel injection is unchanged from the existing pipeline | The 4-channel extension does not invalidate any prior residential paper figures. |

---

## 10. GRAPHICAL ABSTRACT PROMPT

Used to generate `Residential-Office-Retail-Hotel_Pipeline.png`. Paste into a web-based image-generating LLM (e.g., GPT-4o image, Gemini 2.x, Claude image-gen via web).

```
Create a clean, academic graphical abstract titled
"Longitudinal Occupancy-Driven Energy Demand in Canadian Mixed-Use
Tall Buildings: GSS-Derived 4-Channel Occupancy Pipeline (2005-2030)"
in a horizontal landscape layout, flat isometric infographic style,
muted scientific palette (navy base, with four accent colors:
teal = Residential, warm orange = Office, magenta = Retail,
gold = Hotel), thin sans-serif labels, no photoreal humans.

==================================================================
LEFT PANEL (shared data source)
==================================================================
- Stacked icons:
  * Statistics Canada GSS Time-Use cycles 2005 / 2010 / 2015 / 2022
  * Canadian Census PUMF 2006 / 2011 / 2016 / 2021
  * Statistics Canada Tourism / Hotel-occupancy monthly stats
    (separate, smaller source, gold-tinted)
- One arrow labelled "GSS Episode LOCATION codes" splits into 3
  colored streams (teal, orange, magenta); a 4th stream (gold)
  emerges from the tourism source.

==================================================================
CENTER-LEFT (4 PARALLEL CHANNELS — stacked top to bottom)
==================================================================
Each channel is a thin horizontal lane with the same internal stages:
   Episode -> HETUS 48-slot diary -> Transformer head -> 2030 forecast

1) TEAL  - Residential channel
   * LOCATION = 300 (Home) -> AT_HOME presence
   * Output: per-household occupancy + metabolic schedule
   * Tag: "24 % of occupiable area"

2) ORANGE - Office channel
   * LOCATION = workplace codes -> AT_WORK presence
   * Conditioning: NOCS x Industry x WFH-rate trend
   * Output: workforce-presence multiplier
   * Tag: "30 % of occupiable area"

3) MAGENTA - Retail channel
   * LOCATION = retail/services codes -> AT_RETAIL presence
   * Conditioning: shopping activity codes (TUI_01 groups)
   * Output: customer-presence multiplier
   * Tag: "16 % of occupiable area"

4) GOLD - Hotel channel (different source!)
   * Driven by Statistics Canada tourism / monthly hotel-occupancy
     statistics, NOT GSS (Canadian residents are not GSS-sampled
     as guests in their own city's hotels)
   * Output: seasonal occupancy multiplier on ASHRAE 90.1 / NECB17
     hotel schedules
   * Tag: "30 % of occupiable area"

All four channels feed a SHARED central block:
   "Conditional Transformer (shared encoder, 4 output heads)
    + Model 2 progressive fine-tuning 2005 -> 2022 + 2030 forecast"
With three small DRIFT_MATRIX heatmap thumbnails (2005-2010,
2010-2015, 2015-2022). Highlight the COVID 2015->2022 shift with
two emphasized arrows:
    - AT_HOME 63 % -> 70.6 % (teal)
    - WFH rate jump (orange)

==================================================================
RIGHT PANEL (BEM injection — vertical building cross-section)
==================================================================
Isometric cutaway of a SuperTall building, color-banded by use,
showing the actual stack (bottom to top):
    Podium       -> Retail        (magenta)        ~16 %
    Lower-mid    -> Office        (warm orange)    ~30 %
    Upper-mid    -> Hotel         (gold)           ~30 %
    Upper floors -> Apartments    (teal)           ~24 %
    Service cores/elevators/MEP shown as a gray vertical spine
    labelled "52 % of gross floor area -- ASHRAE defaults
    (no occupant-driven modulation)"

Each color band connects horizontally to its source channel on
the left via a colored ribbon. Small labels on the building:
"PNNL Tall (26,750 m2) / SuperTall (40,846 m2) - NECB17 Z6 / Z7A
- Calgary & Montreal"

==================================================================
FAR RIGHT (output)
==================================================================
Title: "UBEM-Ready Annual Schedules, 2005-2030"
Show four miniature 24-hour schedule curves stacked vertically,
each in its channel color, all feeding into a single EnergyPlus
icon labelled "Schedule:Compact - 30-min - Weekday / Saturday /
Sunday - per Climate Zone (5A / 5B / 5C / 6A / 6B / 7A)"

==================================================================
Visual rules
==================================================================
- Flat 2D with light isometric accents, no 3D rendering
- Use icons, not photos
- All text horizontal and legible at thumbnail size
- Clear left-to-right flow with arrows
- Color discipline:
    teal      = Residential / AT_HOME
    orange    = Office / AT_WORK
    magenta   = Retail / AT_RETAIL
    gold      = Hotel / tourism stats
    navy      = shared infrastructure
    gray      = service/MEP/circulation (un-modulated)
- Keep the building cross-section to scale: residential band thinner
  than office and hotel bands, retail thinnest occupiable band,
  service/MEP shown as the dominant gray spine
```
