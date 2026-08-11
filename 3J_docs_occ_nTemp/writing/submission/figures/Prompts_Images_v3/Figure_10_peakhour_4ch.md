# Figure 10 -- Peak timing per channel, all 56 cells

**Target:** an image tool, or any plotting tool · **Style family:** DATA FIGURE, not a schematic
**Purpose:** show that the four populations peak at four different hours. **This is the figure behind
the abstract's headline claim**, so it is the least forgiving of an approximation.
**Source of every number below:** `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_loadshape_peaks.csv`,
column `wd_peak_hour_circular`, plotted as in `3rdJ_09_activityDrivenLoads_4split.py:915-929`.

> 🔴 **THIS IS A RESULTS FIGURE, and the abstract quotes it.** All 224 values are listed below, 56 per
> channel. Reproduce them; do not sample, bin, average, jitter beyond a hairline, or "tidy" the
> clusters. The whole claim is that four tight clusters sit at four separate hours, so any smoothing
> that merges two clusters destroys the result.

## Chart specification

One panel, horizontal strip / dot plot.

- **y axis:** four categories, top to bottom in this order - `office`, `retail`, `hotel`,
  `residential`. One row per channel.
- **x axis:** `weekday peak hour [h], load-weighted circular mean`, fixed limits **0 to 24**, ticks
  every 3 hours. The full 0 to 24 range must be shown even though all data sits between 11.6 and 19.0
  - the empty space is part of the message.
- **One dot per cell**, 56 per row, at its exact x value, with a very small vertical jitter (about
  0.05 of a row height) so overlapping dots stay visible. Dot opacity about 70%.
- **One black vertical tick per row** at the channel mean, drawn long and heavy so it reads as the
  summary marker.
- **Colours** - office `#d62728`, retail `#9467bd`, hotel `#bcbd22`, residential `#1f77b4`.
- **Title:** `Peak timing per channel, all 56 cells`.

## The data. Reproduce exactly.

**Summary, and the black tick position**

| channel | n | mean (tick) | min | max | sd |
|---|---|---|---|---|---|
| office | 56 | 11.86 | 11.67 | 12.05 | 0.09 |
| retail | 56 | 12.55 | 12.10 | 13.20 | 0.33 |
| hotel | 56 | 18.73 | 18.05 | 18.97 | 0.30 |
| residential | 56 | 12.04 | 11.94 | 12.12 | 0.04 |

**office, 56 values**
11.67, 11.68, 11.69, 11.69, 11.70, 11.70, 11.73, 11.74, 11.74, 11.76, 11.77, 11.77, 11.78, 11.80,
11.80, 11.82, 11.86, 11.86, 11.87, 11.87, 11.88, 11.88, 11.88, 11.88, 11.88, 11.88, 11.88, 11.88,
11.88, 11.89, 11.89, 11.89, 11.89, 11.89, 11.90, 11.90, 11.91, 11.91, 11.92, 11.92, 11.92, 11.92,
11.92, 11.93, 11.93, 11.93, 11.93, 11.93, 11.93, 11.93, 11.95, 11.95, 11.98, 12.02, 12.03, 12.05

**retail, 56 values**
12.10, 12.10, 12.10, 12.11, 12.11, 12.11, 12.11, 12.11, 12.11, 12.24, 12.24, 12.24, 12.24, 12.25,
12.25, 12.25, 12.25, 12.26, 12.35, 12.44, 12.49, 12.49, 12.49, 12.50, 12.50, 12.50, 12.50, 12.51,
12.52, 12.52, 12.54, 12.61, 12.62, 12.62, 12.62, 12.62, 12.62, 12.63, 12.63, 12.63, 12.70, 12.74,
12.79, 12.84, 12.88, 12.89, 12.96, 12.98, 12.99, 12.99, 13.07, 13.08, 13.11, 13.11, 13.17, 13.20

**hotel, 56 values**
18.05, 18.05, 18.05, 18.07, 18.09, 18.10, 18.10, 18.12, 18.50, 18.50, 18.50, 18.52, 18.54, 18.54,
18.54, 18.55, 18.79, 18.79, 18.80, 18.83, 18.83, 18.84, 18.84, 18.84, 18.87, 18.87, 18.89, 18.89,
18.89, 18.89, 18.89, 18.89, 18.90, 18.91, 18.91, 18.91, 18.91, 18.91, 18.91, 18.91, 18.91, 18.91,
18.91, 18.92, 18.92, 18.92, 18.93, 18.93, 18.93, 18.94, 18.94, 18.94, 18.94, 18.95, 18.97, 18.97

**residential, 56 values**
11.94, 11.97, 11.98, 12.00, 12.00, 12.00, 12.00, 12.00, 12.00, 12.01, 12.01, 12.01, 12.01, 12.01,
12.01, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02, 12.02,
12.02, 12.05, 12.05, 12.05, 12.05, 12.05, 12.06, 12.06, 12.06, 12.06, 12.06, 12.07, 12.07, 12.07,
12.08, 12.09, 12.09, 12.10, 12.10, 12.10, 12.10, 12.10, 12.10, 12.11, 12.11, 12.11, 12.12, 12.12

## What the figure has to make visible

- **Hotel is alone, six and a half hours to the right of everything else**, and 18.91 is its most
  frequent value - the number the abstract quotes. The gap between the hotel cluster and the other
  three is the figure's entire point.
- **Office, residential and retail are three separate clusters, not one.** They sit at 11.86, 12.04
  and 12.55, in that order, and they must not visually merge into a single midday blob. Residential
  is the tightest of all (sd 0.04) and office is slightly to its left.
- Retail is the only midday channel with real spread, reaching 13.20.

## Output requirements

- **Minimum 4622 px on the long edge**, matching the shipped file, or a vector PDF.
- No 3D, no shadows, no density smoothing or violin substitution - individual cells must remain
  individually visible.
