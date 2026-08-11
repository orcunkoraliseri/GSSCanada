# Figure 7 -- Longitudinal response 2005 to 2022, four channels

**Target:** an image tool, or any plotting tool · **Style family:** DATA FIGURE, not a schematic
**Purpose:** show that the four channels do not move together across the four GSS eras, in energy and
in weekday midday share.
**Source of every number below:** `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_longitudinal.csv`,
aggregated exactly as `3rdJ_09_activityDrivenLoads_4split.py:949-959` does it - `groupby("scenario")`
mean over the four building x city cells, reindexed to the era order.

> 🔴 **THIS IS A RESULTS FIGURE. The numbers below ARE the paper's finding.**
> Nothing here may be invented, adjusted, rounded, smoothed, extended or re-ordered. If the tool
> cannot place a point on an exact value, the figure must be produced by the plotting script instead
> (`fig_longitudinal` in the Step-9 script), not approximated by hand. A drawn approximation of a
> measured series is a fabricated result, and it will not be caught by the figure gates: `f5`'s data
> arm reads the plotting script, not the shipped image.

## Chart specification

Two panels side by side, shared x axis, landscape.

- **x axis, both panels:** four categorical eras in this order - `Y2005`, `Y2010`, `Y2015`, `Y2022`.
- **Left panel, y axis:** `energy Δ% vs 2005`. Include a horizontal zero line.
- **Right panel, y axis:** `weekday midday share` (a fraction from 0 to 1).
- **Four series** in both panels, one line each, markers at every era, straight segments between
  eras (no spline, no smoothing).
- **Legend** in the right panel only.
- **Series colours, fixed by the project theme** - office `#d62728`, retail `#9467bd`,
  hotel `#bcbd22`, residential `#1f77b4`.
- **Title:** `Longitudinal 2005 to 2022, mean over building x city`.

## The data. Reproduce exactly.

**Left panel - energy Δ% vs 2005**

| channel | Y2005 | Y2010 | Y2015 | Y2022 |
|---|---|---|---|---|
| office | 0.0000 | -1.2026 | 0.9449 | -0.6374 |
| retail | 0.0000 | -1.4358 | -2.0818 | 2.3840 |
| hotel | 0.0000 | -0.0032 | 0.0326 | 0.1281 |
| residential | 0.0000 | -0.1525 | 0.0225 | -0.1365 |

**Right panel - weekday midday share**

| channel | Y2005 | Y2010 | Y2015 | Y2022 |
|---|---|---|---|---|
| office | 0.9216 | 0.9150 | 0.9163 | 0.9189 |
| retail | 0.9787 | 0.9771 | 0.9754 | 0.9774 |
| hotel | 0.5075 | 0.5080 | 0.5078 | 0.4393 |
| residential | 0.7962 | 0.7960 | 0.7964 | 0.7962 |

## What the figure has to make visible

- In the left panel, **retail is the only channel with a large swing**, down to -2.08% by 2015 and up
  to +2.38% by 2022; hotel and residential are almost flat. Do not rescale the y axis in a way that
  hides how flat hotel and residential are.
- In the right panel, **hotel is the only channel whose midday share moves**, 0.5078 to 0.4393
  between 2015 and 2022. The other three are flat to three decimal places across seventeen years.
  That contrast is the panel's entire content, so it must survive whatever axis limits are chosen.

## Output requirements

- **Minimum 6000 px on the long edge**, or a vector PDF. Elsevier requires 500 dpi for combination
  art; the shipped version of this figure is 6012 x 2451 px at 600 dpi and any replacement must match
  or beat it.
- No decorative 3D, no shadows, no gradient fills on the lines.
