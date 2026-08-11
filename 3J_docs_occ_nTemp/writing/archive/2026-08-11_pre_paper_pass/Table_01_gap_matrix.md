# Table 1 - Competitor Positioning Matrix

<!-- APPARATUS NOTE: differentiation targets named in this project's own positioning review, "Closest Prior Works and Differentiation": Doma & Ouf, Buttitta & Finn, Widen & Wackelgard. Both "this study" rows are listed separately so the increment from 2J to Leg-3 is visible. This records where the three competitor rows came from; it is not a statement to the reader, and it is stripped from the submission copy. -->



| Study | Time-series occupancy | Time-use-survey-driven | Multi-channel (>1 use) | Calibrated behavioural model | Forecast to a future year | Mixed-use single building | Activity/end-use resolved | Stock-scale |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Doma & Ouf (2023/2024) | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ |
| Buttitta & Finn (2020) | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| Widén and Wäckelgård (2010) | ✓ | ✓ | ✗ | ✓ | ✗ | ✗ | ✓ | ✗ |
| This study (four channels) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| Authors' prior study (single channel) | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |

What the axes mean. Two of the seven are read in more than one way in this literature, so both are
defined here and every cell in the column is scored against the definition given, this study's row
included.

- *Calibrated behavioural model* - presence is produced by a behavioural model whose parameters are
  estimated from observed microdata on the population being modelled, rather than assumed from a
  standard schedule or read off a sensor or positioning trace of one particular building. The axis is
  about where the model's parameters come from, not about how accurately its output reproduces a
  measured energy series; the latter is what §5's energy-use-intensity gates test, and three of those
  gates are reported failing.
- *Stock-scale* - the study's result is intended to represent a building population rather than a
  named set of buildings. A district of individually modelled buildings is not scored as stock-scale;
  a small set of archetypes weighted to stand for a national dwelling stock is.

Reading of the matrix. The three named competitors each hold one axis this study combines: Doma & Ouf
put multiple uses (office, retail, residential) in one modelling framework but from mobile-positioning
snapshots, not a time-use survey, and at district scale, not inside one building. Buttitta & Finn and
Widén and Wäckelgård both drive occupancy from a time-use survey but stay single-channel, residential
only, single-wave, with no forecast. The cell none of the three occupies is a time-use-survey-driven,
multi-channel, forecast-to-a-future-year model inside a single mixed-use building - that is the
cell this study occupies, and the one this project's positioning review names as "genuinely unclaimed
in the literature." The authors' prior single-channel row is carried alongside it to show the increment
is additive: that study already cleared time-series, calibration, forecast, activity-resolution and
stock-scale on the residential-only, single-channel problem; the present study trades stock-scale
representativeness (2 tower prototypes, not a housing stock) for multi-channel and
mixed-use-single-building resolution, which the prior study did not attempt.

The five cells that this table previously left unscored. An earlier version of this matrix carried
five cells the primary positioning review does not state, marked as unscored rather than inferred. All
five have since been read out of the competitors' full texts, and each is recorded with the fact it
rests on: *Doma & Ouf* resolve occupancy at one hour (time-series ✓), read presence from a
mobile-positioning trace with no behavioural model estimated from it (calibrated ✗), and model a
district of 221 individually represented buildings, which under the definition above is not a stock
(stock-scale ✗); *Buttitta & Finn* estimate their presence model from a national time-use survey
(calibrated ✓), report presence-state counts rather than activity categories (activity/end-use
✗), and apply four archetypes standing for a dwelling stock (stock-scale ✓).

Two disagreements between sources, recorded rather than resolved, because neither changes a
verdict. The competitor axes were cross-checked against a second, independent reading of the same
nine studies, and it differs from the sources used here in two places. It gives Doma & Ouf's
positioning data as a different vendor than the one this table's primary source names, and it records
Buttitta & Finn's survey as a different country's than the one §1.2 names. Both are attribute
disagreements inside a cell whose verdict is the same under either reading (mobile positioning either
way; a national time-use survey either way), so both are noted here and neither has been adopted on a
single unverified report.

A third disagreement, on this study's own row, and why the tick stands. That same independent
reading marks *this study* No on *calibrated behavioural model*. It marks all ten rows of its own
matrix No on that axis, including the two rows it separately certifies as time-use-survey-driven, and
its parenthetical for this study is "gate-tested control" - a statement about validation, not a denial
that the model's parameters are estimated from microdata. A column with no variation across ten studies
separates nothing, in either direction. Under the definition given above the tick stands for this study
and for the three competitors that also estimate from survey microdata; under a stricter reading that
requires agreement with a measured energy series, no row in either matrix would be ticked, this study
included, and §5 reports three such gates failing rather than claiming otherwise. The axis is
therefore not one of the four this paper's novelty claim rests on, which are time-use-survey-driven,
multi-channel, forecast to a future year, and mixed-use single building.

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
