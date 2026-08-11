# Table 1 - Competitor Positioning Matrix

<!-- APPARATUS NOTE: differentiation targets named in this project's own positioning review, "Closest Prior Works and Differentiation": Doma & Ouf, Buttitta & Finn, Widen & Wackelgard. Both "this study" rows are listed separately so the increment from 2J to Leg-3 is visible. This records where the three competitor rows came from; it is not a statement to the reader, and it is stripped from the submission copy. -->



| Study | Time-series occupancy | Time-use-survey-driven | Multi-channel (>1 use) | Calibrated behavioural model | Forecast to a future year | Mixed-use single building | Activity/end-use resolved | Stock-scale |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Doma & Ouf (2023/2024) | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Buttitta & Finn (2020) | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| Widén and Wäckelgård (2010) | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| This study (four channels) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Authors' prior study (single channel) | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |

Two of the axes are read in more than one way in this literature, so both are defined here and every
cell in the column is scored against the definition given, this study's row included. A calibrated
behavioural model is one whose parameters are estimated from observed microdata on the population being
modelled, rather than assumed from a standard schedule or read off a sensor or positioning trace of one
particular building; the axis is about where the parameters come from, not about how accurately the
output reproduces a measured energy series, which is what the gates of Chapter 5 test and where three
failures are reported. Stock-scale means the result is intended to represent a building population
rather than a named set of buildings: a district of individually modelled buildings is not scored as
stock-scale, while a small set of archetypes weighted to stand for a national dwelling stock is.

Each of the three named competitors holds one axis this study combines. Doma and Ouf put multiple uses
in one modelling framework, but from mobile-positioning snapshots rather than a time-use survey, and at
district rather than single-building scale. Buttitta and Finn, and Widén and Wäckelgård, both drive
occupancy from a time-use survey but stay single-channel, residential only, single-wave and without a
forecast. The cell none of them occupies is a time-use-survey-driven, multi-channel,
forecast-to-a-future-year model inside a single mixed-use building. The authors' prior single-channel
row is carried alongside to show the increment: that study already cleared time-series, calibration,
forecast, activity resolution and stock scale on the residential-only problem, and the present study
trades stock-scale representativeness, two tower prototypes rather than a housing stock, for
multi-channel and mixed-use resolution the prior study did not attempt.

One independent reading of the same literature marks this study No on the calibration axis. It marks all
ten rows of its own matrix No on that axis, including the two it separately certifies as
time-use-survey-driven, and a column with no variation across ten studies separates nothing in either
direction. Under the definition given above the tick stands, for this study and for the competitors that
also estimate from survey microdata; under a stricter reading requiring agreement with a measured energy
series, no row in either matrix would be ticked, this study included. The axis is in any case not one of
the four the novelty claim rests on, which are time-use-survey-driven, multi-channel, forecast to a
future year, and mixed-use single building.

## Sources

- `deepResearch_Resources/RV09_disputed_dois_and_gap_matrix.md` Part B (10-row competitor matrix, all
  rows marked full text read) and Section B rows B5-B10, vetted in
  `deepResearch_Resources/VETTING_RV09_RV10_2026-08-08.md`:
  - the new `Time-use-survey-driven` column for all five rows;
  - the five previously unscored cells (Doma time-series 1 h / district 221 buildings; Buttitta
    presence-state count / four stock archetypes);
  - the two recorded disagreements (Telus vs the SafeGraph naming in `dr_L3-10`; UK TUS 2000 vs the
    Irish TUS named in §1.2) and the third on this study's own calibration row.
  - Not adopted from RV09: its `Calibrated behavioural model` column, which reads No on 10 of 10
    rows and so cannot discriminate; and its `Activity/end-use resolved` verdict for Doma & Ouf, which
    contradicts `dr_L3-10` on a cell `dr_L3-10` does state. The `dr_L3-10` verdict is kept.
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
