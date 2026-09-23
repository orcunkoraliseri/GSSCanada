# P3 - Code-schedule (uninjected) vs survey-driven comparison - result

Status: DONE (2026-09-22). Read-only on the frozen deliverable. No simulation. Manuscript not edited.

## Verdict (plain)

**The survey-driven model does NOT change load timing in any way that matters, compared with code schedules.
It changes occupant presence timing a great deal, and it changes the level and the day/night contrast of
office and retail energy.** Per cell:

| Cell | Whole-building peak hour, code -> 2022 / 2030 (h) | Coincidence factor, code -> 2022 / 2030 | Hour of the annual building peak (all three) |
|---|---|---|---|
| SuperTall Montreal | 13.85 -> 14.00 / 14.11 | 0.952 -> 0.964 / 0.966 | 07:00, 6 Jan |
| SuperTall Calgary | 14.02 -> 14.22 / 14.34 | 0.949 -> 0.969 / 0.965 | 07:00, 23 Jan |
| Tall Montreal | 15.22 -> 15.48 / 15.56 | 0.912 -> 0.917 / 0.916 | 07:00, 6 Jan |
| Tall Calgary | 15.31 -> 15.60 / 15.70 | 0.833 -> 0.842 / 0.851 | 07:00, 23 Jan |

- The whole-building peak hour moves by +0.16 to +0.29 h (2022) and +0.26 to +0.39 h (2030); every
  channel's energy peak hour moves by at most 0.82 h (hotel), and residential by under 0.1 h.
- The coincidence factor goes UP with the survey model, not down: +0.005 to +0.020 (2022), +0.005 to +0.017
  (2030). Code schedules give slightly MORE diversity. The code building already has "four channels peaking at
  different hours" (hotel 18.3 h against a midday cluster) and a coincidence factor below 1 (median 0.930).
  Both claims in §5.3/§6 are therefore properties of the prototype's code schedules, not of the survey model.
- The annual building peak is a winter 07:00 start-up peak in all 12 cells, identical under code and survey.
  The "whole-building peak at 14.95 h" in §5.3 is a load-weighted circular mean of the average-day profile
  (a centroid), not the hour at which the building peaks.
- What the survey model DOES change (the defensible result):
  - Presence timing: hotel guests present at night instead of daytime (presence peak hour 15 h -> 22 h, all
    cells); residents present at night instead of daytime (9 h -> 0 h in 2022, 4 h in 2030). The prototype's
    code schedules for hotel and apartments are office-shaped (near zero at night).
  - Weekday midday-to-night energy contrast (published 11-14 h vs 22-04 h definition): office 7.2 -> 11.4
    (2022) / 11.8 (2030); retail 9.3 -> 47.1 / 34.2; hotel 1.03 -> 0.78 / 0.77 (the inversion is only in 2 of
    4 cells under code, all 4 under survey); residential 3.78 -> 3.89 / 3.87 (no change).
  - Energy level: office CFA EUI -15.6 % to -20.2 % (2022) and -17.0 % to -22.7 % (2030); retail -12.2 % to
    -14.5 % and -20.2 % to -26.5 %; hotel within +-0.6 %; residential -1.0 % to -1.9 %.
- Why energy timing does not follow presence timing: the channel energy profile is set by lighting,
  equipment and HVAC schedules. Residential injection drives people only (no lights/equipment product), and
  the hotel code lighting/equipment schedules already carry an evening peak, so moving guests to the night
  barely moves hotel energy timing.
- **D3 consequence (author condition "revisit D3 if no difference"):** the condition is met for load timing -
  the timing result as currently framed (peak hours, coincidence) does not survive against code schedules.
  Recommend the paper lead instead with presence timing + day/night contrast + office/retail level vs code,
  and report the timing/coincidence non-difference honestly as a finding (energy timing in these prototypes is
  locked by plant start-up and lighting/equipment schedules). The manager/author owns the D3 revisit.

## P10 dependency

The 2030 central column depends on the 2030 products (cell manifest `INPUTS_HASH_DETAIL`, e.g.
`B_central__Tall__MTL/manifest.json`: `office_presence_multiplier_2030.csv` md5 1536c98c...,
`BEM_Schedules_4split_2030_central.csv` md5 d36388c8..., `retail_presence_multiplier_2030_central.csv`,
`hotel_schedule_multiplier_2030_central.csv`). If P10 finds a raking defect, that column moves. The code and
2022 columns do not depend on P10, and 2022 already gives the same verdict (timing non-difference; presence,
contrast and level differences). Recommendation: state the code-vs-survey comparison on 2022; keep 2030 as a
second column only after P10 clears it. Note §5.3 currently reports everything "under the central 2030
scenario", so it is fully exposed to P10.

## Definitions and provenance

All definitions are the Step-9 script's own (`Leg3_4-split/Step9_docs/3rdJ_09_activityDrivenLoads_4split.py`).

| Metric | File | Column / filter |
|---|---|---|
| Channel weekday peak hour (circular mean, argmax) | `Step8_docs/outputs_step8/agg_deliverable/agg_diurnal.csv` | `season=="all"`, `daytype=="WD"`, `metric=="energy_W"`, column `W`; circular mean as Step-9 `circular_mean_hour` (L215) |
| Whole-building peak hour (published) | `agg_deliverable/agg_peak.csv` | `channel=="_BUILDING"`, column `peak_hour_circular` (all days) |
| Whole-building weekday peak hour (new) | `agg_diurnal.csv` | sum of the six channels' WD `energy_W` profiles |
| Coincidence factor (published) | `agg_peak.csv` | `coincidence_factor` = max of the 6-channel hourly sum / sum of the 6 channel annual maxima (8E L452-455). The 6 channels include residential common space and service/MEP |
| Coincidence factor, 4 tenant channels (new) | cell files `campaign_local_deliverable/<cell>/{hourly_meters,channel_hourly,dhw_hourly}.csv` | hourly reconstruction with the 8E allocation rules; reproduces the published 6-channel value exactly (Control 3) |
| Midday/night (published) | `agg_diurnal.csv` | WD mean over 11-14 h / mean over 22-23 h and 0-4 h (Step-9 L347-348) |
| Day/night (new) | `agg_diurnal.csv` | WD mean over 08-17 h (08:00-18:00) / mean over the other 14 h |
| Presence peak hour | `agg_diurnal.csv` | same filter, `metric=="people"` |
| EUI (two bases) | `Step9_docs/outputs_step9_deliverable/step9_eui_by_channel.csv` | `eui_CFA_kWh_m2`, `eui_GFAshare_kWh_m2` |

## Comparison table (median across the 4 building-city cells; per-cell values in the CSVs)

| Channel | Metric | Code (Default_NECB) | Survey 2022 | Survey 2030 central |
|---|---|---|---|---|
| Office | WD energy peak hour, circular (argmax) | 12.02 (7.5) | 11.69 (7) | 11.90 (7) |
| Office | WD presence peak hour, circular (argmax) | 12.21 (9) | 11.25 (10) | 11.74 (13) |
| Office | Midday/night; day/night 08-18 | 7.21; 2.94 | 11.41; 2.91 | 11.77; 2.87 |
| Office | EUI CFA; GFA-share (kWh/m2/yr) | 85.36; 82.09 | 70.20; 69.64 | 68.53; 68.24 |
| Retail | WD energy peak hour (argmax) | 12.46 (11) | 13.09 (14) | 12.37 (11.5) |
| Retail | WD presence peak hour (argmax) | 13.73 (15) | 14.04 (14.5) | 12.79 (13) |
| Retail | Midday/night; day/night | 9.27; 3.20 | 47.06; 3.69 | 34.16; 3.58 |
| Retail | EUI CFA; GFA-share | 91.74; 86.56 | 79.19; 76.50 | 70.43; 69.70 |
| Hotel | WD energy peak hour (argmax) | 18.32 (18.5) | 18.90 (18) | 18.91 (18) |
| Hotel | WD presence peak hour (argmax) | 12.22 (15) | 23.22 (22) | 23.28 (22) |
| Hotel | Midday/night; day/night | 1.03; 0.85 | 0.78; 0.76 | 0.77; 0.76 |
| Hotel | EUI CFA; GFA-share | 260.23; 216.17 | 259.90; 215.52 | 260.79; 216.15 |
| Residential | WD energy peak hour (argmax) | 11.98 (7) | 12.03 (7) | 12.04 (7) |
| Residential | WD presence peak hour (argmax) | 12.21 (9) | 11.62 (0) - weak, R about 0.2 | 0.92 (4) - weak |
| Residential | Midday/night; day/night | 3.78; 1.83 | 3.89; 1.90 | 3.87; 1.90 |
| Residential | EUI CFA; GFA-share | 120.12; 108.32 | 118.68; 106.88 | 118.35; 106.56 |
| Building | Peak hour, published all-days circular | 14.62 | 14.85 | 14.95 |
| Building | WD circular (argmax) | 14.04 (7 or 17) | 14.25 (7 or 17) | 14.41 (7 or 17) |
| Building | Coincidence factor, 6 channels (published basis) | 0.930 | 0.940 | 0.941 |
| Building | Coincidence factor, 4 tenant channels | 0.963 | 0.969 | 0.965 |
| Building | Midday/night; day/night | 2.94; 1.65 | 2.68; 1.54 | 2.60; 1.52 |

Residential presence circular means are near-meaningless (resultant length R about 0.2, noted in the Step-9
script L224-236); use the argmax. SuperTall Montreal has a 4-tenant coincidence factor of exactly 1.000 in all
three scenarios: all four tenant channels peak in the same hour (the 07:00 January start-up).

Data files (all written by the P3 script):
- `writing/implementation/IMP/data/P3_comparison_long.csv` (per cell x channel, 60 rows),
  `P3_comparison_summary.csv` (median/min/max), `P3_delta_vs_code.csv` (per-cell differences),
  `P3_controls.json` (every control with got/want/tolerance/verdict), `writing/implementation/IMP/data_p3_run.log`.
- Figure data: `writing/figures/fig_codeschedule_vs_survey_profiles.csv`, `fig_codeschedule_vs_survey_metrics.csv`,
  `fig_presence_by_channel_data.csv` (people by hour, WD and WE, per channel, for Default_NECB, Y2005, Y2010,
  Y2015, Y2022, B_central, per cell, with `people_per_100m2` and `channel_injected`).

## Controls (run first; 39 of 45 PASS, every FAIL explained)

Script: `writing/implementation/IMP/scripts/p3_code_schedule_comparison.py`.

- Control 1: my reader vs Step-9's own `step9_loadshape_peaks.csv` `wd_peak_hour_circular`, all 224 channel-cell
  rows: max difference 0 (PASS).
- Control 2, published §5.3 values (2030 central, tolerance half the last printed digit): channel peak-hour
  medians 11.90 / 12.04 / 12.37 / 18.91 PASS; building 14.95 PASS; coincidence factor median 0.941 and low
  0.851 (Tall Calgary) PASS; all eight midday/night kW medians PASS except retail night (below).
  Table 5 CFA ranges and medians for all four channels (56 cells): 12/12 PASS.
- Control 3: hourly reconstruction from the cell files reproduces `agg_peak.csv` coincidence factor and building
  peak exactly in all 12 cells (difference 0) - this licenses the new 4-tenant coincidence factor.
- Control FAILs (manuscript number anomalies, for P9):
  1. §5.3 office range "11.82-11.93 h": the weekday minimum is 11.88; 11.82 is the ALL-DAYS column minimum
     (`agg_peak.csv` `peak_hour_circular`, 11.8195). Mixed columns in one range.
  2. §5.3 building range "14.11-15.70": true values 14.1049 / 15.6948 - double rounding (3 dp then 2 dp);
     correct 2-dp values are 14.10 / 15.69.
  3. §5.3 retail night "2.11 kW": true median 2.104997 (2.10). Rounding edge.
  4. §5.2/§6 "uninjected control scores 85.45": the frozen cells give 82.29 / 90.21 / 81.65 / 88.43, median
     85.36, mean 85.64. 85.45 is a constant hard-coded in the Step-9 band text (`3rdJ_09_...py:164`), not
     derived from this arm. Conclusion (fails the 100 floor) unchanged.
  5. Scope: 0.941 / 0.851 are the 2030-central 4-cell values. Over all 56 cells (the scope of gate `S9-COINC`)
     the median is 0.936 and the minimum 0.833, which is the CODE-schedule cell (Default_NECB Tall Calgary).
- Negative controls (must FAIL; 6 of 7 do): reading `metric=="people"` instead of `energy_W` (office 11.74 vs
  11.90) FAIL; 2022 rows read as 2030 (hotel 18.904 vs 18.91) FAIL, but only narrowly - timing barely differs
  between years; profile rotated +3 h FAIL; coincidence factor from the superseded `outputs_step8/agg/`
  (0.966) FAIL; cooling/heating allocation bases swapped (off by 0.034) FAIL; 4-tenant vs 6-channel
  coincidence factor FAIL. Not discriminating: retail peak hour from the superseded aggregate equals the
  frozen one (12.372 vs 12.374), so peak hours alone cannot tell the two arms apart; and the allocation
  fallback basis cannot move the coincidence factor (fallback hours carry no load).

## Figures (600 dpi PNG + PDF, from the frozen data above)

- `writing/figures/fig_codeschedule_vs_survey.{py,png,pdf}`: (a)-(e) weekday normalised energy profile per
  channel and whole building, code (dashed) vs 2022 vs 2030 central, circular-mean hour marker on top;
  (f) coincidence factor per cell. The curves overlap almost everywhere, which is the point.
- `writing/figures/fig_presence_by_channel.{py,png,pdf}`: weekday occupants per 100 m2 per channel, code
  schedule vs 2005 / 2010 / 2015 / 2022 / 2030 central (hotel: 2022 and 2030 only, since it is uninjected
  earlier). Shows the night-time presence of hotel guests and residents that code schedules lack, and the
  lower 2030 office presence (a P10-exposed value).

## Draft Results sentences (for §5.3; numbers are 2022 medians, 2030 in brackets pending P10)

1. Against the uninjected run of the same towers on code schedules, the survey-driven channels leave the timing
   of energy demand almost unchanged: the whole-building load centroid moves by 0.16 to 0.29 h across the four
   building-city cells, no channel's energy peak hour moves by more than 0.8 h, and the annual building
   maximum falls at 07:00 on a January morning in every cell under both schedule sets.
2. Diversity is not created by the survey model: the coincidence factor is 0.930 on code schedules and 0.940 on
   survey-driven channels (median of four cells), so the code schedules already stagger the four uses and the
   survey channels make the building slightly more coincident, by 0.005 to 0.020.
3. What the survey model changes is who is in the building and when: hotel guest presence peaks at 22 h instead
   of 15 h, and residents are present overnight rather than during the working day, a reversal the code
   schedules of the prototype cannot represent.
4. These presence changes reach energy through the channels whose lighting and equipment follow occupancy: the
   weekday midday-to-night energy ratio rises from 7.2 to 11.4 for office and from 9.3 to 47.1 for retail, the
   hotel ratio falls from 1.03 to 0.78, and office and retail intensities fall by 16 to 20 % and 12 to 15 %.
5. Residential energy is almost unaffected (intensity within 2 %, midday-to-night ratio 3.8 against 3.9),
   because in this model residential occupancy drives occupant heat gains only, while lighting and equipment
   remain on code schedules.

## What I did not verify

- Whether the code residential/hotel occupancy schedules are the PNNL prototype originals (read only through
  the simulated people counts, not the IDF schedule objects).
- The 2030 column's validity (P10).
- Run-to-run noise (V3a): differences of a few hundredths of an hour or 0.005 in coincidence factor may be
  within seed noise; the verdict does not depend on them.
