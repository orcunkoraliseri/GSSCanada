# D2-8: 5J multi-zone building model (design, manager, 2026-09-30 ~15:45 EDT; stamp corrected from `date`)

**Ruling (author, 2026-09-30, earlier afternoon):** "we need to divide to the floors and thermal zones, it is not acceptable
one zone one builidng"; precedent = 3J and 4J ("please learn from them"). Memory rule
`feedback_multizone_per_building.md`.

## What 3J and 4J did (builder study, Explore helper, 2026-09-30; code read only)
* **4J Step 10 (OpenUBEM, `tools/4thJ_step10_nocore_campaign.py`)**: one zone per dwelling, no core, every m2 in
  a flat; zones `<id>_F<storey>_dwelling_<j>`; inter-dwelling walls and floors/ceilings paired; each dwelling its
  OWN seeded Step 7 draw (`4thJ_step10_assign.py:270-300`), no focal dwelling. Limits for 5J: tied to real
  OpenUBEM footprints (not a TABULA row), heating only, no windows, no People object, no meters, repeated vertex
  mismatch failures (FINDINGs 210, 221, 253, 254), UK paths hard-coded (fold "uk", Step 7 index reads every fold).
  About 28-30 s EnergyPlus time for a 16-zone building (step8 box: about 2 s).
* **3J (`eSim_bem_utils_3J`)**: DOE/PNNL prototype IDFs, several unit zones, but `inject_schedules` gives EVERY
  unit the SAME household. Cannot take a TABULA row.
* **Lesson taken:** per-dwelling zones and per-dwelling seeded households (4J Step 10); floors stacked with paired
  floors/ceilings; keep the TABULA physics of the 4J Step 8 box so single-zone and multi-zone results compare.
  Neither builder is usable as is.

## Design (manager; geometry is settled by the ruling, placement items marked ASK go to the author)
1. **Keep `derive(row)` of `4thJ_step8_idf.py` unchanged** (imported, never copy-edited): plate W x D (aspect
   solved from TABULA wall area, D-S8-3a), n_Storey floors of h_room, TABULA U-values, glazing split equally over
   the four facades, total capacity c_m x A_C_Ref.
2. **Floors:** n_Storey floors (integer in all 24 Spanish rows), each h_room high, stacked. Roof on the top floor
   only; ground contact on the ground floor only; floors/ceilings between storeys are paired interzone surfaces.
3. **Dwellings per floor (k):** SFH and TH: k = 1 (the one dwelling spans all floors, one zone per floor).
   MFH and AB: k dwellings side by side along the long E-W axis, each (W/k) x D, full depth (every dwelling has a
   north and a south facade; the two end dwellings also get east/west). k from TABULA's own dwelling count if
   `tabula-values.xlsx` has one for the row (k = n_dwellings / n_Storey, rounded; recorded); if not, the
   manager rules k from the measured TABULA numbers (no number is invented in the builder; k is an argument).
   Party walls between dwellings are paired interzone surfaces.
4. **Windows:** every exterior wall segment gets the same window fraction as its 4J facade (so the total glazed
   area equals 4J `win_total` exactly).
5. **Mass (ruling 3(a) kept):** total capacity c_m x A_C_Ref conserved, spread per m2 over ALL opaque surfaces
   (exterior + interior floors + party walls, each interior pair counted once).
6. **Interior constructions (ASSUMED, written in the IDF header):** interior floor = capacitive layer + resistive
   R 0.35 m2K/W; party wall = capacitive layer + resistive R 0.50 m2K/W. Author may change.
7. **Per zone:** its own IdealLoads, dual setpoint 20/26 C, infiltration ACH of the building row, E_PHI_INT at 0 W
   (phi_zero kept), People + ElectricEquipment from the dwelling's household. A dwelling that spans several
   floors (SFH, TH) splits people and appliance design level over its zones by floor-area share, same schedules.
8. **Outputs per zone, hourly:** IdealLoads heating and cooling energy, Electric Equipment Electricity Energy;
   facility meters kept. Target per dwelling = sum of its zones; per m2 = over the DWELLING floor area.
9. **Check against the old box:** a "collapse" mode (1 floor of full height, k = 1) must reproduce the 5J
   single-zone wrapper's annual heating and cooling (the physics carry-over gate).

## ASK the author (sent 2026-09-30 with this design, stamps corrected)
* **A. Who lives in the other dwellings.** Recommend: the design household sits in ONE focal dwelling per building
  (position drawn once per building with a seed, fixed for all its households); the other dwellings get FIXED
  seeded households from the country's diary pool outside the 60 design households (4J Step 10 precedent), the
  same in every run on that building. Then two runs on one building differ ONLY by the focal household, and the
  paired occupancy effect stays clean. Alternative: every dwelling gets its own design household and every
  dwelling is a training row (more rows per run, but neighbours change between runs, so pairs are no longer clean).
* **B. Electricity.** In the pilot, electricity equals the appliance schedule times its design level
  (P003 = P011 = P029 = P037 on four different buildings): EnergyPlus adds nothing. Recommend: do not score the
  surrogate on electricity; compute it directly from the schedule and report it beside the model. Alternative:
  add heating/cooling electricity with a fixed efficiency so the target depends on the building.

## Work order
1. Builder (employee): `tools/5thJ_idf_mz.py` + TABULA dwelling count + tests on Speed
   (`2026-09-30_wp1_multizone_builder_TASK.md`). Does not depend on A or B.
2. After A and B: pilot rebuild (50 runs, Spain, Madrid), checker update (4.3 absent = presence 0; per m2 over the
   dwelling area), re-time, redo the O-3 run-count arithmetic.

## RULED by the author (2026-09-30 ~15:50 EDT, answers to A and B)
* **A = "Every flat is tested".** Every dwelling gets its own design household and every dwelling is a training
  row (4J Step 10 precedent: per-dwelling seeded draws). No focal dwelling, no fixed neighbours. Consequence for
  the design tables: a run on a building with n dwellings places n design households (seeded permutation of the
  country's 60, repeated as needed so each household visits every building and varied floor/end positions);
  SFH/TH still one household per run. The run count falls for MFH/AB; redo the O-3 arithmetic after the re-pilot.
* **B = "electricity, heating, cooling, equipment".** Manager's reading, four hourly targets per dwelling:
  heating, cooling, equipment (appliance) electricity, and total electricity = equipment + heating/COP_h +
  cooling/COP_c. The efficiencies are ASSUMED (manager, pending the author's numbers): COP_h 3.0, COP_c 3.0
  (reversible heat pump), applied at extraction and written in the run manifest. If the author meant something
  else by "electricity" (e.g., lighting), this line changes.

## Outputs widened (author, 2026-09-30 ~15:52 EDT): "for energy outputs, if necessary get out all possible outputs, perforamnce, heating, cooling, lighting, equipment, etc."
Every run writes, hourly and per zone: IdealLoads heating and cooling (total, sensible, latent, supply and zone
side); equipment electricity; lighting electricity (only if a lighting schedule exists in the 4J path; the builder
does not invent a Lights object: if none exists, record that and the manager asks the author); people heat gain;
infiltration heat gain and loss; window heat gain and loss, transmitted solar; zone mean air and operative
temperature, humidity; thermostat unmet hours (heating and cooling, performance). Plus end-use meters
(Heating, Cooling, InteriorEquipment, InteriorLights, Electricity:Facility), the annual summary tables and
the unmet-hours report. Total electricity with COP 3.0 (ASSUMED) is still computed at extraction. Disk per run is
re-measured in the re-pilot before the campaign size is set.
