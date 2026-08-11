# Table 3 - Simulation domain

The 56-cell Step-8 campaign: two tower prototypes x two cities x 14 scenarios. Surfaces below are the
corrected, parsed values (an implementation correction recorded 2026-07-31) - Sigma(`FloorArea` x `Multiplier`) on
`IsPartOfTotalArea = 1` zones, reproducing EnergyPlus's own *Total Building Area* exactly. The two
IDFs per prototype (Montreal / Calgary) differ by 36 bytes only - geometry is identical, the
climate tag is the sole difference, so EUI deltas isolate climate.

| Prototype | Total area (m2) | Cities | ASHRAE CZ | EPW | Standard | Cells |
|---|---|---|---|---|---|---|
| SuperTall | 135,857.6 | CAN_MTL, CAN_CLG | 6A (Montreal), 7A (Calgary) | TMYx, one per city (filenames in the footnote) | NECB-2017 | 28 |
| Tall | 72,623.1 | CAN_MTL, CAN_CLG | 6A (Montreal), 7A (Calgary) | TMYx, one per city (filenames in the footnote) | NECB-2017 | 28 |

Footer: 56/56 cells simulated, geometry-identical IDFs across cities. `agg_meta.csv` records
`total_building_area_m2` = 135,857.594... (SuperTall) and 72,623.070... (Tall) on every one of the 56
rows, unchanged across scenario and city - confirming area is a building-geometry property, not a
per-run artefact.

## Footnote - the weather files, and why the Calgary filename carries a "6B" tag

The two weather files are `CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw`
(Montreal) and `CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw` (Calgary), each used by
both prototypes in its own city.

The Calgary EPW file is named with a `_6B` suffix on disk (`CAN_AB_Calgary-...712350_TMYx_6B.epw`),
but the campaign driver assigns it climate zone Z7A (`cz: "Z7A"` in `CITIES`, confirmed in every
Calgary row of `agg_meta.csv`). This is not a transcription error: the driver's own docstring names it
explicitly ("EPW tagged `_6B` on disk ... NOT renamed per instruction") and elects to keep the file's
original name rather than rename it to match the zone label used in the NECB-2017 analysis. The same
EPW file (`_6B` in its filename) is also used by the authors' prior single-channel study, where it is reported against
ASHRAE zone 6B (`2J_docs_occ_nTemp/writing/tables/Table_03_sim_domain.md`) - i.e. the same physical
weather file is legitimately labelled differently by climate-zone standard/vintage across the two
manuscripts. Montreal's EPW, by contrast, is filed as `_6A` and reported as CZ 6A in both.

---

## Sources

- `Leg3_4-split/Step8_docs/3rdJ_08D_campaign_cells.py`, lines 137-146 (`CITIES` list: city label, CZ,
  IDF sub-directory, IDF climate-zone tag, EPW filename, province) and lines 115-125 (docstring: 2
  buildings x 2 cities, `_6B`-tagged Calgary EPW not renamed, IDF stock reused from
  `Leg2_2-split/Step8_docs/outputs_step8/office_idfs_v242/{CAN_MTL,CAN_CLG}/`).
- `Leg3_4-split/Step8_docs/outputs_step8/agg_deliverable/agg_meta.csv`, header + all 56 data rows -
  `total_building_area_m2` = 135857.59426106038 (SuperTall, every SuperTall row) and
  72623.06993958 (Tall, every Tall row); `cz` column = `Z6` (MTL rows) / `Z7A` (CLG rows).
- `Leg3_4-split/Step8_docs/3rdJ_08_implementation_improvements.md`:
  - "Etat verrouille au 2026-07-28" table, line 58 - "8B - IDF v24.2 | 4 IDF (Tall/SuperTall x
    MTL/CLG) verifies sur scratch, reutilises de l'etape a deux canaux. Chaque paire MTL/CLG differe de 36 octets ->
    geometrie identique, tag climat seul."
  - Section "Defaut 7" (lines 499-546) - parsed occupiable-share table for the Tall tower, total
    floor area 72,623.1 m2 reproduced exactly by Sigma(FloorArea x Multiplier), method for the
    SuperTall figure (135,857.6 m2) parsed identically.
  - Section "C-bis" (lines 676-701) - md5 of the 4 reused IDF files, confirmed cluster-local match,
    36-byte MTL/CLG delta re-confirmed.
- `3rdJ_00_4split_Occupancy_Pipeline_Overview.md`, header blockquote (lines 10-19) and STEP 8 box
  (lines 122-136) - the corrected SuperTall/Tall totals (135,857.6 / 72,623.1 m2, superseding
  40,846 / 26,750 m2) and the "2-city sweep: CAN_MTL Z6 (6A) + CAN_CLG Z7A -- geometry-identical
  IDFs" statement.

No em dashes or en dashes.
