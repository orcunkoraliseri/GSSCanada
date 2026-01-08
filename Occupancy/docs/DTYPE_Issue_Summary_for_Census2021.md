# DTYPE Distribution Issue: Census 2021 vs Census 2006/2011

## Problem Summary

The Census 2021 filtered data has **collapsed dwelling type (DTYPE) categories** compared to Census 2006/2011, which affects the accuracy of BEM simulations.

---

## DTYPE Categories Comparison

### Census 2006 & 2011 (Detailed - 8 Categories)

| Code | DTYPE Name | Census 2006 | Census 2011 |
|------|------------|-------------|-------------|
| 1 | Single Detached | 62.3% | 62.1% |
| 2 | Semi-Detached | 5.3% | 5.3% |
| 3 | Row/Attached | 5.7% | 6.3% |
| 4 | Duplex/Apartment | 5.2% | 5.3% |
| 5 | High-Rise (5+ stories) | 6.5% | 6.8% |
| 6 | Mid-Rise (<5 stories) | 13.5% | 12.9% |
| 7 | Other Attached | 0.3% | 0.2% |
| 8 | Movable/Mobile | 1.2% | 1.1% |

### Census 2016 & 2021 (Collapsed - Only 4 Categories)

| Code | DTYPE Name | Census 2016 | Census 2021 |
|------|------------|-------------|-------------|
| 1 | Single Detached | 60.3% | 59.4% |
| 2 | Semi-Detached | 26.1% | 26.6% |
| 3 | Attached | 13.5% | 13.8% |
| 8 | Movable | 0.1% | 0.1% |

**MISSING in 2016/2021:** Codes 4, 5, 6, 7 (Duplex, High-Rise, Mid-Rise, Other Attached)

---

## The Problem

When using Census 2021 data for BEM simulations, the current DTypeRefiner ML model expands the 4 categories back to 8. However, the **output distribution doesn't match** the expected patterns from Census 2006/2011.

### Expected Distribution (from 2006/2011):
- Single Detached: ~62%
- Apartments (Mid-Rise + High-Rise): ~20%
- Semi-Detached: ~5%
- Others: ~13%

### Current ML Output (from 2021 expansion):
- Semi-Detached appears over-represented (~26%)
- Apartment breakdown may be incorrect

---

## Root Cause

The Census 2016/2021 **collapsed** multiple dwelling types into fewer categories:
- Code 2 (Semi-Detached) in 2021 may include what was previously coded as DuplexD (4), HighRise (5), MidRise (6)
- The ML model needs to correctly disaggregate these collapsed categories

---

## Required Fix

The DTypeRefiner ML model needs to:
1. **Better map the collapsed categories** - Code 2 (Semi-Detached) at 26% should be split into:
   - True Semi-Detached: ~5%
   - High-Rise Apartments: ~6-7%
   - Mid-Rise Apartments: ~13%
   - Duplex: ~5%

2. **Use additional features** to predict the detailed DTYPE:
   - BEDRM (bedroom count)
   - ROOM (total rooms)
   - HHSIZE (household size)
   - Geographic indicators

3. **Validate output distributions** against Census 2006/2011 benchmarks

---

## Data Source Files

Located in: `Occupancy/Outputs_CENSUS/`
- `cen06_filtered.csv` - 309,841 rows, 8 DTYPE categories
- `cen11_filtered.csv` - 333,008 rows, 8 DTYPE categories
- `cen16_filtered.csv` - 343,330 rows, 4 DTYPE categories
- `cen21_filtered.csv` - 361,915 rows, 4 DTYPE categories

---

## Validation Reference

The benchmark distribution from Census 2006 should be:
```
SingleD:   62.3%
SemiD:      5.3%
Attached:   5.7%
DuplexD:    5.2%
HighRise:   6.5%
MidRise:   13.5%
OtherA:     0.3%
Movable:    1.2%
```

Any ML expansion of Census 2021 DTYPE should aim to reproduce this distribution pattern.
