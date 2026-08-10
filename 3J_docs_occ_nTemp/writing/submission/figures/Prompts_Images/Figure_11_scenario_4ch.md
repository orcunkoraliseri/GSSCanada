# Figure 11 -- One-at-a-time scenario response

**Target:** an image tool, or any plotting tool · **Style family:** DATA FIGURE, not a schematic
**Purpose:** show each channel's energy response to its own occupancy lever, held one at a time, and
that the response is monotonic and directional.
**Source of every number below:** `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_scenario_response.csv`,
column `energy_pct_vs_Bcentral`, pivoted by building x city, plotted as in
`3rdJ_09_activityDrivenLoads_4split.py:932-946`.

> 🔴 **THIS IS A RESULTS FIGURE.** 36 measured values are listed below. Reproduce them exactly. The
> **sign** of each point is the finding - it is what makes the monotonicity gate directional rather
> than hand-waved - so a flipped or approximated point inverts a reported result.

## Chart specification

Three panels side by side, **shared y axis**, landscape.

- **One panel per channel**, left to right: `office`, `retail`, `hotel`.
- **x axis, each panel:** three categorical scenario tags, in the order given in each table below.
  Rotate the labels about 20 degrees.
- **y axis, left panel only:** `channel energy Δ% vs B_central`.
- **A horizontal black zero line** in every panel.
- **Four dots per scenario tag**, one per building x city cell, at their exact values. The four cells
  are `SuperTall/CLG`, `SuperTall/MTL`, `Tall/CLG`, `Tall/MTL`.
- **Colours** - office panel `#d62728`, retail panel `#9467bd`, hotel panel `#bcbd22`.
- **Panel titles** carry the lever order: office `conservative → hybrid → fullyhybrid`,
  retail `0.90 → 0.97 → 1.05`, hotel `0.92 → 1.00 → 1.05`.
- **Figure title:** `One-at-a-time scenario response (G8o / G8r / G8h), sim-side evidence`.

## The data. Reproduce exactly. Values are percent.

**Office panel**, x order `sens_office_cons` | `B_central` | `sens_office_opt`

| scenario | SuperTall/CLG | SuperTall/MTL | Tall/CLG | Tall/MTL |
|---|---|---|---|---|
| sens_office_cons | +2.21 | +1.67 | +2.45 | +1.97 |
| B_central | 0.00 | 0.00 | 0.00 | 0.00 |
| sens_office_opt | -1.93 | -1.46 | -2.19 | -1.72 |

**Retail panel**, x order `sens_retail_cons` | `B_central` | `sens_retail_opt`

| scenario | SuperTall/CLG | SuperTall/MTL | Tall/CLG | Tall/MTL |
|---|---|---|---|---|
| sens_retail_cons | -1.98 | -1.60 | -2.10 | -1.59 |
| B_central | 0.00 | 0.00 | 0.00 | 0.00 |
| sens_retail_opt | +2.40 | +1.88 | +2.50 | +1.94 |

**Hotel panel**, x order `sens_hotel_cons` | `B_central` | `sens_hotel_opt`

| scenario | SuperTall/CLG | SuperTall/MTL | Tall/CLG | Tall/MTL |
|---|---|---|---|---|
| sens_hotel_cons | -0.76 | -0.52 | -0.50 | -0.40 |
| B_central | 0.00 | 0.00 | 0.00 | 0.00 |
| sens_hotel_opt | +0.40 | +0.48 | +0.26 | +0.37 |

## What the figure has to make visible

- **Office runs the opposite way to the other two.** Its conservative lever is *positive* (more people
  on site, return to office) while retail's and hotel's conservative levers are *negative*. That sign
  reversal is deliberate and is the reason the lever order is printed in each panel title. Do not
  "correct" it into a common direction.
- **Every B_central point is exactly 0.00** by construction - it is the reference. Draw all four on
  the zero line.
- **Hotel's response is roughly four times smaller** than office's or retail's, ranging only -0.76 to
  +0.48. Because the y axis is shared, hotel must visibly flatten. Do not give it its own scale.

## Output requirements

- **Minimum 6597 px on the long edge**, matching the shipped file, or a vector PDF.
- No 3D, no shadows, no connecting lines between the scenario categories - these are three discrete
  runs, not a trend.
