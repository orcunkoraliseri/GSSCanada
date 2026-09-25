# Supplementary material: additions and moves for the revised manuscript

This file holds the material moved out of the main text. It is merged with `writing/fullSet/readySubmission_SI.md` when the SI is rebuilt.

## Numbering of supplementary items

| New SI item | Content | Source |
|---|---|---|
| Table S1 | Checks and thresholds, with their provenance | old Table 4 (`writing/tables/Table_04_validation_gates.md`) |
| Table S2 | Limitations with a bounding measurement for each | old Table 7 (`writing/tables/Table_07_limitations.md`), with row L6's measured claim removed (see below) |
| Table S3 | Model card and per-cycle retail code mapping | old Tables A1 and A2 |
| Table S4 | Components carried over from the two-channel version | old Table 6, rewritten below |
| Figure S1 | Occupiable-area share per channel | old Figure S1 (was in main-text §4.1) |
| Figure S2 | One scenario lever per channel | old Figure S2 (was in main-text §4.3) |
| Figure S3 | Two-channel version of the framework | old Figure S3 |
| Figure S4 | Three-stage development of the model | old Figure 2 (`Figure_02_three_leg_roadmap.png`) |
| Figure S5 | Exclusivity step across the three decoder heads | old Figure 4 (`Figure_04_exclusivity_projection.png`) |
| Figure S6 | Diurnal load per channel, central 2030 scenario | old Figure 9 (`Figure_09_diurnal_4ch.png`) |
| Figure S7 | Channel and whole-building peak hours, central 2030 scenario | old Figure 10 (`Figure_10_peakhour_4ch.png`) |

## S.1 Checkpoint selection

The delivered occupancy model was selected by a composite validation score rather than by the rule specified before training. The specified rule was to discard every checkpoint that did not pass a hard check, then to take the highest retail F1 among the rest. The training code instead kept the checkpoint with the lowest composite of the mean Jensen-Shannon divergence and the mean gap in presence rate across the three heads:

$$S = \overline{\mathrm{JS}} + \tfrac{1}{2}\cdot\frac{g_{\mathrm{home}} + g_{\mathrm{work}} + g_{\mathrm{retail}}}{3}$$

The score contains neither the precision-recall area nor F1. The two rules pick different epochs in four of five seeds. The delivered seed ranks first of five on the composite and fourth of five on retail F1. It is 0.0218 retail F1 below the specified rule's choice, 5.6 % in relative terms and 0.16 standard deviations of the spread across seeds.

The model was not re-selected, for an evidential reason. Both rules rank epochs on teacher-forced validation columns. A separate person-level test showed that those columns cannot see person-level retail skill. The hard-check clause of the specified rule could also not be applied as written. Two of its five check families are pool-level quantities that exist only after inference and adjustment. On the observed range the clause would not have removed any epoch. The worst epoch reached a precision-recall area of 0.518 against a bar of 0.15, an F1 of 0.282 against 0.25, and a raw impossible-state rate of 0.014 % against 0.5 %.

## S.2 Injection checks

The field check on occupant objects has its origin in the two-channel version. There, a modulated occupancy schedule was attached to the wrong field of the occupant object. That field still existed and still held a valid schedule. Every input-side check then available passed, including schedule presence, syntax and non-empty fields. The error flattened the office channel's daily signal. It was found only when office output did not differ from an unmodulated run. The check now confirms the correct field on every modulated space.

An input-side check cannot show that outputs carry the scenario signal. Two output-side checks were therefore added. The first requires scenarios that should differ to give different outputs. The second re-runs a simulation whenever the injection code or the schedule files it reads have changed since that output was produced. The first version of this second check tracked only the injection code. It was extended to the schedule files, because their content also decides what is injected.

## S.3 Retail scoring rule

Retail was first scored by counting every simulation against the range. That count turned on a margin of 0.15 % of the floor. In an earlier improvement round, a shift of -0.05 % in the median changed one simulation's verdict. The rule was then changed to require the median of all simulations to lie within the range. The change was made after the numbers of an earlier run had been seen. The rule was then written down before the numbers of the reported runs were read. Retail does not meet its range under both rules.

## Table S4. Components carried over from the two-channel version

A "Yes" is entered only where the files themselves were compared by checksum. Where nothing was compared, the table says so.

| Component | Two-channel version | Four-channel change | Identical? | Basis |
|---|---|---|---|---|
| Data collection | Survey columns for residential and office | Monthly provincial hotel series added; retail needs no new survey variable | Not compared | No comparison was run |
| Harmonisation | Code mapping for residential and office | Hotel series preparation added, plus the retail rule (Eq. B.1) | Not compared | No comparison was run |
| Half-hour slot tables | Residential and office slot tables | One added retail entry, written to a separate file | Not compared | Design intent only; not tested against the output |
| Occupancy model | Two decoder heads | Third head for retail; shared encoder kept with targeted upgrades | No | The drift tolerance is 0.002 bits, a bounded change rather than identity; the measured drift is not reported |
| Linkage | Household and worker linkage | Retail as one population-level fraction; hotel by provincial multiplier | Not compared | Documented as unchanged; no comparison was run |
| 2030 scenarios and hotel model | Survey-cycle adjustment, demographic drift, office work-from-home bands | Adjustment reused; retail lever and hotel time-series model added | No | Not compared at the level of injected schedules |
| Building-model integration | Two-channel injection by space tag | Four-channel routing; a missing channel keeps the code schedule | Yes, base prototype geometry only | The four prototype files are byte-identical. The injection code exists in three non-matching copies, so the building is shared and the code writing into it is not |
| Building simulation | 72-run residential re-simulation plus the office runs | The 56-simulation campaign with all four channels | Not compared | Channel isolation was shown inside this campaign; the two versions' outputs were not compared |
| End-use loads | Two-channel checks against survey and prototype references | Four-channel checks, two reported outside their ranges (Table 4) | No | Different check sets and possibly a different basis; the two cannot be differenced |
