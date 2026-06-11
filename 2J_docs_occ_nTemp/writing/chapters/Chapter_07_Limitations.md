# 7 Limitations

Seven limitations bound the interpretation of the results. Each is stated together with its disposition — the design choice, mitigation, or sensitivity analysis that contains it — so that the boundary of the claim is explicit rather than implied. They are ordered from the most consequential correctness issue (now resolved) to the scope choices that frame the forecast.

---

### 7.1 The Schedule-Injection Phase Error and Its Remediation

The single most consequential correctness issue in the campaign was the four-hour schedule-injection phase error described in §4.2 and §6.5: the 04:00-origin GSS diary slots were initially written into the EnergyPlus hour field without the circular rotation onto the 00:00 simulation clock, displacing all four schedule channels four hours early. The disposition is complete. The error was diagnosed on 2026-06-08, the rotation was restored, and both the Step-8 occupancy campaign (6,000 runs) and the Step-9 end-use campaign (4,800 paired runs) were fully re-simulated and re-verified on 2026-06-10. Because annual energy is phase-invariant, the magnitude and SHEU-calibration results were never affected (maximum archetype EUI change +2.85 %, all cells remaining within plausibility bands); only the intraday timing required re-evaluation, and the corrected timing — a stationary ~17:30 peak and a 0 ± 1 h activity-arm null shift — is what the results report. The pre-fix "~4 h earlier" peak reading is superseded and is not cited as a finding.

---

### 7.2 The Un-Calibrated Metabolic Channel

The metabolic (internal-heat-gain) channel rides the raw J3 activity mix and is not independently calibrated against a survey benchmark, unlike the equipment and lighting channels, which are SHEU-anchored. The disposition rests on three points. First, occupancy — the dominant internal-gain driver in residential thermal balance — *is* calibrated, so the principal heat-gain pathway is anchored. Second, the activity-to-watts mapping is grounded in recognised standards (the 2024 Adult Compendium of Physical Activities for MET values, referenced to ASHRAE 55 / ISO 7730), and is applied conservatively (70 W/MET against an ~60 kg reference adult, below the ~105 W/MET comfort-standard default), so the channel is bounded rather than free. Third, an activity-side raking facility exists and could anchor the metabolic mix in future work should a suitable benchmark become available. The metabolic channel therefore introduces a bounded, standards-grounded uncertainty in absolute internal-gain magnitude, not an open degree of freedom.

---

### 7.3 Weekend Pooling and Hourly Reporting Resolution

Two resolution choices simplify the temporal representation. Saturday and Sunday are pooled into a single "Weekend" day-type, and the EnergyPlus reporting interval at the IDF interface is hourly (24 values per day-type). The disposition is that both are deliberate compromises rather than data losses. The 48×30-min diary is the documented optimal accuracy-versus-cost resolution (§3.1), and the finer 30-min structure is preserved upstream through harmonization, augmentation, and calibration; the hourly down-sampling occurs only at the simulation interface, where it materially reduces run cost without altering the diurnal features the analysis examines. The Saturday/Sunday split, and a sub-hourly reporting interval, are both available extensions identified in §8 as natural refinements; neither is expected to alter the peak-stability finding, which is an evening-weekday phenomenon.

---

### 7.4 Single-Envelope Generalization Across Climates and a Frozen Stock

The simulation holds a single Montréal Zone-6 envelope fixed across all six climate cities, freezes the dwelling stock at the 2022 analytical frame, and uses Typical Meteorological Year weather rather than future climate files; Atlantic-province households are mapped onto the Montréal EPW. These are isolation choices, and the disposition follows from the paired design itself: because each household is differenced against itself across cycle-years (§4.3), the within-household Δ cancels the envelope, the climate file, and the frozen stock exactly, so these constants cannot bias the behavioural signal that the paper reports. They do bound the *absolute* EUI levels and limit cross-climate generalization of the magnitude figures, and a Zone-7A cold-zone EUI sensitivity is the natural check. Future weather files and stock turnover are flagged in §8 as the appropriate vehicle for projecting absolute future demand, which is outside the present attribution scope.

---

### 7.5 Conditional-Independence Risk in Statistical Matching

The Census–GSS linkage (§3.3) is a statistical match, and like all such matches it rests on a conditional-independence assumption: that, conditional on the seven demographic match keys and the day-type stratum, the carried diary behaviour is independent of the dwelling variables drawn from the Census record. The disposition is mitigation by design. The match vector is parsimonious and predictive (age group, sex, marital status, household size, labour-force status, province, and census metropolitan area), the assignment is probabilistic rather than deterministic, and the realized match-tier distribution is reported transparently (Tier-1 Perfect 44.94 %, Tier-2 Core 21.39 %, Tier-3 Constraints 33.67 %, Tier-4 FailSafe 0.00 %), so the reader can see that the FailSafe tier is never invoked and that two-thirds of agents match on the full or core key set. The conditional-independence risk is acknowledged as intrinsic to statistical matching and contained, not eliminated.

---

### 7.6 The Survey-Mode Transition

The four GSS cycles span a collection-mode transition from computer-assisted telephone interviewing to an electronic-questionnaire instrument, which could in principle confound a cross-cycle behavioural comparison. The disposition is that the effect is absorbed at three levels: ex-post output harmonization reconciles the cross-cycle schemas, per-cycle calibration re-anchors each cycle's marginals, and the generator conditions explicitly on a COLLECT_MODE covariate so that mode is modelled rather than ignored. Most importantly, the COVID break that carries the headline (+5.2 pp weekday at-home at 2015→2022) is far larger than any plausible mode effect and survives demographic standardization, so the principal behavioural signal cannot be a mode artefact.

---

### 7.7 The Single COVID-Persistence Scenario

The 2030 forecast is generated under a single demographic-and-behavioural scenario in which the COVID/work-from-home shift persists with probability one. The disposition is to frame this explicitly as the high-persistence bound rather than a central estimate: it is the upper end of plausible work-from-home retention, and the corresponding lower bound — a high-reversion counter-scenario in which in-home time decays toward the pre-pandemic baseline — is the natural sensitivity analysis. Adding that counter-scenario before submission would convert the point forecast into a bracketed range; at minimum, the single-scenario design is stated here as a scope boundary so that the 2030 numbers are read as a persistence-conditioned projection, not an unconditional prediction.

---

## References (this chapter)

*This chapter introduces no new numerical claims; all citations are reused from earlier chapters and listed for completeness.*

**Standards and methodological references** *(verify against master bibliography):*

- Aerts, D., Minnen, J., Glorieux, I., Wouters, I. and Descamps, F. (2014) A method for the identification and modelling of realistic domestic occupancy sequences for building energy demand simulations and peer comparison. *Building and Environment*, 75, pp. 67–78.
- ASHRAE (2023) *ANSI/ASHRAE Standard 55: Thermal Environmental Conditions for Human Occupancy.* Atlanta: ASHRAE.
- Eurostat (2018) *Harmonised European Time Use Surveys (HETUS) — 2018 Guidelines.* Luxembourg: Publications Office of the European Union.
- Herrmann, S.D. et al. (2024) *2024 Adult Compendium of Physical Activities.* — *(verify author list, publisher, and citation form against master bibliography)*
- ISO (2005) *ISO 7730: Ergonomics of the thermal environment — Analytical determination and interpretation of thermal comfort using calculation of the PMV and PPD indices and local thermal comfort criteria.* Geneva: International Organization for Standardization.
