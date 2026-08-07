# Table 1 - Competitor Positioning Matrix

*Differentiation targets named in dr_L3-10 §2.4 "Closest Prior Works & Differentiation": Doma & Ouf,
Buttitta & Finn, Widen & Wackelgard. Both "this study" rows are listed separately so the increment
from 2J to Leg-3 is visible.*

| Study | Time-series occupancy | Multi-channel (>1 use) | Calibrated behavioural model | Forecast to a future year | Mixed-use single building | Activity/end-use resolved | Stock-scale |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Doma & Ouf (2023/2024) | ⚠ check source | ✓ | ⚠ check source | ✗ | ✗ | ✓ | ⚠ check source |
| Buttitta & Finn (2020) | ✓ | ✗ | ⚠ check source | ✗ | ✗ | ⚠ check source | ⚠ check source |
| Widen & Wackelgard (2010) | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| **This study (Leg-3)** | **✓** | **✓** | **✓** | **✓** | **✓** | **✓** | **✗** |
| **This study (2J)** | **✓** | **✗** | **✓** | **✓** | **✗** | **✓** | **✓** |

**Reading of the matrix.** The three named competitors each hold one axis Leg-3 combines: Doma & Ouf
put multiple uses (office, retail, residential) in one modelling framework but from mobile-positioning
snapshots, not a time-use survey, and at district scale, not inside one building. Buttitta & Finn and
Widen & Wackelgard both drive occupancy from a time-use survey but stay single-channel, residential
only, single-wave, with no forecast. **The cell none of the three occupies is a time-use-survey-driven,
multi-channel, forecast-to-a-future-year model inside a single mixed-use building** - that is the
Leg-3 cell dr_L3-10's positioning verdict names as "genuinely unclaimed in the literature." The 2J row
is carried alongside Leg-3 to show the increment is additive: 2J already cleared time-series,
calibration, forecast, activity-resolution and stock-scale on the residential-only, single-channel
problem; Leg-3 trades stock-scale representativeness (2 tower prototypes, not a housing stock) for
multi-channel and mixed-use-single-building resolution, which 2J did not attempt.

**Cells marked `⚠ check source`.** dr_L3-10's Novelty Matrix (Table 3) and Reporting Survey (Table 1)
do not use the same six axes as this table, so several cells are not directly stated in the two
permitted sources and are left as `⚠ check source` rather than inferred:
- Doma & Ouf - *Time-series occupancy*: dr_L3-10 states the occupancy source is "Mobile positioning
  data (SafeGraph snapshots)" and separately that the study is **not** longitudinal (2019-2021
  snapshot); neither statement confirms or denies within-day temporal resolution.
- Doma & Ouf - *Calibrated behavioural model*: not characterised as calibrated or uncalibrated in
  either source.
- Doma & Ouf - *Stock-scale*: dr_L3-10 Table 1 says occupancy is "modeled as separate buildings at a
  district scale"; district-scale is not the same claim as stock-scale and no building count is given.
- Buttitta & Finn - *Calibrated behavioural model*, *Activity/end-use resolved*, *Stock-scale*: dr_L3-10
  states only that the study is time-use-survey-driven (Irish TUS), residential-only, and uses MURB
  archetypes; it does not characterise calibration, activity/end-use resolution, or scale.

## Sources

- `Leg3_4-split/deepResearch/dr_L3-10_mixeduse_reporting_positioning_REPORT.md`:
  - Table 1 (Mixed-Use Tall-Building Energy Studies), lines 10-18 - Doma & Ouf occupancy source and
    per-use reporting basis.
  - Table 3 (Novelty Matrix), lines 32-41 - multi-channel, time-use-survey-driven, longitudinal,
    forecast horizon, mixed-use-single-building and Canadian axes for Doma & Ouf (2023/2024),
    Buttitta & Finn (2020), Widen & Wackelgard (2010) and "This Study (GSS-Canada Pipeline)".
  - §2.4 "Closest Prior Works & Differentiation", lines 84-88 - the three named differentiation targets.
  - §2.3 "Positioning Verdict", lines 75-82 - the unclaimed-cell statement.
- `../2J_docs_occ_nTemp/writing/tables/Table_01_gap_matrix.md`:
  - Row `Widen & Wackelgard (2010)`, line 8 - Time-series occupancy ✓, Calibrated behavioural model ✓,
    Forecast to future year ✗, Activity & end-use resolved ✓, Stock-scale ✗.
  - Row `This study`, line 17 - Time-series occupancy ✓, Calibrated behavioural model ✓, Forecast to
    future year ✓, Activity & end-use resolved ✓, Stock-scale ✓ (carried to the "This study (2J)" row
    here).
- `writing/implementation/3rd_Occ_Journal_BuildInstructions.md` §0, lines 20-64 - 2J scope
  (residential-only, single-channel AT_HOME, four residential archetypes, not mixed-use) and Leg-3
  scope (four channels, two tower prototypes, two cities), used to fill the two columns
  (Multi-channel, Mixed-use single building) that the 2J gap matrix does not itself carry, since these
  describe this project's own prior work rather than an external paper.
