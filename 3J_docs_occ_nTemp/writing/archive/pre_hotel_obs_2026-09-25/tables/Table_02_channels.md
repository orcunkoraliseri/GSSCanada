# Table 2 - The four channels and their provenance

Four occupancy channels drive four uses inside one stacked building, not four building archetypes.
Residential and Office are the two-channel stage's channels, reused; Retail is the one new survey
channel; Hotel is the one non-survey, tourism-statistics side-track.

| Channel | Source | Derivation | Injection mode | Scenario lever |
|---|---|---|---|---|
| Residential (AT_HOME) | GSS Time-Use | Census PUMF household linkage, occupant count driven by household size | REPLACE | none |
| Office (AT_WORK) | GSS Time-Use | Transformer Head 2; occupation-by-industry workforce linkage | MODULATE, NECB office density x AT_WORK fraction | Work-from-home band (conservative / hybrid / fully hybrid) |
| Retail (AT_RETAIL) | GSS Time-Use, new in this study | Derived from the survey's location and activity columns (§3.1); Transformer Head 3; one PNNL retail archetype as a population-level fraction | MODULATE, 0.95 x customer-hours shape | In-store share 2030 (0.90 / 0.97 default / 1.05), Quebec-Sunday sub-axis |
| Hotel | ISQ (Quebec) and CBRE / Travel Alberta (Alberta) monthly series | SARIMA(1,1,1)(1,1,1,12) per province with a COVID indicator, giving a monthly multiplier | MODULATE, NECB guest-room schedule x monthly multiplier | SARIMA band 2030 (0.92 / 1.00 / 1.05) |

Retail models customer presence only: the survey logs retail workers as at work rather than as a
retail activity, so staff density stays on the code baseline being modulated.

---

## Sources

- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`:
  - STEP 1 / STEP 2 box, lines 27-49 (GSS column reuse, no new GSS variables, AT_RETAIL derivation
    rule, retail-staff-invisible note, hotel monthly-series source, restaurant out-of-scope).
  - STEP 6 box, lines 86-102 (retail lever bands, QC-Sunday sub-axis, hotel SARIMA side-track,
    `hotel_multiplier` formula, `s(t)` shape).
  - STEP 7 box, lines 104-122 (Tag-2 dispatch: REPLACE for residential, MODULATE for office / retail /
    hotel; retail injection formula and staff-slot floor).
  - `## OPEN DECISIONS`, item 1 (line 265) - AT_RETAIL OR-rule text, exact frozen formula and leak
    cross-tab wording.
  - `## OPEN DECISIONS`, item 4 (line 268) - hotel diurnal shape `s(t)` resolution (dr_L3-05).
  - `## KEY DESIGN DECISIONS SUMMARY`, lines 218-234, rows "Hotel from provincial tourism stats
    (ISQ/CBRE), not GSS" and "Retail = customer presence only".

No em dashes or en dashes.
