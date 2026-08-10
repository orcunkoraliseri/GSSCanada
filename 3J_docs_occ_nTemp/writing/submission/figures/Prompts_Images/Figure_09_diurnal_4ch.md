# Figure 9 -- Coincident four-channel diurnal load

**Target:** an image tool, or any plotting tool · **Style family:** DATA FIGURE, not a schematic
**Purpose:** show the four channels stacking into one building load, and that their contributions
peak at different hours, which is what produces a coincidence factor below 1.
**Source of every number below:** `Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_diurnal.csv`,
filtered to `metric == "energy_W"` (the attributed load, not the occupant count - see the Step-9
script at `:331`), `cell_tag == "B_central__SuperTall__CLG"`, `daytype == "WD"`. Plotted as in
`3rdJ_09_activityDrivenLoads_4split.py:895-912`. Values below are **kW**, that is `W / 1000`.

> 🔴 **THIS IS A RESULTS FIGURE.** 288 measured values are listed below. Every one must be placed
> where it is stated. Do not smooth, do not interpolate, do not resample to fewer hours, do not
> reorder the stack. The shape of these curves is the paper's behavioural claim.

## Chart specification

Two panels side by side, **shared y axis**, landscape.

- **Left panel:** `winter, weekday`. **Right panel:** `summer, weekday`.
- **x axis, both:** hour 0 to 23, ticks every 3 hours.
- **y axis, left panel only:** `stacked load [kW]`.
- **Stacked filled areas**, six of them, stacked in **this order from the bottom up**:
  `office`, `retail`, `hotel`, `residential`, `residential_common`, `service_MEP`.
  Fill opacity about 85%, no line borders.
- **Colours** - office `#d62728`, retail `#9467bd`, hotel `#bcbd22`, residential `#1f77b4`,
  residential_common `#7f7f7f`, service_MEP `#c7c7c7`.
- **Legend** in the right panel, upper right, two columns.
- **Title:** `Coincident four-channel diurnal load, B_central__SuperTall__CLG`.

## The data. Reproduce exactly. Units kW, hour 0 to 23 left to right.

**Winter, weekday**

| channel | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| office | 151.8 | 163.0 | 171.9 | 180.7 | 183.6 | 191.7 | 807.6 | 1562.2 | 1345.5 | 1075.7 | 985.9 | 967.8 | 976.6 | 897.7 | 772.8 | 793.7 | 931.8 | 884.7 | 925.5 | 941.8 | 980.8 | 144.4 | 89.2 | 128.6 |
| retail | 7.6 | 9.0 | 10.1 | 10.9 | 11.8 | 12.6 | 66.3 | 147.5 | 116.0 | 85.5 | 78.0 | 90.8 | 85.1 | 96.6 | 94.1 | 90.3 | 75.2 | 78.0 | 82.2 | 85.1 | 88.5 | 0.0 | 1.3 | 2.4 |
| hotel | 366.8 | 356.1 | 371.8 | 378.4 | 381.0 | 403.3 | 714.1 | 1337.7 | 1037.1 | 710.7 | 609.4 | 555.7 | 545.1 | 506.2 | 466.2 | 509.1 | 598.3 | 1534.9 | 1645.3 | 1637.0 | 1647.2 | 1302.1 | 1285.0 | 1214.0 |
| residential | 129.5 | 109.3 | 88.3 | 92.1 | 117.4 | 220.0 | 544.5 | 912.4 | 782.5 | 650.2 | 608.3 | 544.5 | 505.2 | 467.7 | 439.9 | 473.8 | 527.9 | 565.7 | 581.6 | 574.1 | 574.7 | 249.4 | 228.6 | 156.5 |
| residential_common | 12.6 | 11.6 | 11.4 | 11.4 | 11.2 | 11.2 | 12.9 | 48.1 | 39.5 | 32.2 | 25.6 | 21.3 | 18.4 | 16.5 | 15.4 | 15.3 | 15.7 | 15.8 | 15.9 | 16.1 | 16.2 | 12.2 | 14.2 | 13.4 |
| service_MEP | 61.6 | 59.8 | 59.4 | 59.8 | 60.4 | 67.3 | 100.5 | 417.5 | 517.8 | 535.0 | 555.1 | 571.8 | 575.6 | 579.6 | 542.3 | 516.2 | 492.1 | 376.2 | 273.1 | 240.2 | 222.0 | 176.0 | 89.4 | 66.0 |

**Summer, weekday**

| channel | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| office | 20.6 | 16.6 | 14.1 | 6.0 | 5.2 | 143.6 | 285.7 | 482.8 | 586.4 | 641.7 | 710.1 | 731.2 | 719.2 | 676.0 | 683.7 | 683.7 | 431.8 | 335.6 | 254.2 | 193.5 | 116.3 | 42.8 | 42.7 | 21.6 |
| retail | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 12.0 | 14.9 | 19.4 | 28.5 | 35.7 | 74.4 | 68.0 | 92.0 | 97.8 | 93.8 | 62.3 | 46.8 | 33.4 | 29.6 | 21.2 | 0.0 | 0.0 | 0.0 | 0.0 |
| hotel | 331.6 | 336.2 | 336.3 | 330.7 | 351.9 | 415.7 | 445.3 | 427.9 | 363.9 | 384.2 | 386.3 | 375.8 | 352.4 | 349.1 | 393.0 | 462.4 | 1231.2 | 1266.1 | 1243.3 | 1214.5 | 1216.8 | 1182.8 | 1107.2 | 349.7 |
| residential | 91.0 | 66.7 | 64.9 | 86.7 | 181.4 | 382.3 | 418.2 | 516.6 | 527.0 | 526.1 | 499.1 | 468.1 | 449.6 | 454.0 | 484.4 | 510.4 | 524.0 | 457.2 | 391.0 | 344.8 | 238.7 | 213.3 | 145.1 | 113.2 |
| residential_common | 13.5 | 13.0 | 12.3 | 12.0 | 13.6 | 12.0 | 12.0 | 13.2 | 14.0 | 14.6 | 15.4 | 15.4 | 15.6 | 16.2 | 16.7 | 16.9 | 16.2 | 15.3 | 14.5 | 13.1 | 13.7 | 15.3 | 15.8 | 15.6 |
| service_MEP | 53.5 | 51.4 | 49.7 | 50.2 | 63.5 | 116.2 | 151.7 | 274.9 | 291.9 | 296.4 | 301.4 | 299.1 | 299.4 | 305.9 | 309.3 | 309.9 | 270.7 | 180.5 | 140.5 | 121.8 | 103.4 | 60.3 | 56.1 | 55.9 |

## What the figure has to make visible

- **Office spikes at hour 7** in winter (1562.2 kW) and collapses at 21. **Hotel has a second, larger
  evening plateau** from hour 17 to 20 in winter (1534.9 to 1647.2 kW) and from 16 to 20 in summer.
  Those two humps sitting at different hours are why the building's coincidence factor is below 1.
- **Retail drops to exactly 0.0 kW** at several hours in both seasons. Zero is a measured value here,
  not missing data; draw it as zero, not as a gap.
- The winter and summer panels have very different totals. Because the y axis is shared, summer must
  visibly sit lower - do not normalise the panels to each other.

## Output requirements

- **Minimum 6058 px on the long edge**, matching the shipped file, or a vector PDF.
- No 3D, no shadows, no smoothing of the hourly steps.
