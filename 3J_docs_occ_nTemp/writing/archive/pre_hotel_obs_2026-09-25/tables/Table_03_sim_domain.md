# Table 3 - Simulation domain

The 56-cell campaign: two tower prototypes by two cities by fourteen scenarios. Areas below are parsed
from the model geometry as the sum of floor area times multiplier over the zones counted in the building
total, reproducing EnergyPlus's own total building area exactly. The two models per prototype differ by
36 bytes, the climate tag alone, so geometry is identical and EUI differences isolate climate.

| Prototype | Total area (m2) | Cities | ASHRAE CZ | Weather | Standard | Cells |
|---|---|---|---|---|---|---|
| SuperTall | 135,857.6 | Montreal, Calgary | 6A, 7A | TMYx, one file per city | NECB-2017 | 28 |
| Tall | 72,623.1 | Montreal, Calgary | 6A, 7A | TMYx, one file per city | NECB-2017 | 28 |

All 56 cells were simulated. The parsed area is identical on every run of a given prototype, across
scenario and city, confirming it as a geometry property rather than a per-run artefact. The Calgary
weather file is the same physical file used in the authors' prior single-channel study, where it is
reported against ASHRAE zone 6B; the campaign here assigns it zone 7A, so the two manuscripts label one
file differently by climate-zone standard and vintage.

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
  - "Etat verrouille" table, line 58 - "8B - IDF v24.2 | 4 IDF (Tall/SuperTall x
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
