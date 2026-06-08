# Round-2b WFH Delta Analysis â€” Summary

## Sanity Check (HH34299, 2022)
- IDF wd mean HH34299: 0.7361  (expected â‰ˆ 0.736)
- CSV wd mean HH34299: 0.6528  (expected â‰ˆ 0.653)

## Dataset
- Paired HHs analysed: 1200
- Cells covered: 24
- HHs skipped (missing data): 0

## Overall Metrics (h9â€“h17 midday window)
| Metric | Value |
|--------|-------|
| Midday Î”_asbuilt | +7.920 pp |
| Midday Î”_disk | +10.124 pp |
| Midday DoD (key) | -2.204 pp |
| Max |DoD| (any HH, any hour) | 200.000 pp |
| Peak WFH hour as-built | h9 |
| Peak WFH hour disk | h5 |
| Peak-hour shift | +4h |
| WFH direction preserved | 46.0% |

## Worst Cell
- HighRise__Toronto_5A: midday DoD=+19.778 pp, max|DoD|=200.000 pp, dir=52.0%

## Per-Cell Table
| Cell | N | MidDay_DoD_pp | MaxDoD_pp | Dir% | PkShift |
|------|---|---------------|-----------|------|---------|
| HighRise__Calgary_6B | 50 | -16.389 | 200.000 | 34.0% | +0h |
| HighRise__Kelowna_5B | 50 | -3.926 | 200.000 | 46.0% | +0h |
| HighRise__Montreal_6A | 50 | -5.111 | 200.000 | 50.0% | -3h |
| HighRise__Toronto_5A | 50 | +19.778 | 200.000 | 52.0% | +0h |
| HighRise__Vancouver_5C | 50 | -0.444 | 200.000 | 40.0% | +0h |
| HighRise__Winnipeg_7A | 50 | -2.611 | 200.000 | 40.0% | +0h |
| MidRise__Calgary_6B | 50 | +0.778 | 200.000 | 40.0% | -3h |
| MidRise__Kelowna_5B | 50 | -12.436 | 200.000 | 44.0% | -2h |
| MidRise__Montreal_6A | 50 | +10.685 | 200.000 | 58.0% | +0h |
| MidRise__Toronto_5A | 50 | +3.064 | 200.000 | 46.0% | +0h |
| MidRise__Vancouver_5C | 50 | -3.074 | 200.000 | 46.0% | +2h |
| MidRise__Winnipeg_7A | 50 | -9.814 | 200.000 | 50.0% | +0h |
| OtherDwelling__Calgary_6B | 50 | -1.250 | 200.000 | 46.0% | -3h |
| OtherDwelling__Kelowna_5B | 50 | +3.602 | 200.000 | 42.0% | +0h |
| OtherDwelling__Montreal_6A | 50 | -1.418 | 200.000 | 44.0% | +0h |
| OtherDwelling__Toronto_5A | 50 | -6.798 | 200.000 | 46.0% | +1h |
| OtherDwelling__Vancouver_5C | 50 | +0.519 | 200.000 | 42.0% | +0h |
| OtherDwelling__Winnipeg_7A | 50 | -9.222 | 200.000 | 54.0% | -7h |
| SingleD__Calgary_6B | 50 | +0.130 | 200.000 | 32.0% | +0h |
| SingleD__Kelowna_5B | 50 | -9.369 | 200.000 | 42.0% | -5h |
| SingleD__Montreal_6A | 50 | +3.602 | 200.000 | 60.0% | +0h |
| SingleD__Toronto_5A | 50 | -9.064 | 200.000 | 44.0% | +4h |
| SingleD__Vancouver_5C | 50 | -5.040 | 200.000 | 50.0% | +0h |
| SingleD__Winnipeg_7A | 50 | +0.917 | 200.000 | 56.0% | +0h |

## Classification
**VERDICT: CONTAMINATED**

Thresholds:
- CLEAN: midday |DoD| â‰¤ 1.0 pp AND peak_shift = 0h AND dir preserved 100%
- GREY: midday |DoD| 1.0â€“1.5 pp
- CONTAMINATED: midday |DoD| > 1.5 pp OR peak_shift â‰  0h OR direction flip

Flags raised:
- midday|DoD|=2.204pp > 1.5pp threshold
- peak-hour shift=+4h (as-built h9 vs disk h5)
- WFH direction flipped in 648 HHs (54.0%)
- worst-cell 'HighRise__Toronto_5A' midday|DoD|=+19.778pp > 1.5pp
