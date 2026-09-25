# Table 5 - Per-channel EUI vs plausibility bands

Every measured value below comes from the frozen deliverable of the campaign reported here. EUI is
reported on two bases and the two are never averaged: conditioned floor area of the zones assigned to
that use, the primary thermodynamic metric, and the whole-building gross floor area times the parsed
occupiable-area fraction for that channel, reported for stock comparability.

| Channel | As-modelled band, low/central/high (PASS criterion) | Empirical band, low/central/high (INFO criterion) | Measured range, CFA basis (median) | Measured range, GFA-share basis (median) | Cells passing (as-modelled) | Verdict |
|---|---|---|---|---|---|---|
| Office | 100 / 135 / 200 kWh/m2/yr | 170 / not reported / 360 kWh/m2/yr | 61.72-90.21 (median 71.02) | 63.27-85.51 (median 71.53) | 0/56 | FAIL, all 56 cells below the 100 floor |
| Retail | 80 / 110 / 155 kWh/m2/yr | 150 / 280 / 380 kWh/m2/yr | 63.63-96.84 (median 75.63) | 62.88-91.95 (median 73.27) | 12/56 in band; gate scored on the median | FAIL under the median-in-band rule; all-cells count 12 PASS / 44 FAIL |
| Hotel | 180 / 240 / 300 kWh/m2/yr | 220 / 350 / 480 kWh/m2/yr | 203.33-318.42 (median 260.54) | 171.07-261.18 (median 215.96) | 28/56 | FAIL, 28/56 above the 300 ceiling, all on Tall |
| Residential | none defined | 113.9 / not reported / 147.2 kWh/m2/yr (SHEU high-rise) | 111.57-128.77 (median 119.10) | 101.54-115.05 (median 107.24) | n/a, INFO only | INFO, 55/56 outside the empirical band |

The empirical band's central value is not reported for office or residential because the
deliverable carries no such column and a midpoint was not invented. No band value was moved
and no gate verdict was changed to produce this table.

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
