# Figure 8 -- Per-channel EUI against the as-modelled band

**Target:** an image tool, or any plotting tool · **Style family:** DATA FIGURE, not a schematic
**Purpose:** show where each channel's 56-cell EUI distribution sits relative to its reference band.
**This is the figure that carries three of the paper's four failing gates.**
**Source of every number below:** `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_eui_by_channel.csv`,
column `eui_CFA_kWh_m2`, plotted as in `3rdJ_09_activityDrivenLoads_4split.py:875-892`. Bands are the
`BENCH` dict at `:149`.

> 🔴 **THIS IS A RESULTS FIGURE, and it is the most consequential one in the paper.**
> The gap between a box and its band IS the finding. Moving a whisker, a median or a band edge by a
> millimetre changes what the paper reports. Nothing below may be invented, adjusted, rounded,
> smoothed or re-ordered. **Never widen a band to make a box fit** - the three failures are the
> contribution, and the project rule is that no band is moved to pass.

## Chart specification

One panel, four box plots side by side.

- **x axis:** four categories in this order - `office`, `retail`, `hotel`, `residential`.
- **y axis:** `EUI [kWh/m2/yr], CFA basis`.
- **One box per channel** drawn from the five numbers in the table below, filled with the channel
  colour at about 55% opacity, **median line in black**.
- **Behind each box, a green band rectangle** spanning `lo` to `hi`, at about 10% opacity, plus a
  solid green horizontal line at `central`. The band is drawn narrower than the tick spacing so it
  reads as belonging to that channel only.
- **Residential has no band** and gets no green rectangle. That absence is deliberate and must not be
  filled in.
- **Colours** - office `#d62728`, retail `#9467bd`, hotel `#bcbd22`, residential `#1f77b4`; bands green.
- **Title:** `Per-channel EUI vs as-modelled band (green), CFA basis, all 56 cells`.

## The data. Reproduce exactly.

**Box statistics, n = 56 cells per channel**

| channel | n | min | Q1 | median | Q3 | max |
|---|---|---|---|---|---|---|
| office | 56 | 61.72 | 65.37 | 71.02 | 74.77 | 90.21 |
| retail | 56 | 63.63 | 66.30 | 75.63 | 77.60 | 96.84 |
| hotel | 56 | 203.33 | 212.82 | 260.54 | 307.67 | 318.42 |
| residential | 56 | 111.57 | 115.30 | 119.10 | 123.39 | 128.77 |

**Reference bands**

| channel | lo | central | hi | gate rule |
|---|---|---|---|---|
| office | 100.0 | 135.0 | 200.0 | all cells |
| retail | 80.0 | 110.0 | 155.0 | median |
| hotel | 180.0 | 240.0 | 300.0 | all cells |
| residential | none | none | none | no band |

## What the figure has to make visible

- **Office sits entirely below its floor.** Its maximum, 90.21, is under the 100.0 floor: not one of
  the 56 cells reaches the band. This is the failure the cover letter leads on.
- **Retail's median, 75.63, is below its 80.0 floor**, and the retail gate is scored on the median.
- **Hotel straddles its ceiling.** The box runs 203.33 to 318.42 across a band of 180 to 300, so the
  300 ceiling falls *inside* the distribution - the channel splits into two prototype clusters rather
  than missing in one direction. Do not draw hotel as a single tight box.
- A single y axis must hold 61.72 and 318.42 at once. Do not break the axis, and do not give each
  channel its own scale: the point is that these are compared on one basis.

## Output requirements

- **Minimum 4652 px on the long edge**, matching the shipped file, or a vector PDF. Elsevier requires
  500 dpi for combination art.
- No 3D, no shadows, no gradient fills.
