# Table 5 — Annual EUI vs NRCan SHEU Plausibility Bands

*Source:* `methodology_assessment_and_paper_skeleton.md` Part 1 Q1.2 + Part 3b Steps 7–8 (v2 corrected campaign; manager-verified 2026-06-10)

| Archetype | SHEU dwelling type | Simulated EUI (kWh/m²) | SHEU national central (kWh/m²) | SHEU band (regional range, kWh/m²) | Within band? |
|---|---|---|---|---|---|
| SingleDetached | Single detached | 208 | 155.6 | 130.6 – 186.1 | **No — above upper (≈ +12%)** |
| OtherDwelling | Single attached (double / row / terrace / duplex) | 128 | 144.4 | 136.1 – 186.1 | **Marginal — ≈ 6% below lower** |
| MidRise | Apartment, low-rise (< 5 storeys) | 152 | 144.4 | 111.1 – 216.7 | Yes |
| HighRise | Apartment, high-rise (≥ 5 storeys) | 117 | 130.6 | 113.9 – 147.2 | Yes |

**Notes:**
- **Simulated EUI** values are from the Step-8 v2 corrected campaign (`953111` + `954135` + Sub-step 8G `954296/954300`), manager-verified 2026-06-10. Exact recomputed values: SingleD 208.13, MidRise 151.79, OtherDwelling 127.80, HighRise 117.01 kWh/m² (rounded to integers above; ordered by envelope-to-occupant ratio).
- **SHEU bands now sourced** (resolves the earlier ⚠ cells): NRCan *2019 Survey of Household Energy Use* — national central = **Table 3.3b** (Energy Intensity Per Heated Area excluding Garage, by Dwelling Type); regional range = **Table 3.3a** (same metric, by region: Canada / Atlantic / Quebec / Ontario / Manitoba–Saskatchewan / Alberta / British Columbia). Total all-fuels (secondary/site energy), per **heated** area **excluding basement and garage**. Conversion 1 GJ = 277.78 kWh. U-flagged (suppressed) regional cells excluded from the range. Tables released/modified 2023-07-06. See `deepResearch/Canadian Residential Energy-Use Intensity by Dwelling Type (NRCan)…md`.
- **Floor-area basis — reconciled (2026-06-11).** A direct check of the simulated IDFs (`BEM_setup/Buildings_MTL_v242/`) confirms the EUI denominator is EnergyPlus *Net Conditioned Building Area* — conditioned zones only, with the unconditioned basement and attic excluded — which coincides with SHEU's heated-area-excluding-basement/garage basis. For SingleDetached the simulated and SHEU denominators are the same (≈221 m²: 12.13 × 9.10 m × 2 storeys), so the ≈+12% over-band reading is **not** a denominator artifact. The elevation is genuine and sits in the *space-heating* component — a total-energy quantity fixed by the NECB/IECC envelope and Zone-6 weather, which (unlike equipment + lighting) was not SHEU-calibrated. For the apartment archetypes the simulated building EUI divides by floor area that includes common corridors; re-normalizing to per-dwelling-unit area (×1.11) raises MidRise to ≈168 and HighRise to ≈130 kWh/m², both still inside their SHEU low-/high-rise ranges. Reconciliation detail: `deepResearch/EUI_floor_area_reconciliation.md`.
- **What actually passed validation.** The hard calibration gate was on **per-household end-use kWh/yr** (net-after-fridge anchors; 48/48 dwelling-by-year cells within ±2.7% of SHEU, max +2.33% equipment / +2.63% lighting — Step-9 manager-verified 2026-06-10). The EUI-per-m² check above is a **secondary plausibility cross-check**, and on it two of four archetypes fall outside the SHEU *regional-average* intensity range (SingleDetached above; OtherDwelling marginally below). Regional averages smooth within-province variance, so a single cold-zone archetype legitimately can exceed them — but the table should state this honestly rather than assert a blanket "within band."
- v2 vs v1 Δ: SingleD +2.85%, MidRise −0.47%, OtherDwelling +1.69%, HighRise +0.64% (SingleD shift = phase-roll + 2022/2030 provenance correction, not a calibration failure).
- Ordered by envelope-to-occupant ratio (colder zones higher within each archetype type).

**Step-8 v2 corrected campaign, verified 2026-06-10. Scorecard: 24 PASS / 0 WARN / 3 INFO / 0 FAIL.**
