# Table 5 - Per-channel EUI vs plausibility bands

Source for all measured values: `Leg3_4-split/Step9_docs/outputs_step9_deliverable/` (frozen
2026-08-06 00:05, canonical arm; registered `improvements/v2/V2-G1_FROZEN_DELIVERABLE.md`). The
sibling `outputs_step9/` (2026-07-31, superseded) is NOT used anywhere in this table; it inverts the
hotel result.

Dual-basis EUI reporting per dr_L3-10: **CFA** (Conditioned Floor Area of the zones assigned to that
use) is the primary thermodynamic metric; **GFA-share** (whole-building Gross Floor Area times the
parsed occupiable-area fraction for that channel) is reported for stock/SCIEU comparability. The two
bases are never averaged.

| Channel | As-modelled band, low/central/high (PASS criterion) | Empirical band, low/central/high (INFO criterion) | Measured range, CFA basis (median) | Measured range, GFA-share basis (median) | Cells passing (as-modelled) | Verdict |
|---|---|---|---|---|---|---|
| Office | 100 / 135 / 200 kWh/m2/yr | 170 / ⚠ check source (central not reported) / 360 kWh/m2/yr | 61.72-90.21 (median 71.02) | 63.27-85.51 (median 71.53) | 0/56 | **FAIL, all 56 cells below the 100 floor** |
| Retail | 80 / 110 / 155 kWh/m2/yr | 150 / 280 / 380 kWh/m2/yr | 63.63-96.84 (median 75.63) | 62.88-91.95 (median 73.27) | 12/56 individually in-band; gate scored on the **median** (75.63, below the 80 floor) | **FAIL under the median-in-band rule in force** (all-cells count: 12 PASS / 44 FAIL) |
| Hotel | 180 / 240 / 300 kWh/m2/yr | 220 / 350 / 480 kWh/m2/yr | 203.33-318.42 (median 260.54) | 171.07-261.18 (median 215.96) | 28/56 | **FAIL, 28/56 above the 300 ceiling, 0/56 below the 180 floor, all failures on `Tall`** |
| Residential | no as-modelled band defined | 113.9 / ⚠ check source (central not reported) / 147.2 kWh/m2/yr (SHEU HighRise context) | 111.57-128.77 (median 119.10) | 101.54-115.05 (median 107.24) | n/a (INFO only) | INFO, 55/56 outside the empirical band (1/56 IN) |

## The three failing gates, at full strength

- **Office.** The as-modelled band floor is 100 kWh/m2/yr. All 56 injected campaign cells fail it
  (median 71.02, range 61.72-90.21 on the CFA basis). Separately, and more importantly for the
  band-applicability argument: the **uninjected `Default_NECB` control** (the code's own reference
  implementation, no occupancy signal applied at all) scores **85.45 kWh/m2/yr against the same 100
  floor** -- it fails the band by 15 % before this work touches it. A gate that no untreated control
  can pass is measuring the band, not the model. Two candidate mechanisms were tested to explain the
  gap and **both were refuted in 56/56 cells**: modelled heating share is 17 % against the band's
  35-45 %, and rebasing on service/MEP area moves all 56 cells further down, not up. The band's own
  source document additionally gives three different floors for itself (Table 7.1 = 100.0; line 21 =
  80-140; Table 2.1 = 85.0-115.0), so the floor is recorded as contested and unsourced.
- **Hotel.** `S9-EUI-hotel` FAILs **28 of 56 cells**, measured range **203.33-318.42 kWh/m2/yr**,
  median 260.54. Every failure is **above the 300 kWh/m2/yr ceiling** (0 cells below the 180 floor),
  and every failure is on the **`Tall`** prototype (`SuperTall` clears the ceiling in 28/28 of its
  cells). This is the count and direction read directly from `step9_gates.json` (`S9-EUI-hotel` detail
  string) and `step9_eui_by_channel.csv`, both in the frozen deliverable. The band ceiling itself
  rests on the first-party DOE/PNNL Large Hotel, ASHRAE 90.1-2019 prototype value (284.44 kWh/m2/yr,
  CZ 6A Rochester; 299.28, CZ 7 International Falls), which is 1.0 % from the ceiling's original
  90.1-2004-lineage anchor of 302.21, so the vintage-mismatch objection does not hold; the remaining
  limitation is that the reference archetype (90.1-2019 Rochester/International Falls) and city set do
  not match this study's NECB-2017 Montreal/Calgary tower.
- **Retail.** The gate rule in force is **median-in-band**, not all-cells (decided at V2-B3, in
  advance of the numbers). The retail band spans 80-155 kWh/m2/yr; the measured median is **75.63,
  which is 5.47 % below the 80 floor** (re-derived from the 56 CFA values in the deliverable CSV).
  Under the median rule the gate is FAIL. Under an all-cells count, 12/56 cells sit inside the band and
  44/56 sit below the floor (0 above the ceiling); this per-cell tally is reported for transparency but
  is not the rule that scores the gate.
  The rule change itself was justified by a *different* quantity, and the two must not be conflated:
  V2-B3 records that the all-cells gate **was turning on 0.15 % of its floor**, meaning the per-cell
  verdict count was decided by a margin that narrow, so that a **-0.05 %** median shift in the V2-E3
  arm flipped one cell (55/56 to 54/56). That 0.15 % is the decision margin of the retired all-cells
  rule; it is **not** the distance between the median and the floor, which is 5.47 %.

## What was confirmed against the source files, and what was not

**Confirmed directly against `step9_eui_by_channel.csv` (56 rows per channel, 224 rows total) and
cross-checked against `step9_gates.json`'s `S9-EUI-*` gate `detail` strings:**
- Office: CFA range 61.72-90.21, median 71.02; GFA-share range 63.27-85.51, median 71.53; band
  100/135/200; empirical/INFO band 170/⚠ check source/360 (`info_central` is not a column in the CSV;
  only `info_lo`/`info_hi` are present); 0/56 PASS; all FAIL.
- Retail: CFA range 63.63-96.84, median 75.63; GFA-share range 62.88-91.95, median 73.27; band
  80/110/155; empirical/INFO band 150/380 (both `info_verdict` = OUT, 56/56); per-cell tally
  12 PASS / 44 FAIL; gate-level verdict FAIL under the median rule.
- Hotel: CFA range 203.33-318.42, median 260.54; GFA-share range 171.07-261.18, median 215.96; band
  180/240/300; empirical/INFO band 220/480 (`info_verdict` 28 IN / 28 OUT); 28/56 PASS, 28/56 FAIL, all
  failures above the ceiling, all on `Tall` (`verdict_asmodelled` cross-tabulated by `building` column
  in the CSV).
- Residential: CFA range 111.57-128.77, median 119.10; GFA-share range 101.54-115.05, median 107.24; no
  as-modelled band (`band_lo/central/hi` empty, gate is INFO-only); empirical/INFO band
  113.9/⚠ check source/147.2, 55/56 `info_verdict` = OUT, 1/56 IN.

**Confirmed against `_PROVENANCE.md` in the deliverable directory (not the CSV/JSON):** the hotel
median 260.5411 kWh/m2/yr and the "28 above the 300 ceiling, 0 below the 180 floor" summary, matching
the CSV/JSON independently.

**Taken from the brief and the pipeline docs, not independently re-derived from a per-cell CSV row
(no such standalone row exists in the deliverable's tabular outputs):**
- The uninjected `Default_NECB` control value of **85.45 kWh/m2/yr**. This number does not appear as a
  row in `step9_eui_by_channel.csv` (that file's 56 office rows are all *injected* cells). It does
  appear verbatim inside `step9_gates.json`'s `S9-EUI-office` gate `detail` string and inside
  `step9_report.html`, both in the frozen deliverable, so it is deliverable-sourced, just not
  CSV-tabulated. Its underlying simulation artefact (the `finding9_verify/` uninjected-control IDF) is
  held in the sibling `outputs_step9/` directory, which `_PROVENANCE.md` states is retained
  specifically because it is not reproducible elsewhere.
- The as-modelled band values themselves (retail 80/110/155; hotel 180/240/300; office 100/135/200)
  and the empirical/INFO bounds are sourced to `dr_L3-02_retail_eui_bands_REPORT.md` and
  `dr_L3-03_hotel_eui_bands_REPORT.md` (Table 5 in each report) and, for office, to the Leg-2-inherited
  `Office Reference EUI ... As-Modelled Bands.md` Table 7.1, cited via the `band_src` field in the CSV
  itself (also deliverable-sourced, confirmed).

No band value was moved and no gate verdict was changed to produce this table.

---

## Sources

- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_eui_by_channel.csv` - 224 rows (56 cells x
  4 channels), columns `channel`, `eui_CFA_kWh_m2`, `eui_GFAshare_kWh_m2`, `band_lo`, `band_central`,
  `band_hi`, `verdict_asmodelled`, `info_lo`, `info_hi`, `info_verdict`, `band_src`.
- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_gates.json` - gates `S9-EUI-office`,
  `S9-EUI-retail`, `S9-EUI-hotel`, `S9-EUI-residential` (30 gates total in file; scorecard
  `{'PASS': 17, 'INFO': 10, 'FAIL': 3}`).
- `Leg3_4-split/Step9_docs/outputs_step9_deliverable/_PROVENANCE.md` - identity block confirming the
  hotel median (260.5411), range (203.3295-318.4200), and the "28 above ceiling, 0 below floor" tally
  independently of the CSV/JSON.
- `Leg3_4-split/deepResearch/dr_L3-02_retail_eui_bands_REPORT.md`, Table 5 (as-modelled 80/110/155,
  empirical 150/280/380).
- `Leg3_4-split/deepResearch/dr_L3-03_hotel_eui_bands_REPORT.md`, Table 5 (as-modelled 180/240/300,
  empirical 220/350/480) and the ASHRAE 90.1-2019 Large Hotel first-party retrieval (284.44 / 299.28).
- `Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md`, Part C §1 (dual-basis
  EUI reporting specification: CFA primary, occupiable GFA-share for stock comparison).
- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline.md`, section `LIMITATIONS - CONSOLIDATED`, items L4
  (office, lines ~651-659) and L5 (hotel, lines ~661-674), for the refuted-mechanisms and
  archetype-mismatch language quoted above.

No em dashes or en dashes.
