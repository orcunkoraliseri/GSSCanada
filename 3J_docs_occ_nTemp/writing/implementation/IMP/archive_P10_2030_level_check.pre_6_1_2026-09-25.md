# P10 - 2030 level check (does 3J share 2J's raking defect?) - implementation state

Task doc: `writing/implementation/3J_IMP_execution_2026-09-22.md` §P10; plan §5 "P10"
Status: DONE (read-only; no simulation, no existing file edited)
Scripts + raw outputs: `writing/implementation/IMP/scripts/p10_0*.py` and `p10_0*.out` (each script
re-derives its numbers from the files; every number below names its script output).

---

## VERDICT: DEFECT

Same class as 2J, different mechanism, and larger. The 2022 level that the 2030 occupancy was
calibrated against is not the 2022 level that the Y2022 cells were built from, and the 2030
residential schedules are drawn from a different population than the one the 2022 schedules
describe. Three frame mismatches, all measured:

1. **The Y2022 schedules are not 2022.** They are built from the whole Step-5 stock file, which holds
   diaries from all four survey cycles: only 5,560 of 29,502 person-rows (18.8 %) are 2022 diaries,
   44.59 % are synthetic. The 2030 calibration anchor is 2022-only, real-only (3,087 rows). Proven
   by re-running `cmd_year_2022`'s own calls in memory: full file reproduces the injected Y2022
   residential and office files exactly (max diff 0.0000); the 2022-only rows do not (negative
   control, max diff 1.0 / 0.149) (`p10_08`).
2. **The 2030 residential schedules draw diaries at random from a whole-population pool onto a
   labour-force stock.** The stock is 94.27 % employed, no one outside the labour force (it inherits
   `Aligned_Census_2025.csv`: LFTAG 1 = 28,498, 2 = 1,765, 99 = 10); the 2030 pool is 49.87 %
   employed and 44.4 % not in the labour force (LFTAG 3), and much older. `assemble_2030()` draws
   within day-type only, with no demographic match.
3. **The Step-6 weekend and retail rakes use a labour-force target on a whole-population pool.**
   Stage B (weekday work) is conditioned on employed persons; Stages C0 (weekend work), C1 (weekend
   home) and RETAIL take one pooled target from the labour-force anchor and apply it to the whole
   2030 pool. The pooled numbers match to 0.1 pp; inside the employed group, 2030 weekend home sits
   9.0 pp below 2022 and weekend work 6.5 pp above (hybrid band).

Size, on the injected products (weekday, clock 09:00-17:00):

| | Shipped 2022 | 2022 on the anchor frame | Shipped 2030 central | 2030 central, same frame | Shipped step | Like-for-like step |
|---|---|---|---|---|---|---|
| Residential at-home | 0.3006 | 0.4180 | 0.5186 | 0.3402 | **+21.8 pp** | **-7.8 pp** |
| Office_Knowledge at-work | 0.5634 | 0.4749 | 0.4343 (injected) | 0.4695 | **-12.9 pp** | **-0.5 pp** |

2J's defect turned an intended +1.5 pp into +8.3 pp. Here the residential step moves from -7.8 pp
to +21.8 pp (the sign flips) and the office step from about -0.5 pp to -12.9 pp.

**What softens it.** Unlike 2J, the 3J manuscript never prints a 2022-to-2030 difference: Figure 7
and §5.1 stop at 2022, and §5.4 compares 2030 cells with 2030 central. Within-2030 lever
comparisons share the frame, so the level error cancels there (the office band spread survives:
12.0 pp injected vs 13.8 pp same-frame). What the defect reaches is (a) every "2022" number (the
Y2022 point is a 2005-2022 blend), (b) every "under the central 2030 scenario" level in §5.3, and
(c) Table 5/Figure 8 ranges and medians over the 40 affected cells. Office's FAIL verdict cannot
flip (highest cell 90.21 against a floor of 100).

**The "10.51 pp" is reproduced and is not this defect.** It is exact (-10.51 pp, d = -0.649), but it
measures (a) the old 2030 file (`_C`, 7c105ef3), not the `_C_v2` the frozen cells were built from
(-10.78 pp there), (b) the 2030 synthetic pool, not an injected product, and (c) a population mix:
a 50 %-employed pool against a 94 %-employed anchor. The like-for-like metric of record is -0.92 pp
outside business hours, and -4.05 pp inside them. Table 6's sentence "2030 work presence sits 10.51
percentage points below observed 2022, four to five times the signal" is wrong as written.

**Side finding (not P10's question, but it changes the re-run scope).** The frozen 2030-family
cells injected the office and retail 2030 products from **before** the 2026-08-02 FINDING-6/7 fixes:
office `1536c98c` (pool-direct), retail `cf8721c6`, not the current `575d17e5` / `11414644`. Shown
three ways: cell manifests, the injected IDF's office schedule values, and the cells' own
office-people ratio (below).

---

## 1. Reproduce the 10.51 first (`p10_03_reproduce_1051.out`)

Definition: mean of `wrk30_001..048` over all rows (all bands, day types and LFTAG) of the 2030
file, minus the same mean over OBS2022 = `3rdJ_25CEN_aug_Full_Aggregated_excl.csv` rows with
`CYCLE_YEAR==2022 & IS_SYNTHETIC==0` (n = 3,087). Cohen's d on per-person day-means, pooled SD.
Source of the claim: `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md:278-284`
("Defaut 4"); explanation at `Leg3_4-split/Step6_docs/3rdJ_06_longitudinalForecasting_4split.md:525-533`.

| Quantity | Recorded | Re-derived, old `_C` 7c105ef3 | Re-derived, `_C_v2` 5aa74f44 (injected) |
|---|---|---|---|
| Pooled 2030 vs OBS2022 | -10.51 pp, d -0.649 | **-10.51 pp, d -0.649** (0.0894 vs 0.1944) | -10.78 pp, d -0.685 |
| Per band cons / central / opt | -9.25 / -10.60 / -11.67 | -9.25 / -10.60 / -11.67 | -9.61 / -10.88 / -11.85 |
| vs observed 2005/10/15 | -15.32 | -15.32 | -15.59 |
| Pre-calibration SYN2022 vs OBS2022 | -5.82, d -0.324 | -5.82, d -0.324 | (n/a) |
| Metric of record: weekday, employed, 32 non-business slots | -1.91 / -0.92 | -1.91 | **-0.92** |
| Same, all 48 slots / 16 business slots | -2.62 / -1.96; -4.05 | -2.62; -4.05 | -1.96; -4.05 |
| Negative control: contaminated all-2022 anchor | must differ | -7.92 (differs) | -8.19 |

Composition behind the pooled number: weekday employed share 18,456/37,008 = 49.87 % in the 2030
pool against 19,801/21,005 = 94.27 % in the stock and 2,708/2,879 = 94.06 % in OBS2022. Within the
employed on weekdays, 2030 hybrid work is -2.36 pp (day-mean). Within LFTAG 3 it is 0.0128 against
0.2031 (`p10_07_rake_composition.out`). The pooled -10.5 pp is therefore mostly this population mix.

## 2. Q1 - which 2030 diary file did the frozen cells read? (`p10_01_manifests.out`)

- All nine 2030-family scenarios × 4 cells carry residential `BEM_Schedules_4split_2030_{cons,central,opt}.csv`
  md5 `df94ff6a` / `d36388c8` / `4462726d` in `manifest.json` → `INPUTS_HASH_DETAIL`. These are the
  current files in `Step7_docs/outputs_step7/`, written 2026-07-30 19:17-19:18 by the runs whose logs
  print `[H6 PASS] 2030 _C file MD5 verified: 5aa74f44...` (`Step7_docs/run_year2030_central_20260730.log:4`,
  `_cons_...:4`, `_opt_...:4`). The pre-v2 central product survives as `..._central_BAK_2026-07-30.csv`
  (`043e0727`) and was not injected. **Answer: post-fix `_C_v2` (5aa74f44).**
- Office, all 36 cells: `office_presence_multiplier_2030.csv` md5 `1536c98c`, which on disk is now
  `office_presence_multiplier_2030_BAK_2026-08-02.csv` (pool-direct, pre-FINDING-6; Office_Knowledge
  weekday n = 1,928). The IDF confirms it: `B_central__Tall__MTL/injected_resized.idf:12437-12487`
  weekday values 0.0161, 0.0158, 0.0140 ... 0.4523 equal that file's hybrid `AT_WORK_fraction` column,
  not the current `575d17e5` (0.0163, 0.0163, 0.0157 ... 0.4939).
- Retail, all 36 cells: `cf8721c6` (central) / `0e3b256e` / `f7152e5a`, which are the `_BAK_2026-08-02`
  files (pre-FINDING-7), not the current `11414644` / `82b425b5` / `700398d0`.
- `injected.idf.provenance.txt` is dated 2026-07-30 21:27. `INJ_HASH cf69d508` was "inherited"
  (`improvements/v2/V2-G1_FROZEN_DELIVERABLE.md:14`), so the 2026-08-02 product fixes never reached
  the frozen arm. `improvements/prompts/previous/3rdJ_L3_manager_prompt_2026-08-03_PRE-ARMH.md:148`
  records the staleness as an open user decision. I found no later record that closes it.

## 3. Q2 - which 2022 frame did each side use?

| Product | Frame actually used | Code |
|---|---|---|
| Y2022 residential, office, retail | full stock `3rdJ_25CEN_aug_Full_Aggregated_excl.csv`, **no CYCLE_YEAR / IS_SYNTHETIC filter**: 29,502 rows = 2005: 9,488, 2010: 7,040, 2015: 7,414, 2022: 5,560; 44.59 % synthetic (`p10_02_aug_profile.out`) | `3rdJ_07_aug_to_bem_4split.py:82-83, 1058, 1064-1073` |
| Y2005 / Y2010 / Y2015 | same stock, diaries replaced by that cycle's real rows, demographic match | `3rdJ_08A_gen_historical_products_4split.py:228` (pool = cycle & IS_SYNTHETIC==0) |
| 2030 calibration anchor (all stages) | stock rows `CYCLE_YEAR==2022 & IS_SYNTHETIC==0`, n = 3,087 (pure anchor ON by default) | `3rdJ_06_calibrate_C_4split.py:904, 939-942` |
| 2030 residential | stock households, diaries drawn at random from the band pool **within day type only** | `3rdJ_07_aug_to_bem_4split.py:393-412` (called at :1157) |
| 2030 office (injected) | band pool directly (pre-FINDING-6) | predecessor of `build_office_2030_product`, docstring `:557-567` |

Proof that the Y2022 files come from the full stock (`p10_08_y2022_frame_control.out`): with the
full stock, `convert(complete_day_types(stock))` joins 1,109,520/1,109,520 rows of the injected
`BEM_Schedules_4split_2022.csv` with max |diff| 0.0000. `build_office_multiplier(stock, "observed")`
matches `office_presence_multiplier_2022.csv` with max |diff| 0.0000. Negative control: the same
calls on 2022-only rows join 255,984 rows with max |diff| 1.0 (residential) and 0.149 (office).

The rake-target frame (`p10_07_rake_composition.out`, weekend, day-mean over 48 slots, hybrid band,
`_C_v2`):

| Weekend | OBS2022 (labour force only) | 2030 pooled | 2030 employed (LFTAG 1) | 2030 LFTAG 3 |
|---|---|---|---|---|
| Home | 0.7893 (employed 0.7863) | 0.7890 (-0.02 pp) | 0.6964 (**-8.99 pp** vs employed) | 0.8913 |
| Work | 0.0747 (employed 0.0731) | 0.0737 (-0.10 pp) | 0.1379 (**+6.48 pp**) | 0.0049 |

The stages hit their pooled targets. The employed, who are the only people the office product
reads and who make up 94 % of the stock, sit far from 2022. The old `_C` shows the same pattern
(employed weekend work +7.79 pp, `p10_07b_rake_composition_oldC.out`), so the Lot-A fix did not
cause it. One consequence: the FINDING-6 docstring's reading that "the ×2 weekend rise from 2022 is
REAL BEHAVIOUR in the 2030 diaries" (`3rdJ_07_aug_to_bem_4split.py:604-605`) is not established. A
pooled weekend-work target, diluted by 44 % non-workers, lets employed weekend work stay high.

## 4. Q3 - weekday shares by hour, 2022 vs 2030

Residential `Occupancy_Schedule` = HH-mean of members' `hom30`, clock hours (`convert()`
`3rdJ_07_aug_to_bem_4split.py:304-348`, roll +4 at :330); unweighted mean over SIM_HH_ID.
Counterfactuals are built in memory by the frozen functions themselves (`p10_05_counterfactual_frames.out`):
"anchor frame" = `08A.demo_assemble(stock, 2022 real rows)`, which is exactly how Y2005/10/15 are
built; "same frame 2030" = `demo_assemble_2030(stock, band pool)`, the matcher Step 7 already uses
for the post-FINDING-6 office. Control: re-running the shipped `assemble_2030("hybrid")` path in
memory reproduces the injected central file on 1,109,520/1,109,520 rows, max |diff| 0.0000.
Negative control against the Y2022 file gives mean |diff| 0.306.

Residential, weekday (clock h 0..23):

```
Shipped Y2022 (281d96c0)     0.956 0.965 0.970 0.972 0.951 0.915 0.812 0.606 0.405 0.330 0.299 0.285 0.283 0.266 0.267 0.297 0.379 0.539 0.657 0.696 0.765 0.842 0.903 0.936
Y2022 on anchor frame        0.965 0.973 0.977 0.976 0.952 0.924 0.851 0.708 0.545 0.474 0.432 0.405 0.393 0.380 0.387 0.404 0.470 0.598 0.711 0.758 0.826 0.888 0.932 0.955
Shipped 2030 central (d363)  0.949 0.956 0.962 0.963 0.995 0.995 0.987 0.902 0.742 0.623 0.562 0.483 0.504 0.474 0.472 0.476 0.555 0.686 0.768 0.809 0.841 0.885 0.925 0.936
2030 hybrid, same frame      0.942 0.951 0.963 0.966 0.997 0.997 0.983 0.840 0.596 0.467 0.430 0.277 0.294 0.270 0.281 0.280 0.422 0.594 0.674 0.764 0.813 0.866 0.909 0.929
```

| Residential | WD day-mean | WD 09-17 h | WE day-mean |
|---|---|---|---|
| Shipped Y2022 | 0.6373 | 0.3006 | 0.7292 |
| Y2022 on anchor frame | 0.7035 | 0.4180 | 0.7823 |
| Shipped 2030 cons / central / opt | 0.7520 / 0.7688 / 0.7792 | 0.4773 / 0.5186 / 0.5454 | 0.7650 / 0.7882 / 0.8063 |
| Same-frame 2030 cons / hybrid / fully | 0.6510 / 0.6876 / 0.7076 | 0.2516 / 0.3402 / 0.3944 | 0.6588 / 0.7006 / 0.7279 |

Decomposition of the shipped weekday 09-17 h step (+21.8 pp): Y2022 frame +11.7, 2030 random-draw
composition +17.8, like-for-like -7.8. Day-mean: shipped +13.2 = frame +6.6 + composition +8.1,
like-for-like -1.6. The shipped band spread (cons to opt, 09-17 h) is 6.8 pp. On one frame it is
14.3 pp, because 44 % of the drawn diaries come from non-workers, who carry no band signal.

Survey frames behind them (person-level `hom30`, weekday 09-17 h, `p10_04_levels.out`): all-cycle
stock 0.3001; 2022 real 0.4135; 2005 / 2010 / 2015 real 0.2742 / 0.2913 / 0.2772; 2030 hybrid pool
0.5196 overall, 0.3392 employed, 0.7338 LFTAG 3.

Office_Knowledge `AT_WORK_fraction` (the archetype every cell injects), weekday:

| Office | WD day-mean | WD 09-17 h | WE day-mean | Source |
|---|---|---|---|---|
| Shipped Y2022 | 0.2530 | 0.5634 | 0.0651 | `office_presence_multiplier_2022.csv` (ff0fc987), n = 3,383 |
| 2022 on anchor frame | 0.2100 | 0.4749 | 0.0961 | `p10_05` (person-level check: 0.2089 / 0.4700, n = 488) |
| Injected 2030 cons / hybrid / fully | 0.2070 / 0.1872 / 0.1680 | 0.4947 / 0.4343 / 0.3750 | 0.1622 / 0.1353 / 0.1126 | `..._2030_BAK_2026-08-02.csv` (1536c98c), n = 1,928 |
| Current, not injected | 0.2198 / 0.2025 / 0.1759 | 0.5283 / 0.4695 / 0.3902 | 0.1694 / 0.1378 / 0.1044 | `office_presence_multiplier_2030.csv` (575d17e5), n = 3,383 |

Office step, weekday 09-17 h: shipped -12.9 pp = Y2022 frame -8.9 + stale pool-direct product -3.5
+ like-for-like -0.5. The office Y2022 overstates 2022 because pre-2022 cycles carry more on-site
work (pre-2022 real 0.5743).

**Cross-check from the frozen cells' `channel_hourly.csv`** (`p10_06_cells_crosscheck.out`/`.csv`;
row = hour of 2006, RunPeriod starts Sunday per `injected_resized.idf:119-132`; weekday 09-17 h;
the IDF applies DST, so this is a cross-check, not a re-derivation):
- The 27 residential households are the same in all seven compared scenarios in all four cells.
- `office_people` B_central / Y2022 = **0.780** in all four cells (cons 0.883, opt 0.676). The
  injected-product ratio is 0.771 (0.878 / 0.666). The current file would give 0.833. The cells ran
  the stale office product.
- `residential_people` B_central / Y2022 = 1.328 (Tall) / 1.408 (SuperTall). The product ratio for the
  same 27 households, HHSIZE-weighted, is 1.620 / 1.483. The direction and size agree; the cells
  scale by the space's own people count, not HHSIZE, so the ratios are not identical.

## 5. Q4 - intended scenario change or artefact?

What Step 6 intended (from the code): weekday employed work outside business hours = 2022
(Stage B, :455-462, skips business slots :399-400); business hours = decoder, with the WFH band;
weekend work and home = 2022 (C0/C1); retail = 2022 × lever. So the intended 2022-to-2030 change
is the WFH band effect in weekday business hours for workers, with everything else near 2022.

What the injected products carry: residential weekday daytime at-home +21.8 pp and office -12.9 pp
(09-17 h). About +29.6 pp and -12.4 pp of those are frame artefacts: the Y2022 blend, the unmatched
2030 residential draw, and the stale pool-direct office. **Artefact, not scenario.**

What remains on one frame is not the "intended" change either, and the manager should see it
before approving a re-run. Same-frame 2030 residential daytime at-home falls below 2022 in all three
bands (-16.6 / -7.8 / -2.4 pp, 09-17 h). The 2030 employed diaries carry less work and less home
(more "away, not at work") than real 2022 ones: weekday employed home -1.36 pp and work -2.36 pp in
day-mean (hybrid). This is the decoder residual already documented as the -4.05 pp business-hours
gap (§B.2.1), not a frame effect. A reviewer who sees a work-from-home scenario lower daytime home
occupancy will ask about it.

## 6. Paper numbers affected (`writing/fullSet/readySubmission.md`)

**Directly wrong as written**
- Table 6 row "Step 6" (`readySubmission.md:469`; `writing/tables/Table_06_leg2_leg3_delta.md:16, :75`):
  "2030 work presence sits 10.51 percentage points below observed 2022, four to five times the
  signal". The number is for the superseded `_C` file and a population mix; the injected file gives
  -10.78, and the like-for-like gap is -0.92 / -4.05 pp. Rewrite even if nothing is re-run.

**Exposed through the Y2022 frame (the "2022" point is a 2005-2022 blend, 81 % pre-2022 diaries)**
- §5.1 (`:600-617`): office 2022 70.20 kWh/m2/yr (-0.67 %), retail 2022 79.19 (+2.36 %, range
  +0.13 to +4.69 %), residential 2022 118.68 (-0.07 %), hotel 2022 +0.09 %. Figure 7 (2022 point).
  The claim that retail "jumps past its own 2005 baseline by 2022" rests on a blended retail product
  (not sized here).
- §5.1 energy/area shares aggregated over the four cycles (`:622-626`: 44.47 / 20.25, 21.42 / 35.14,
  18.27 / 17.73, 2.56 / 3.92 %): these include the Y2022 cells.
- P3's recommendation to report the code-vs-survey comparison "on 2022" (`IMP/P3_code_schedule_comparison.md:47-55`):
  still valid as a survey-vs-code contrast, but the column must not be called "2022".

**Exposed through the 2030 central level (§5.3 is all "under the central 2030 scenario")**
- Abstract (`:5`) and Highlights 1-2 (`:13-14`): peak hours 18.91 h and "near 12 h", coincidence
  factor median 0.941.
- §5.3 (`:685-711`): office 11.90 h, residential 12.04 h, retail 12.37 h, hotel 18.91 h (ranges),
  whole-building 14.95 h (14.11-15.70); midday/night kW 72.03/2.11, 569.33/48.10, 347.82/89.53,
  434.47/335.93; coincidence factor 0.941, low 0.851. Figures 9 and 10. Residential daytime occupancy
  in these cells is inflated by about 18 pp by composition. Office carries the stale product. Expected
  movement: small for timing (P3 found energy timing is locked by plant and lighting schedules; the
  residential channel drives People only, `step9_gates.json` D-20), but the kW levels will move.
  Not measurable without a re-run.
- §6 Discussion (`:775-780`) and §7 Conclusion (`:832`) repeat the same numbers.

**Exposed through the 40 affected cells in whole-campaign statistics**
- §5.2 and Table 5 (`:644-669, :762-767`): office median 71.02, range 61.72-90.21 (FAIL cannot flip:
  it would need +11 %); retail median 75.63, 12/56 in band, 44/56 below the floor (retail also used
  stale 2030 products; direction unknown); hotel 203.33-318.42, 28/56 (hotel products are unaffected,
  whole-building coupling only); residential 111.57-128.77, median 119.10, 55/56 INFO. Figure 8.

**Within-2030 comparisons (mostly safe, because the frame is shared)**
- §5.4 (`:728-746`): office +1.67 to +2.45 % / -2.19 to -1.46 % (stale product, but band spread similar:
  12.0 vs 13.8 pp); retail (stale product); hotel (unaffected product); **residential +0.06 to +0.29 %
  is understated.** Its band spread is 6.8 pp shipped vs 14.3 pp on one frame. Bundles -2.05 to
  +2.20 etc. Figure 11.

**Not affected**: NECB control 85.45 (Default_NECB cells inject nothing); Y2005/10/15 products (real,
cycle-pure, same stock); hotel 2030 products (`4b3d3a46`, `d6e834ba`, `e0ab6c86`).

## 7. Re-rake and re-run design (for the manager; nothing done)

**Option R - fix and re-run (removes the defect).**
1. *Re-rake, Step 6* (`Leg3_4-split/Step6_docs/3rdJ_06_calibrate_C_4split.py`): make Stages C0 (:532-535),
   C1 (:644-647) and RETAIL (:732-737) take LFTAG-stratified targets, as Stage B already does (:455).
   Each 2022 real LFTAG 1 and 2 target is applied to the same LFTAG in 2030. LFTAG 3 and NaN have no
   anchor (the census frame has no one outside the labour force), so leave them uncalibrated; the
   matched assembly below almost never draws them. Write `..._C_v3.csv` (new md5; `_C` and `_C_v2`
   stay). Run locally, a few minutes (docstring :84-85). Re-run the Step-6 validator. Author decision
   inside this step: whether to add a weekday HOME target (2J-style) or accept the decoder residual
   (§5 above).
2. *Re-assemble, Step 7* (`Leg3_4-split/Step7_docs/3rdJ_07_aug_to_bem_4split.py`):
   - Y2022: `demo_assemble(stock, stock[CYCLE_YEAR==2022 & IS_SYNTHETIC==0])` (the 08A function), then
     the same residential, office and retail builders, into new files beside the old ones. Hotel 2022
     is unchanged. Real-only matches both the Step-6 anchor and the Y2005/10/15 convention (reuse is
     about 9.6× per diary: 29,502 / 3,087).
   - 2030 residential × 3: `demo_assemble_2030` instead of `assemble_2030` at :1157.
   - 2030 office: `build_office_2030_product` from `_C_v3` (already stock-matched).
   - 2030 retail × 3: `build_retail_product_2030` from `_C_v3` (current FINDING-7 path).
   - Re-run the Step-7 validator.
3. *Cells*: Y2022 × 4 + all nine 2030-family scenarios (B_cons/central/opt, sens_office/retail/hotel ×
   cons/opt) × 4 = **40 of 56 cells**. Y2005/10/15 (12) and Default_NECB (4) are unchanged and are
   carried over by copy.
4. *Cost*: measured locally at 6.6 min per cell alone and 12-18 min per cell at 6 workers; planning
   figure 15.9 min per run (`Step8_docs/3rdJ_08_simulation_4split.md:1745-1756, 2146, 2222`). 40 runs ×
   0.27 h = **about 11 CPU-hours**, or about 21 if the per-object DHW resize (Step-9H) needs its own
   sizing run per cell (not verified; V3 is measuring Speed run times). On Speed with ≤ 32 CPUs this
   is one wave, about 0.5-1 h wall-clock. Locally at 6 workers it is about 2-2.5 h (double with a
   resize run). Then Step-8E aggregate (pass the new aggregate explicitly; never `DEFAULT_AGG`), the
   Step-9 scorer and the figures, as a new sibling arm. The frozen arm stays.
5. *Gates, written before the run, each seen failing first*:
   (a) the new Y2022 weekday 09-17 h residential mean must equal 0.4180 ± 0.005 (this doc), and
   the old file must fail it (0.3006);
   (b) per-LFTAG weekend home and work gaps against OBS2022 after the re-rake must satisfy |Δ| ≤ 1.4 pp
   (the pooled weekend SEs: home 1.37 pp at `3rdJ_06_longitudinalForecasting_4split.md:762`, work
   1.05 pp at `:689`; the employed-only n = 191 makes the SE slightly larger, so recompute it and
   state it before the run), and `_C_v2` must fail (-8.99 / +6.48);
   (c) mutex 0 at every stage (existing H8);
   (d) each cell manifest's `INPUTS_HASH_DETAIL` must name the new product md5s. This is the check that
   would have caught the stale office and retail.

**Option L - no re-run (cheaper, weaker).** Keep the frozen arm. Relabel the Y2022 cells as the "pooled
2005-2022 survey" product. Move §5.3 to the Y2022 cells (they carry no 2030 artefact; P3 already
has that column) or state the residential-composition and stale-office limitation next to every 2030
central number. Rewrite the Table 6 sentence. Add a limitation that the 2022 point in Figure 7 is a
blend. Any 2022-to-2030 comparison stays out of the paper.

Either option needs the Table 6 rewrite. Only Option R lets the paper say anything about 2030
levels.

## WHAT I DID NOT VERIFY
- Energy consequences: no simulation was run, so the movement of any EUI, peak hour or coincidence
  factor after a fix is not measured, only argued.
- The retail channel's own frame effect (Y2022 retail blend; stale 2030 retail) was not sized.
- Whether the Step-9H resize requires a second EnergyPlus run per cell (it affects the CPU-hours
  estimate ×2).
- Why the census frame holds only labour-force persons (it is inherited from
  `0_Occupancy/Outputs_Aligned/Aligned_Census_2025.csv`; I did not trace its construction).
- Whether a record after 2026-08-03 explicitly accepted the stale office and retail products for the
  deliverable arm. I searched `improvements/v2/` and found none.
