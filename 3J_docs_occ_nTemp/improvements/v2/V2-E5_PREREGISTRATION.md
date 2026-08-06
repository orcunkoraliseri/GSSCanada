# V2-E5 PRE-REGISTRATION — written before the deliverable arm was built or run

**2026-08-05, night. Local win32. Speed not touched.**

## What is being run, and why this is not another gate-chasing arm

The user's 2026-08-04 direction change stands: **stop running arms to move `S9-EUI-*`.** This run does
not violate it, and the distinction is worth stating because it is the whole justification.

V2-E5 is not an attempt to move a gate. It is the **scoring of the deliverable** — the one arm the
paper will report — under corrections that were **already decided on other grounds**:

- **V2-D9** (retail `NECB-C-*`): decided because retail was running the *office* occupant density.
  D9 measured its own effect on 4 cells and recorded that it makes `S9-EUI-retail` **worse**. It is in
  the deliverable because it is the correct input, not because it helps.
- **V2-B4 / V2-D10** (per-object DHW resize, `Laundry Service Water Use 30.6gpm 180F=8.5`, every
  other heater at K = 1): decided because the hotel DHW plant was measurably undersized — `LAUNDRY`'s
  own ln E-vs-ln V slope was **0.0182**, i.e. the burner, not the occupancy, was setting the energy.
  **The factor 8.5 was fixed by D10's peak-draw sizing before this run and without reference to the
  band.**

No third change is being introduced. Nothing here is tuned. If a gate moves, it moves because a
decided correction moved it.

## Baseline — the arm being differenced against

`Step8_docs/outputs_step8/agg`, `INJ_HASH cf69d508`, `PLATFORM win32`, 56 cells.
Scorecard **17 PASS / 3 FAIL / 10 INFO**.

| channel | rule | band | in | below | above | median |
|---|---|---|---|---|---|---|
| office | all_cells | [100, 200] | 0 | 56 | 0 | **71.0832** |
| retail | median | [80, 155] | 12 | 44 | 0 | **75.4288** |
| hotel | all_cells | [180, 300] | 28 | 28 | 0 | **178.2943** |

Hotel DHW is **37.19 %** (median; range 33.13–40.96) of hotel channel energy.
`corr(hotel EUI, hotel DHW share) = 0.7170` — the highest-EUI cells are also the ones that will rise
most, which is what makes the ceiling the live risk rather than the floor.

## Predictions

### The load-bearing one, stated first

**P1 — hotel DHW energy rises by +112 % (interval +95 … +135 %), median across 56 cells.**

Derivation, from the K = 6 measurement rather than from hope: `LAUNDRY`'s share of hotel DHW went
**26.7 % → 65.4 %**. Holding the other five heaters fixed, that implies `LAUNDRY` delivered
**5.19×** more and the hotel total **×2.118**, i.e. **+112 %**. Arm R (global K = 10) measured
**+124 %**, which brackets it from above. The deliverable is ×8.5 on `LAUNDRY` alone, so it should
land at or slightly above the K = 6 figure.

**P2 — `S9-EUI-hotel` stays FAIL, and its failing end is now the CEILING, with 1–20 cells above 300
and 0 below 180.**

This is a knife-edge call and I am recording the knife edge rather than hiding it. Propagating P1
through each cell's own DHW share:

| DHW increase | hotel EUI min / median / max | in-band | below | above |
|---|---|---|---|---|
| +80 % | 191.0 / 231.6 / 273.0 | **56** | 0 | 0 |
| +100 % | 201.8 / 245.0 / 288.8 | **56** | 0 | 0 |
| **+112 % (point est.)** | 208.3 / **253.0** / **298.4** | **56** | 0 | 0 |
| +124 % | 214.7 / 261.0 / 307.9 | 42 | 0 | **14** |
| +140 % | 223.4 / 271.6 / 320.6 | 28 | 0 | **28** |

**The gate PASSES iff the DHW increase lands between roughly +55 % and +115 %.** My point estimate
is +112 %, which is *inside* the passing window by 1.6 kWh/m² on the worst cell — a margin far
smaller than my own uncertainty. I predict **FAIL** anyway, because the deliverable is ×8.5 against
the ×6 the estimate was derived from, and every unmodelled term I can think of (the other five
heaters are no longer the binding constraint either) pushes **up**.

🔴 **Stated in advance, because it is the finding most open to a bad-faith reading: if
`S9-EUI-hotel` comes back PASS, that is a PASS I predicted against, produced by a factor fixed
before the run on peak-draw grounds.** It must be reported as a gate that changed status without
being aimed at — and the user, not I, decides whether the paper leans on it. **It does not
retro-justify 8.5.** If it passes, the honest reading is that the band and the plant sizing agree,
not that the plant was sized to the band.

**P3 — the three blocking gates do not all clear. `S9-EUI-office` and `S9-EUI-retail` both stay
FAIL.** Office is untouched by both corrections; retail is moved the wrong way by D9, by its own
measurement.

### The rest

| # | prediction | basis |
|---|---|---|
| **P4** | `S9-EUI-office`: **0/56 in band**, median moves < 0.05 % from 71.0832 | neither correction touches office; D9 measured ≤ 0.0258 % off-channel |
| **P5** | `S9-EUI-retail`: FAIL; median moves **UP** +0.06 … +0.12 kWh/m² (75.4288 → 75.49 … 75.55); in-band count 12 → 11–13 | D9's own 4-cell measurement was **+0.0932** |
| **P6** | **DHW VOLUME** unchanged ≤ 0.1 % in all four channels, all 56 cells | C1′. Draw is schedule-driven and cannot see the burner. **This is the control that can fail** — any movement means the edit was not surgical |
| **P7** | Structural gates identical: `S9-AREA` 56/56, `S9-CELLS` 56/56, `S9-SCHEMA` `db4e729f`, `S9-PLATFORM` `win32`, attribution residual 0.000000 % on every cell | no geometry or schema change |
| **P8** | All four `S9-PEAK-*` and `S9-WE-office`, `S9-COINC`, all `S9-LONG-*` keep their status; `S9-PEAK-retail` circular mean moves < 0.1 h from 13.04 h | only `LargeHotel Retail` (11.7 % of the channel) gets a new occupancy shape |
| **P9** | `G8o` / `G8r` / `G8h` all stay PASS; `G8h` spread moves most | the resize is uniform across scenarios within a cell trio |
| **P10** | **Total status changes ≤ 3, and no gate goes FAIL → PASS except possibly `S9-EUI-hotel` (P2)** | everything else is either untouched or moved by < 0.15 % |
| **P11** | `S9-BASIS` (INFO) drops **hotel** from its below-floor list | follows mechanically from P1 if the hotel median clears 180 |

### Membership, not just counts

For **every** gate whose count is unchanged, membership is checked cell-by-cell — vacuous-gate
**class #12**, which has already fired once on `S9-EUI-hotel` (28/56 in both arm H and arm R, a
*different* 28). A gate that reports the same number over a different set has not held still.

### What would make this run vacuous

If **nothing** changes anywhere, the run has still measured something: that two decided corrections
are jointly inert at gate level. That is a reportable result, not a failure. What would make it
**vacuous** is scoring only the counts and calling stability agreement — which is what P-membership
above exists to prevent.

## Method

Base cell `injected.idf` → **D9 converter** (`3rdJ_09J_retail_necb_c.py --verify`) → **D10 per-object
resize** (`3rdJ_09H_resize_campaign_cell.py … 1.0 "Laundry Service Water Use 30.6gpm 180F=8.5"`) →
EnergyPlus 24.2.0 local → §8E aggregation → `3rdJ_09_activityDrivenLoads_4split.py --agg-dir`.

Two variables move at once versus the base arm. Both were measured in isolation first (D9 on 4 cells,
D10 on the slope study), so the joint arm is the deliverable, not the attribution experiment.
