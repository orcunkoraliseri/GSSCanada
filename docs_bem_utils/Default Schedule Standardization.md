# Default Schedule Standardization

Standardize default schedules across single building and neighbourhood simulations to ensure consistent baseline comparisons.

## Problem Statement

Currently, single building and neighbourhood simulations use different IDF sets with inconsistent default schedules. This inconsistency affects the comparability of Default scenario results between simulation types.

---

## Data Source and Academic References

**Schedule Data Provenance for Journal Publication**

The standard residential schedules used in this study are derived from the following authoritative sources:

1. **U.S. Department of Energy (DOE) Commercial Reference Buildings**
   - 16 common building types including "Midrise Apartment"
   - Developed to comply with ASHRAE Standard 90.1 (2004, 2010, 2013, 2016, 2019)
   - Reference: https://www.energy.gov/eere/buildings/commercial-reference-buildings

2. **OpenStudio Standards Gem (NREL)**
   - Maintained by the National Renewable Energy Laboratory (NREL)
   - Parses and distributes DOE reference building schedules
   - Reference: https://github.com/NREL/openstudio-standards

3. **Ladybug Tools Schedule Library**
   - Downloads and formats schedules from OpenStudio Standards
   - Source file: `schedule.json` (7.7 MB, 220,016 lines)

---

## Schedule Selection Rationale

**No Detached House Schedules Available**

Neither the EnergyPlus Schedules.idf library (ASHRAE 90.1-1989) nor the DOE Commercial Reference Buildings (`schedule.json`) contain schedules specifically for detached houses/single-family homes.

**Recommended: Use MidRise Apartment Schedules** as the closest residential proxy. These represent realistic dwelling unit behavior patterns.

---

## MidRise Apartment Schedule Values

Source: `BEM_Setup/Templates/schedule.json`

### Occupancy Schedule (`ApartmentMidRise OCC_APT_SCH`)

| Hour | 0-6 | 7 | 8 | 9-15 | 16 | 17 | 18-20 | 21-23 |
|------|-----|---|---|------|----|----|-------|-------|
| Fraction | 1.0 | 0.85 | 0.39 | 0.25 | 0.30 | 0.52 | 0.87 | 1.0 |

*Pattern: High night occupancy (sleeping), low daytime (work/school), evening return*

### Equipment Schedule (`ApartmentMidRise EQP_APT_SCH`)

| Hour Range | Fraction |
|------------|----------|
| 00:00-04:00 | 0.38-0.45 |
| 05:00-08:00 | 0.43-0.66 |
| 09:00-15:00 | 0.65-0.70 |
| 16:00-17:00 | 0.80-1.00 (peak) |
| 18:00-23:00 | 0.58-0.93 |

### Lighting Schedule (`ApartmentMidRise LTG_APT_SCH`)

| Hour Range | Fraction |
|------------|----------|
| 00:00-04:00 | 0.01-0.03 |
| 05:00-08:00 | 0.03-0.08 |
| 09:00-15:00 | 0.02-0.04 |
| 16:00-19:00 | 0.08-0.18 (peak) |
| 20:00-23:00 | 0.03-0.12 |

### DHW Schedule (`ApartmentMidRise APT_DHW_SCH`)

| Hour Range | Fraction |
|------------|----------|
| 00:00-04:00 | 0.01-0.08 |
| 05:00-08:00 | 0.27-1.00 (morning peak) |
| 09:00-16:00 | 0.41-0.76 |
| 17:00-20:00 | 0.73-0.86 (evening peak) |
| 21:00-23:00 | 0.29-0.61 |

### Activity Level (Metabolic Rate)

**Constant 95 W** (seated, light activity)

---

## Implementation Architecture

### Key Points

1. **`idf_optimizer.py`** = The "gatekeeper" that ensures ALL IDFs use MidRise Apartment schedules
2. **`integration.py`** = Only modifies schedules AFTER standardization (for 2025/2015/2005 scenarios)
3. **Default scenario** = Uses pure MidRise schedules (no occupancy modification)
4. **Year scenarios** = Uses MidRise as base, then applies occupancy patterns

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              ANY IDF (Single or Neighbourhood)                   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: idf_optimizer.py → standardize_residential_schedules() │
│  • Replaces EXISTING schedules with MidRise Apartment schedules │
│  • Applies to: People, Lights, Equipment, WaterUse objects      │
│  • This ensures ALL IDFs start from the SAME baseline           │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
     ┌──────────────────┐            ┌──────────────────────┐
     │  DEFAULT SCENARIO │            │  2025/2015/2005      │
     │  (No modification)│            │  (Occupancy-based)   │
     └──────────────────┘            └──────────────────────┘
                │                               │
                │                               ▼
                │            ┌─────────────────────────────────────┐
                │            │  STEP 2: integration.py →           │
                │            │  inject_schedules() /               │
                │            │  inject_neighbourhood_schedules()   │
                │            │  • Takes MidRise baseline           │
                │            │  • Applies occupancy formula:       │
                │            │    result = occ × MAX(midrise, floor)│
                │            │           + (1-occ) × baseload      │
                │            └─────────────────────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
                     ┌──────────────────────┐
                     │  Run EnergyPlus      │
                     │  Simulation          │
                     └──────────────────────┘
```

---

## Proposed Code Changes

### [MODIFY] idf_optimizer.py

1. **Add `load_standard_residential_schedules()`**: Parses MidRise Apartment schedules from `schedule.json`
2. **Add `standardize_residential_schedules()`**: Called during Default scenario preparation

### [MODIFY] integration.py

1. **Modify `inject_schedules()`**: Use standardization from `idf_optimizer` before occupancy integration
2. **Modify `inject_neighbourhood_schedules()`**: Same standardization for neighbourhood
3. **Modify `inject_neighbourhood_default_schedules()`**: Use `idf_optimizer` standard schedules instead of hardcoded profiles

---

## Verification Plan

### Automated Tests
```bash
cd /path/to/eSim
python -m pytest tests/test_integration_logic.py -v
```

### Manual Verification
1. Run Option 3 (Single building Default) - note EUI breakdown
2. Run Option 6 (Neighbourhood Default) - note EUI breakdown
3. **Expected**: Lighting/Equipment/DHW intensities within ±10%
