# Table 2 - The four channels and their provenance

Four occupancy channels drive four uses inside one stacked building (not four building archetypes;
see Standing rules). Residential and Office are the two-channel stage's channels, reused; Retail is the one new GSS
channel; Hotel is the one non-GSS, tourism-statistics side-track.

| Channel | Source | Derivation | Injection mode | Scenario lever |
|---|---|---|---|---|
| Residential (AT_HOME) | GSS Time-Use | Census PUMF household linkage; `Number_of_People_Schedule` = `HHSIZE` | REPLACE | none |
| Office (AT_WORK) | GSS Time-Use | Transformer Head 2; NOCxNAICS workforce linkage | MODULATE, NECB office density x AT_WORK fraction | WFH band (conservative / hybrid / fullyhybrid) |
| Retail (AT_RETAIL) | GSS Time-Use, new in this study | Derived from `occPRE`/`occACT` (footnote 1); Transformer Head 3; one PNNL retail archetype as a population-level fraction | MODULATE, People = 0.95 x shape_cd(t) in customer hours (footnote 2) | In-store share 2030 (0.90 / 0.97 default / 1.05), QC-Sunday sub-axis |
| Hotel | ISQ (Quebec) and CBRE / Travel Alberta (Alberta) monthly series | SARIMA(1,1,1)(1,1,1,12) per province with a COVID indicator (2020-03 to 2022-06), giving `hotel_multiplier(t,month,PR)` | MODULATE, NECB guest-room schedule x `hotel_multiplier` | SARIMA band 2030 (0.92 / 1.00 / 1.05) |

## Footnotes

1. AT_RETAIL rule, frozen 2026-07-02.

```
AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE in {5, 9})
```

Location-mapping detail by cycle: 2005/2010 `PLACE = 06+07`; 2015 `LOCATION = 306`; 2022
`LOCATION = 3306`. The activity arm (`occACT == 4`, "Purchasing Goods & Services") is gated to
`occPRE in {5, 9}` specifically to exclude the online-shopping wrinkle
`occACT == 4 & occPRE == 1` (shopping from home) from being counted as retail presence. That
online-shopping leak cross-tab is still reported per cycle as a verification check, even though the
rule itself is frozen and not reopened by it. Restaurant presence (`occPRE == 7`) is available in all
cycles and is explicitly out of scope (no prototype Space to drive it).

2. Retail staff are invisible in GSS. Retail workers are logged as AT_WORK (the office channel),
not as a retail-specific activity, so no GSS signal exists for staff presence. Staff-only slots
therefore stay on the NECB baseline density, and the retail channel models customer presence
only - worker density already lives in the NECB baseline being modulated.

---

## Sources

- `Leg3_4-split/3rdJ_00_4split_Occupancy_Pipeline_Overview.md`:
  - STEP 1 / STEP 2 box, lines 27-49 (GSS column reuse, no new GSS variables, AT_RETAIL derivation
    rule, retail-staff-invisible note, hotel monthly-series source, restaurant out-of-scope).
  - STEP 6 box, lines 86-102 (retail lever bands, QC-Sunday sub-axis, hotel SARIMA side-track,
    `hotel_multiplier` formula, `s(t)` shape).
  - STEP 7 box, lines 104-122 (Tag-2 dispatch: REPLACE for residential, MODULATE for office / retail /
    hotel; retail injection formula and staff-slot floor).
  - `## OPEN DECISIONS`, item 1 (line 265) - AT_RETAIL OR-rule text, RESOLVED 2026-07-02, exact frozen
    formula and leak cross-tab wording.
  - `## OPEN DECISIONS`, item 4 (line 268) - hotel diurnal shape `s(t)` resolution (dr_L3-05).
  - `## KEY DESIGN DECISIONS SUMMARY`, lines 218-234, rows "Hotel from provincial tourism stats
    (ISQ/CBRE), not GSS" and "Retail = customer presence only".

No em dashes or en dashes.
