# 5 Results

The four subsections below move from the raw behavioural driver behind each channel (Section 5.1), to
its annual energy consequence measured against reference bands, including where that consequence fails
the bands (Section 5.2), to its reshaping of the load curve inside a single stacked building (Section
5.3), and finally to how each channel responds when its own 2030 scenario lever, and only its own lever,
is moved (Section 5.4). Every measured value in this chapter is read from the frozen deliverable of the campaign reported here.
No band value is moved and no gate verdict changes anywhere in this chapter.

---

### 5.1 Four channels move differently over 2005 to 2030

The longitudinal results cover the four historical GSS Time-Use cycles, 2005, 2010, 2015 and 2022,
simulated across all four building-city cells (SuperTall and Tall, Montreal and Calgary). Read as the
median EUI (CFA basis) across those four cells, three of the four channels genuinely vary by cycle, and
they do not move together or in the same direction.

Office is not monotonic: median EUI falls from 70.63 kWh/m2/yr in 2005 to 69.78 in 2010 (-1.21 %),
climbs to 71.29 by 2015 (+0.94 % against 2005), then falls again to 70.20 by 2022 (-0.67 %) - a
dip-rise-dip pattern rather than a trend, with the individual four-cell range never exceeding -1.48 % to
+1.18 % in any cycle. Retail moves the furthest and reverses direction outright: it declines through 2010
(median 76.36, -1.42 % vs 2005) and 2015 (median 75.84, -2.03 %), then jumps past its own 2005 baseline
by 2022 (median 79.19, +2.36 %, four-cell range +0.13 % to +4.69 %). Residential is close to flat across
all four cycles, drifting from a 2005 median of 118.73 kWh/m2/yr to 118.68 in 2022 (median change
-0.07 %, four-cell range -0.49 % to +0.09 %).

Hotel's apparent flatness across the same four cycles is a feature of the campaign design, not a
measured behavioural finding, and must be read as such. Per the scenario list (Chapter 4, §4.3), Hotel is
deliberately left uninjected, on the untouched NECB default schedule, in the 2005, 2010 and 2015
scenarios, because the ISQ/CBRE provincial tourism-statistics series behind it does not reach a matching
pre-2019 Quebec coverage (Table 7). The near-zero change recorded for hotel across those three cycles, a median of -0.003 % in 2010 and
+0.031 % in 2015 against the 2005 baseline, therefore reflects whole-building thermal coupling with the three genuinely-varying channels, not a hotel
occupancy signal. The first cycle at which Hotel is actually injected is 2022, at its observed-2022
tourism-statistics product; even there the median change against the uninjected-2005 baseline is small,
+0.09 % (four-cell range -0.39 % to +0.73 %). Hotel's real year-to-year movement is carried by the SARIMA
2030 band rather than by the historical GSS-cycle axis, and is examined directly in Section 5.4.
Figure 7 plots all four trajectories on the same cycle axis, with Hotel's 2005 to 2015 segment marked as the
uninjected NECB baseline so that its flatness is not read off the figure as a measured hotel signal.

The four channels also carry very different weight inside the same building envelope. Aggregated across
all four cycles and all four building-city cells, Hotel's median share of building energy (44.47 %) runs 24.22 percentage points
above its median share of building floor area (20.25 %), while Office's median energy share (21.42 %)
runs 13.72 points below its area share (35.14 %); Residential (energy 18.27 % vs area 17.73 %) and Retail
(2.56 % vs 3.92 %) sit close to proportional. This asymmetry between one high-intensity, low-footprint
channel and one low-intensity, high-footprint channel is the structural backdrop for the per-channel band
verdicts in Section 5.2 (Figure 8).

**Figure 7.** *(insert `Figure_07_longitudinal_4ch.png` here)* - Four-channel EUI across GSS cycles.

---

### 5.2 Per-channel EUI and the band verdicts, including the three failures

Table 5 reports per-channel EUI on a dual basis - conditioned floor area (CFA, the primary thermodynamic
metric) and gross-floor-area occupiable-share (GFA-share, a secondary stock-comparability check) - never
averaged together - against an as-modelled band (PASS criterion) and a wider empirical band (INFO
criterion only, not scored). Residential carries no as-modelled band and is reported INFO-only, 55 of 56
cells outside the empirical band (1 of 56 IN). Of the three channels that do carry a PASS/FAIL band, all
three fail, and all three are reported here at full strength, with the deciding number in the same
sentence that states the failure.

Office fails hardest: all 56 injected campaign cells sit below the 100 kWh/m2/yr floor, median 71.02
kWh/m2/yr (CFA range 61.72-90.21), and the uninjected NECB control, the code's own reference
implementation carrying no occupancy signal at all, scores 85.45 kWh/m2/yr against that same 100 floor,
so the untreated control fails too. A gate that no untreated control can pass is measuring the band, not
the model. Two candidate mechanisms for the gap were tested and both were refuted in 56 of 56 cells:
modelled heating share sits at 17 % against the band's own 35-45 %, and rebasing on service/MEP area
moves every cell further down, not up. The band's own source document additionally gives three different
floors for itself (Table 7.1 = 100.0; line 21 = 80-140; Table 2.1 = 85.0-115.0), so the floor is recorded
as contested and unsourced, not merely missed.

Hotel fails on the opposite side of its band: 28 of 56 cells FAIL, every one above the 300 kWh/m2/yr
ceiling and every one on the Tall prototype, while SuperTall clears the ceiling in all 28 of its own cells,
over a measured range of 203.33 to 318.42 kWh/m2/yr (median 260.54). The band ceiling rests on the
first-party DOE/PNNL Large Hotel, ASHRAE 90.1-2019 (ASHRAE, 2019) prototype value (284.44 kWh/m2/yr at CZ 6A, 299.28 at
CZ 7), which is 1.0 % from the ceiling's original 90.1-2004-lineage anchor of 302.21, so a vintage-mismatch
objection does not hold; what remains is that the reference archetype's own city set (Rochester /
International Falls) does not match this study's NECB-2017 Montreal / Calgary towers.

Retail fails under the gate rule actually in force, median-in-band rather than all-cells (decided in advance of the numbers): the measured median is 75.63 kWh/m2/yr, which is 5.47 % below the 80
kWh/m2/yr floor. Under an all-cells count, 12 of 56 cells sit inside the band and 44 of 56 sit below the
floor (0 above the ceiling); that per-cell tally is reported for transparency but is not the rule that
scores the gate. This 5.47 % median-to-floor gap must not be confused with a different, smaller quantity:
the retired all-cells rule was itself replaced because it was turning on a margin of only 0.15 % of its
floor (a -0.05 % shift in the median, from a separate improvement round, flipped one cell's individual
verdict) - that 0.15 % is the decision margin that justified changing the rule, not the distance between
the median and the floor, which is the 5.47 % reported above.

No band value was moved and no gate verdict was changed to produce these results; all three failures are
reported as findings about band applicability, not resolved by widening a band or by selecting whichever
rule happens to pass (Table 5). Figure 8 plots all 56 cells per channel against their own band, which is
where the three failures' different geometries are visible at once: office below its floor across the
whole cell set, hotel split into two prototype clusters on either side of its ceiling, and retail
straddling its floor with the median on the failing side.

**Figure 8.** *(insert `Figure_08_eui_4ch.png` here)* - Per-channel EUI against as-modelled bands.

---

### 5.3 Load shape and peak-hour behaviour in a stacked building

A full-day and weekday/weekend load shape is reported per channel and per whole-building total, on the
same cell grid used in Table 5. Under the central 2030 scenario the four channels do not share a peak hour. By the circular-mean weekday peak-hour metric
(median across the four building-city cells), Office peaks at 11.90 h (range 11.82-11.93 h), Residential
at 12.04 h (range 12.01-12.10 h), and Retail at 12.37 h (range 12.11-12.62 h) - all clustered around
midday - while Hotel peaks at 18.91 h (range 18.84-18.94 h), roughly seven hours later, in the early
evening. The whole-building peak lands at a median of 14.95 h
(range 14.11-15.70 h across the four cells): between the midday cluster of Office/Residential/Retail and
Hotel's evening peak, and coincident with none of the four channels' own peaks exactly. Figure 10 places
the four channel peaks and the whole-building peak on one clock face for all four building-city cells,
and Figure 9 gives the underlying weekday and weekend load-shape curves the peaks are read from.

The weekday midday-to-night contrast also differs sharply by
channel, and one channel inverts it. Retail shows the sharpest daytime concentration: median weekday
midday demand of 72.03 kW against 2.11 kW at night, a ratio near 34 to 1. Office follows at roughly 11.8
to 1 (569.33 kW midday, 48.10 kW night). Residential is far flatter, near 3.9 to 1 (347.82 kW midday,
89.53 kW night) - a floor set by continuously-operating residential end uses rather than by occupant
presence alone. Hotel is the only channel where the ratio inverts: median weekday night demand of 434.47
kW exceeds median midday demand of 335.93 kW, consistent with a guest-room channel occupied overnight
rather than during the day.

Because the four channels peak at different hours and carry different day/night profiles, the
whole-building coincidence factor - the ratio of the simultaneous building peak to the sum of the four
channels' own individual peaks - stays below 1 in every one of the four cells: median
0.941, low of 0.851 (Tall, Calgary). Occupant and use-type diversity inside one stacked building therefore
flattens the aggregate peak relative to what a simple sum of the four channels' individual peaks would
imply, the same attenuation effect reported for household diversity within a single archetype in the
two-channel construction stage, here operating across four different uses sharing one envelope instead of across
households sharing one archetype.

**Figure 9.** *(insert `Figure_09_diurnal_4ch.png` here)* - Coincident diurnal load by channel.

**Figure 10.** *(insert `Figure_10_peakhour_4ch.png` here)* - Per-channel and whole-building peak hours.

---

### 5.4 Scenario sensitivity, one lever per channel

Each of Table 2's three scenario levers, the office work-from-home band, the retail in-store share and
the hotel SARIMA band, is moved one at a time against the 2030 central scenario, with the other two held
at their central draw. Each lever moves its own channel by a margin specific to that channel and leaves the
other channels close to unmoved.

Office's own energy moves by +1.67 % to +2.45 % under the conservative work-from-home draw, which
means less home working and more office presence, and by -2.19 % to -1.46 % under the optimistic draw.
Retail's own energy moves by -2.42 % to -1.76 % under its conservative in-store-share draw and by
+1.88 % to +2.50 % under its optimistic one. Hotel moves by the smallest margin of the three, -0.76 % to
-0.40 % conservative and +0.26 % to +0.48 % optimistic, consistent with a channel whose 2030 product is a province-level monthly multiplier
applied to a fixed guest-room shape, rather than a per-household behavioural draw.

The three levers leave the channels they were not built to move close to unchanged. Under the
conservative office draw, Retail shifts by only -0.08 % to +0.02 % and Hotel by +0.004 % to +0.03 %;
under the conservative retail draw, Office shifts by -0.02 % to -0.01 % and Hotel by -0.01 % to 0.00 %;
under the conservative hotel draw, Office shifts by -0.27 % to -0.18 % and Retail by -0.23 % to
-0.16 %. Residential
is the one channel that structurally has no scenario lever of its own (Table 2): its 2030 product is
produced by the same function, keyed off the same WFH-band parameter, as Office's own product, rather than
carrying an independent draw (Chapter 4, §4.3). Residential's own energy moves by +0.06 % to +0.29 % under the
coupled office scenarios and by under 0.10 % under the retail and hotel ones, in every case the smallest movement of any channel under any lever.
The two outer 2030 bundles reproduce this same per-channel ordering when all three levers move together,
Office -2.05 % to +2.20 %, Retail -2.42 % to +2.66 % and Hotel -0.73 % to +0.45 %, close to the sum of the isolated single-lever effects above, which is the
cross-check this section relies on: each lever's effect is close to additive rather than interacting with
the other two. Figure 11 shows the three isolated levers and the two jointly-varying bundles on one
panel per channel, which is where that near-additivity is read directly rather than inferred from the
percentages above.

**Figure 11.** *(insert `Figure_11_scenario_4ch.png` here)* - Channel response to scenario levers.

---

## Sources (this chapter)

- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_longitudinal.csv` - 64 rows (4 channels x 4
  cycles x 4 building-city cells); `eui_CFA_kWh_m2`, `energy_pct_vs_2005`, `energy_share_pct`,
  `area_share_pct`, `share_delta_pp` columns; medians and ranges in Section 5.1 computed in this task
  across the four building-city cells per channel/cycle from this file.
- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_eui_by_channel.csv` and
  `writing/tables/Table_05_eui_bands.md` - Section 5.2, all band values, measured ranges, and the three
  failing-gate numbers.
- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_loadshape_peaks.csv` - 392 rows; Section 5.3
  figures computed in this task, `B_central` scenario, `peak_hour_circular`/`wd_peak_hour_circular`,
  `wd_midday_kW`, `wd_night_kW`, `coincidence_factor` columns, medians and ranges across the four
  building-city cells per channel.
- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_scenario_response.csv` - Section 5.4 figures
  computed in this task, `eui_CFA_kWh_m2`, `energy_pct_vs_Bcentral` columns, `sens_office_*`,
  `sens_retail_*`, `sens_hotel_*`, `B_cons`, `B_opt` scenario rows.
- `writing/tables/Table_02_channels.md` - the four channels, their scenario levers, and the "Residential
  has no lever" framing.
- `writing/chapters/Chapter_04_ExperimentalDesign.md`, §4.3 - the 14-scenario list, Hotel's deliberate
  absence from the 2005/2010/2015 scenarios, and the Residential/Office 2030 coupling, cross-referenced
  rather than re-derived in this chapter.
- `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py`, module docstring "Hotel absence for
  2005/2010/2015" section - independent confirmation of the Chapter 4 citation above, checked directly
  in this task.

No em dashes or en dashes.

---

**Table 5.** *(insert `Table_05_eui_bands.md` here)* - Per-channel EUI versus plausibility bands.

