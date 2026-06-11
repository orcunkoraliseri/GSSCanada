# Table 5 — Annual EUI vs NRCan SHEU Plausibility Bands

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 1 Q1.2 + Part 3b Steps 7–8 (v2 corrected campaign; manager-verified 2026-06-10)

| Archetype | Simulated EUI (kWh/m²) | SHEU lower band | SHEU upper band | Within band? |
|---|---|---|---|---|
| SingleDetached | 208 | ⚠ check source | ⚠ check source | Yes |
| MidRise | 152 | ⚠ check source | ⚠ check source | Yes |
| OtherDwelling | 128 | ⚠ check source | ⚠ check source | Yes |
| HighRise | 117 | ⚠ check source | ⚠ check source | Yes |

**Notes:**
- Simulated EUI values are from the Step-8 v2 corrected campaign (`953111` + `954135` + Sub-step 8G `954296/954300`), manager-verified 2026-06-10. Exact manager-recomputed values: SingleD 208.13, MidRise 151.79, OtherDwelling 127.80, HighRise 117.01 kWh/m² (rounded to integers above for reporting; ordered by envelope-to-occupant ratio).
- v2 vs v1 Δ: SingleD +2.85%, MidRise −0.47%, OtherDwelling +1.69%, HighRise +0.64% — all within NRCan SHEU bands; SingleD shift is phase-roll + 2022/2030 provenance correction, not a calibration failure.
- SHEU band lower/upper bounds: the source documents confirm all four archetypes fall within NRCan SHEU plausibility bands but do not quote the band boundaries as explicit lower/upper numbers for EUI (kWh/m²). The SHEU 2019 report publishes end-use kWh/hh·yr totals (not EUI bands); the EUI plausibility check is described as being within "NRCan SHEU bands" in the pipeline documentation. **Numeric band boundaries require direct lookup in NRCan SHEU 2019 Table C or equivalent — not found in pipeline source docs.**
- Ordered by envelope-to-occupant ratio (colder zones higher within each archetype type).

**Step-8 v2 corrected campaign, verified 2026-06-10. Scorecard: 24 PASS / 0 WARN / 3 INFO / 0 FAIL.**
