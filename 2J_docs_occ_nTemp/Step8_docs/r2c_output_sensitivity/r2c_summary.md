# Round-2c Output-Level EUI Sensitivity — Summary

**Date:** 2026-06-06
**Reference:** Step-8 Round-2c task
**MC CI half-width:** 1.80% (gate 3.2 from 8F report)

## Sanity Check
- HH34299/2022 IDF wd mean: 0.7361 (expected ≈0.736, PASS)
- Joined rows: 2022 N=1200, 2030 N=1200

## Method
Cross-HH linear regression of as-run EUI on as-built daily-mean weekday occupancy,
within each (cell, year). Slope × Δocc_per_HH gives a first-order upper-bound
estimate of the EUI impact of the provenance gap.

**Note:** the slope absorbs HHSIZE and archetype-internal variation, so it
**overstates** the true dEUI/docc — i.e., results are a conservative upper bound.

## Overall Results

| Metric | 2022 | 2030 | Both |
|--------|------|------|------|
| N joined HH | 1200 | 1200 | 2400 |
| Mean \|ΔEUI%\| (level) | 2.629% | 3.241% | 2.935% |
| Worst HH \|ΔEUI%\| (level) | 18.910% | 21.451% | 21.451% |
| Worst-cell mean \|ΔEUI%\| | (see table) | (see table) | — |
| Mean \|ΔEUI%\| (paired WFH) | — | — | 4.300% |
| MC CI half-width | 1.80% | 1.80% | 1.80% |

Worst cell 2022: OtherDwelling__Toronto_5A
Worst cell 2030: OtherDwelling__Toronto_5A

## Per-Cell Table

| Cell | Year | N | Slope (kBtu/ft²/occ) | R² | Mean Δocc | Mean\|ΔEUI%\| | Worst\|ΔEUI%\| |
|------|------|---|---------------------|----|-----------|--------------|--------------|
| HighRise__Calgary_6B | 2022 | 50 | 42.8210 | 0.763 | -0.0415 | 3.150% | 9.313% |
| HighRise__Calgary_6B | 2030 | 50 | 42.8098 | 0.870 | +0.0817 | 4.738% | 13.876% |
| HighRise__Kelowna_5B | 2022 | 50 | 38.0762 | 0.628 | +0.0239 | 2.552% | 7.924% |
| HighRise__Kelowna_5B | 2030 | 50 | 32.3059 | 0.662 | +0.0028 | 3.537% | 12.118% |
| HighRise__Montreal_6A | 2022 | 50 | 35.8772 | 0.656 | -0.0435 | 2.826% | 10.142% |
| HighRise__Montreal_6A | 2030 | 50 | 42.0857 | 0.794 | -0.0146 | 2.763% | 13.011% |
| HighRise__Toronto_5A | 2022 | 50 | 46.2646 | 0.687 | +0.0017 | 3.389% | 8.726% |
| HighRise__Toronto_5A | 2030 | 50 | 35.2202 | 0.674 | -0.1138 | 3.124% | 7.373% |
| HighRise__Vancouver_5C | 2022 | 50 | 30.4974 | 0.531 | -0.0333 | 2.363% | 7.186% |
| HighRise__Vancouver_5C | 2030 | 50 | 31.8582 | 0.524 | -0.0260 | 3.405% | 10.526% |
| HighRise__Winnipeg_7A | 2022 | 50 | 45.2847 | 0.730 | -0.0629 | 3.172% | 10.772% |
| HighRise__Winnipeg_7A | 2030 | 50 | 39.0762 | 0.664 | -0.0265 | 2.909% | 10.527% |
| MidRise__Calgary_6B | 2022 | 50 | 24.2672 | 0.505 | -0.0314 | 1.172% | 3.037% |
| MidRise__Calgary_6B | 2030 | 50 | 17.8984 | 0.358 | -0.0335 | 1.069% | 4.745% |
| MidRise__Kelowna_5B | 2022 | 50 | 18.2816 | 0.326 | -0.0672 | 0.775% | 2.974% |
| MidRise__Kelowna_5B | 2030 | 50 | 22.4848 | 0.401 | +0.0406 | 1.583% | 3.788% |
| MidRise__Montreal_6A | 2022 | 50 | 24.6279 | 0.430 | +0.0145 | 1.023% | 4.980% |
| MidRise__Montreal_6A | 2030 | 50 | 26.7759 | 0.457 | -0.0501 | 1.468% | 6.411% |
| MidRise__Toronto_5A | 2022 | 50 | 20.1008 | 0.410 | -0.0205 | 0.882% | 2.357% |
| MidRise__Toronto_5A | 2030 | 50 | 17.8731 | 0.370 | -0.0260 | 0.988% | 2.447% |
| MidRise__Vancouver_5C | 2022 | 50 | 19.3193 | 0.351 | -0.0484 | 1.013% | 5.670% |
| MidRise__Vancouver_5C | 2030 | 50 | 19.7274 | 0.382 | -0.0180 | 1.041% | 3.605% |
| MidRise__Winnipeg_7A | 2022 | 50 | 25.3406 | 0.372 | -0.0756 | 0.978% | 4.037% |
| MidRise__Winnipeg_7A | 2030 | 50 | 24.8595 | 0.390 | +0.0291 | 1.424% | 5.078% |
| OtherDwelling__Calgary_6B | 2022 | 50 | 6.3906 | 0.588 | -0.0524 | 3.614% | 12.213% |
| OtherDwelling__Calgary_6B | 2030 | 50 | 6.6409 | 0.635 | -0.0149 | 4.361% | 17.952% |
| OtherDwelling__Kelowna_5B | 2022 | 50 | 6.0939 | 0.671 | +0.0328 | 3.588% | 9.706% |
| OtherDwelling__Kelowna_5B | 2030 | 50 | 6.0371 | 0.654 | -0.0135 | 4.345% | 17.393% |
| OtherDwelling__Montreal_6A | 2022 | 50 | 3.9081 | 0.277 | -0.0206 | 1.263% | 5.745% |
| OtherDwelling__Montreal_6A | 2030 | 50 | 6.1660 | 0.676 | +0.0162 | 3.124% | 10.124% |
| OtherDwelling__Toronto_5A | 2022 | 50 | 7.5211 | 0.683 | -0.0679 | 4.694% | 18.910% |
| OtherDwelling__Toronto_5A | 2030 | 50 | 7.7807 | 0.758 | -0.0101 | 4.496% | 21.451% |
| OtherDwelling__Vancouver_5C | 2022 | 50 | 7.0480 | 0.595 | +0.0069 | 4.027% | 11.095% |
| OtherDwelling__Vancouver_5C | 2030 | 50 | 5.4208 | 0.482 | -0.0097 | 3.042% | 10.144% |
| OtherDwelling__Winnipeg_7A | 2022 | 50 | 6.1947 | 0.552 | -0.0298 | 2.170% | 7.092% |
| OtherDwelling__Winnipeg_7A | 2030 | 50 | 6.2539 | 0.702 | +0.0508 | 2.979% | 9.390% |
| SingleD__Calgary_6B | 2022 | 50 | 9.3196 | 0.505 | -0.0054 | 4.013% | 14.718% |
| SingleD__Calgary_6B | 2030 | 50 | 10.6453 | 0.522 | -0.0020 | 5.504% | 15.196% |
| SingleD__Kelowna_5B | 2022 | 50 | 9.3169 | 0.625 | -0.0503 | 4.092% | 13.578% |
| SingleD__Kelowna_5B | 2030 | 50 | 9.5967 | 0.632 | -0.0169 | 5.045% | 14.536% |
| SingleD__Montreal_6A | 2022 | 50 | 7.5239 | 0.397 | -0.0064 | 2.142% | 7.496% |
| SingleD__Montreal_6A | 2030 | 50 | 5.4396 | 0.305 | -0.0336 | 2.800% | 7.887% |
| SingleD__Toronto_5A | 2022 | 50 | 7.1603 | 0.527 | -0.0991 | 2.827% | 14.156% |
| SingleD__Toronto_5A | 2030 | 50 | 7.6021 | 0.462 | -0.0274 | 4.296% | 13.896% |
| SingleD__Vancouver_5C | 2022 | 50 | 6.3125 | 0.481 | -0.0319 | 2.698% | 10.362% |
| SingleD__Vancouver_5C | 2030 | 50 | 8.1793 | 0.594 | +0.0158 | 5.624% | 13.438% |
| SingleD__Winnipeg_7A | 2022 | 50 | 11.9987 | 0.687 | -0.0180 | 4.676% | 14.498% |
| SingleD__Winnipeg_7A | 2030 | 50 | 8.5088 | 0.517 | +0.0052 | 4.110% | 11.493% |

## Classification

**VERDICT: FLAG**

- A-VERIFIED: overall mean |ΔEUI%| < 1.0% AND well inside 1.80% CI
- AMBIGUOUS: 1.0–1.8% (near CI) → recommend Round-2d 48-run spot-check
- FLAG: >1.8% → output-material; escalate

## Limitations

- First-order linear estimate; EnergyPlus is nonlinear → treat as upper bound.
- Cross-HH slope also absorbs HHSIZE/composition effects → overstates sensitivity.
- Low R² cells: occupancy is not the dominant EUI driver; gap is likely harmless
  in those cells regardless of slope magnitude.
- Peak demand is an independent non-coincident peak (electricity at summer peak,
  gas at winter peak) — serves as supplementary, not primary, evidence.
