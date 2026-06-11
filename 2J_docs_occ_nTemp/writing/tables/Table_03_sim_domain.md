# Table 3 — Simulation Domain: Archetype × City × Climate Zone

*Source:* `08_simulation.md` (confirmed assets + prerequisites); EPW filenames confirmed from `BEM_Setup/WeatherFile/` directory listing; `methodology_assessment_and_paper_skeleton.md` Part 3b Steps 7–8

| City | Province | ASHRAE climate zone | TMY weather file (EPW) | Archetype standard |
|---|---|---|---|---|
| Toronto | Ontario | 5A | `CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw` | NECB17/NBC936 Z6 |
| Kelowna | British Columbia | 5B | `CAN_BC_Kelowna.Intl.AP.712030_TMYx_5B.epw` | NECB17/NBC936 Z6 |
| Vancouver | British Columbia | 5C | `CAN_BC_Vancouver.Harbour.CS.712010_TMYx_5C.epw` | NECB17/NBC936 Z6 |
| Montréal | Québec | 6A | `CAN_QC_Montreal.Center-Jean.Brebeuf-McGill.Univ-McTavish.716120_TMYx_6A.epw` | NECB17/NBC936 Z6 |
| Calgary | Alberta | 6B | `CAN_AB_Calgary-Canadian.Olympic.Park.Upper.712350_TMYx_6B.epw` | NECB17/NBC936 Z6 |
| Winnipeg | Manitoba | 7A | `CAN_MB_Winnipeg.The.Forks.715790_TMYx_7A.epw` | NECB17/NBC936 Z6 |

**4 archetypes per city:** SingleDetached, OtherDwelling, MidRise, HighRise (Canadian NECB17/NBC936 Z6 code archetypes, not DOE prototypes); EnergyPlus v24.2. Atlantic provinces mapped to the Montréal EPW — stated limitation.

**Stock distribution (144,507 household frame):** SingleDetached 52.9% · MidRise 21.3% · OtherDwelling 13.0% · HighRise 12.8%.

**Base building model:** MTL set (`BEM_setup/Buildings_MTL/`), held fixed across all 6 climates. The single Z6 envelope under all climates is a deliberate isolation choice: the paired within-household design differences out the envelope, so only the occupancy × weather interaction varies.

**Cold-zone sensitivity:** `Buildings_CLG/` Z7A code archetypes (Calgary/Winnipeg) available as an optional EUI sensitivity.
