# `D-S8-2` items 1, 3 and 4 — geometry, construction layers, and which archetype represents a cell

**Date:** 2026-08-24 (evening)
**Raised by:** preparing to answer *"is anything for Step 8 running?"* — nothing is, and these three
items are the whole reason why.
**Status:** OPEN. Nothing was changed. No IDF written, no builder edited, no table rebuilt.
`prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

**Evidence:** `Step8_docs/outputs_step8/archetype_parameters_{es,uk,it}.csv` and
`archetype_parameter_provenance.md` §5–§6. Every number below was re-derived from those three CSVs
today; none is quoted from the prose.

---

## 0. 🔴 Three corrections to the record, before any ruling

These are not opinions about the decisions. They are things the Step 8 documents currently state that
the files do not support, and two of them change what is actually being asked.

### 0.1 It is THREE open items, not five

`4thJ_08_bemSimulation.md` line 10 (STATUS) says *"**five** of the six geometry/zoning/load decisions
are still open (§6 items 1–4 and 6)"*. The same file at line 460, written later the same day, says
*"Section 6 items 2 and 6 are struck through; **items 1, 3 and 4 remain open**."* The provenance file
§6 agrees with line 460 — item 2 is marked CLOSED (one thermal zone per dwelling) and item 6 RULED
(diary-survey-year actual weather).

**The STATUS header is stale.** Open: **1 (geometry), 3 (layers), 4 (archetype selection)**.

### 0.2 🔴 `FINDING 107` — Italy has ZERO empty cells. The "42 of 48" in §5 counts an axis that does not exist

§5 reports `it` as *"42 of 48"* type × period cells and the STATUS prose speaks of *"6 empty IT
cells"*. Re-derived from `archetype_parameters_it.csv`:

| fold | dwelling types | periods | cells | filled | **empty** | rows |
|---|---|---|---|---|---|---|
| `es` | 4 | 6 | 24 | 24 | **0** | 24 |
| `uk` | 4 | 8 | 32 | 29 | **3** | 36 |
| `it` | 4 | 8 | 32 | **32** | **0** | 42 |

48 is `6 × 8`, and the 6 comes from counting `Code_BuildingType`, which for Italy holds **six** tokens
— `AB, MFH, MFH-AB, SFH, SFH-TH, TH`. But `MFH-AB` and `SFH-TH` are **composite rows spanning two of
the same four census types**, not two extra types. On the axis the census actually gives us,
`Code_BuildingSizeClass`, Italy has four types and **every one of its 32 cells is filled**. The 42
rows are 32 cells plus 10 duplicates.

**Consequence: item 4b is a `uk`-only question.** There are no Italian holes to fill.

### 0.3 🔴 `FINDING 108` — the 3 empty GB cells are an artefact of how the builder keyed merged rows, not a gap in TABULA

The three empty `uk` cells are `AB × GB.05`, `AB × GB.06`, `AB × GB.08`. Here is every `AB` row in the
file, with the period span its own code declares:

| assigned to | `Code_Building` | span the code declares |
|---|---|---|
| `GB.01` | `GB.ENG.AB.01.ApartmentBuildings.SyAv.001` | 01 |
| `GB.02` | `GB.ENG.AB.02-03.ApartmentBuildings.SyAv.002` | **02–03** |
| `GB.03` | `GB.ENG.AB.03.Gen.ReEx.001` | 03 |
| `GB.04` | `GB.ENG.AB.04-08.ApartmentBuildings.SyAv.005` | **04–08** |
| `GB.04` | `GB.ENG.AB.04.Gen.ReEx.001` | 04 |
| `GB.07` | `GB.ENG.AB.07.Gen.ReEx.001` | 07 |

`GB.ENG.AB.04-08` **explicitly covers GB.05, GB.06, GB.07 and GB.08.** The builder keyed it to
`Code_ConstructionYearClass`, which holds only its **first** period, so 05/06/08 read as empty while a
row that names them sits in the table. The same keying makes `AB.02-03` and `AB.03` overlap on GB.03.

**So item 4b is not "what do we invent for a cell TABULA never published".** TABULA published it. The
question is whether a merged row is allowed to represent every period it declares.

---

## 1. §6 item 1 — Geometry

### The fact

TABULA gives envelope **areas** (`A_Roof_1..2`, `A_Wall_1..3`, `A_Floor_1..2`, `A_Window_1..2`,
`A_Door_1`), a conditioned volume `V_C`, a reference floor area `A_C_Ref`, storey count `n_Storey` and
room height `h_room`. It gives **no shape**: no footprint aspect ratio, no rotation.

It also ships a compass split — `A_Window_Horizontal / East / South / West / North` — which looks at
first like it settles orientation for free. **It does not, and this is the second thing measurement
changed.**

🔴 **`FINDING 109` — the UK archetypes have NO south-facing and NO north-facing glazing at all.**

| fold | rows | `_East` > 0 | `_South` > 0 | `_West` > 0 | `_North` > 0 | `_Horizontal` > 0 | all four > 0 |
|---|---|---|---|---|---|---|---|
| `es` | 24 | 19 | 17 | 17 | 19 | 0 | 8 |
| `uk` | 36 | **36** | **0** | 27 | **0** | 0 | **0** |
| `it` | 42 | 29 | 38 | 28 | 25 | 0 | 9 |

Every one of the 36 GB archetypes puts its entire glazed area on **East and West**. Not one has a
square metre facing south. That is not an English building stock fact; it is a convention inside the
GB dataset — glazing assigned to two opposite facades with the compass labels carrying no meaning.
Spain and Italy split across all four.

Taking orientation from these columns would therefore give the `uk` fold a housing stock with **zero
south solar gain** while `es` and `it` get a real four-way split — a **country-correlated** difference
in heating and cooling demand, produced by a data convention, landing on exactly the fold the paper
already carries three asymmetries for (`D-S6-2` wave gap, `D-S5-1` census year, `FINDING 58` England
for the UK).

⚪ Two smaller facts from the same check. The compass split fails to sum to `A_Window_1 + A_Window_2`
in 8 `es` and 7 `uk` rows, but every one of those is rounding at **≤ 0.7 %** — except one real defect:
**`ES.ME.MFH.05.Gen.ReEx.001` has `A_Window_1 = A_Window_2 = 0` while its compass columns sum to
153.7 m².** An IDF built from the total column alone would give that archetype **no windows**. Italy
closes 42 of 42 exactly.

### The decision

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. One box per archetype; total glazed area distributed EQUALLY over the four vertical faces; compass columns not used for orientation.** Footprint from `A_C_Ref / n_Storey`, aspect ratio **1 : 1.5**, long axis east–west, height `n_Storey × h_room`, checked against `V_C`. | The one choice that treats the three folds identically. Orientation stops being a country-correlated variable, so the LOCO comparison is not contaminated by a GB dataset convention. Costs realism per building; the paper declares the box and the equal split as assumptions. Take the window area from the **compass sum** where the total column is zero, which repairs `ES.ME.MFH.05` |
| **(b)** | Use the TABULA compass columns literally — each area on its named face. | Uses a column TABULA actually publishes, and for `es`/`it` it is probably meaningful. But it hands the `uk` fold a stock with no south glazing, and the resulting cross-fold demand difference would be **unattributable** — partly occupancy, partly a labelling convention. `FINDING 109` would have to be quoted beside every cross-fold number |
| **(c)** | Compass columns for `es`/`it`, equal split for `uk`. | Fixes the physics per fold and **creates the asymmetry in the method itself**. The fold that gets special treatment is the fold whose result is then read differently. Worst of both |
| **(d)** | Aspect ratio and rotation become a pre-registered sensitivity, as `phi_int` did. | Removes the free parameter honestly. Multiplies a campaign that `D-S8-2` item 5 already multiplied by five — 510 archetype-runs per weather specification becomes 1,530 at three aspect ratios |

⚪ Under (a), (b) and (c) the geometry is one number the paper declares. Under (d) it is a measured
band. The recommendation is (a) **because of `FINDING 109`, not in spite of it** — the compass data is
unusable for the comparison this paper makes.

---

## 2. §6 item 3 — Construction layer build-up

### The fact

TABULA publishes **U-values** per surface (`U_Wall_1..3`, `U_Roof_1..2`, `U_Floor_1..2`,
`U_Window_1..2`, `U_Door_1`) and a thermal-bridging surcharge
(`delta_U_ThermalBridging_Original`). It publishes **no layers**. Thermal mass enters the EU boundary
set as a single lumped `c_m = 45 Wh/m²K` (provenance §6 item 3).

EnergyPlus needs layers. Recovering a layer stack from one U-value and one lumped capacity is an
inverse problem with **many** solutions, and which one is picked changes the dynamic response — the
time constant, the setback recovery, the peak — even when the steady-state U matches to the digit.
🔴 That matters here more than usual: **the dynamic response is what generated occupancy acts on.** A
schedule that turns heating off at 09:00 and on at 17:00 produces a different peak in a heavy wall
than in a light one at identical U.

### The decision

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Two-layer equivalent: one massless resistive layer per surface sized so `U` equals the TABULA value exactly, plus one mass layer sized so the construction's areal capacity reproduces `c_m = 45 Wh/m²K`.** | Both published quantities are hit **exactly and by construction**, in all three folds, with no country-specific step. The build-up is declared in the paper as a thermal equivalent, not as a real wall — which is true and is the honest form of the statement. Nothing has to be looked up outside the workbook |
| **(b)** | Use the named assemblies in `Tab.Building.Constr` (`ES.Wall.ReEx.01.01` …). | Physically real layers. But the provenance file records those assemblies as found for **Spain**; GB and IT presence is **not verified**, and a per-fold difference in whether real layers were available is another country-correlated method difference. The assembly U will not generally equal the archetype U, so one of the two published numbers has to give — and the archetype U is the one every other part of Step 8 is keyed to |
| **(c)** | One massless layer per surface for `U`, thermal mass carried by an `InternalMass` object sized to `c_m`. | Hits both numbers too, and is simpler to write. The mass couples to zone air rather than sitting inside the envelope, so it damps the zone but does not delay conduction through the wall — the setback recovery, which is the occupancy-sensitive quantity, behaves differently from (a). Defensible, but it moves the mass to the wrong side of the envelope |
| **(d)** | Layer distribution as a pre-registered sensitivity (light / medium / heavy at fixed U and fixed `c_m`). | The only option that **measures** how much the choice is worth instead of assuming it away. Triples the campaign again. Worth considering precisely because the quantity it perturbs — dynamic response to a schedule — is the paper's own subject |

⚪ If the author wants one sensitivity in Step 8 beyond `phi_int`, **(d) here is a better buy than
(d) under item 1**: aspect ratio moves solar gain, which the occupancy signal does not touch, whereas
thermal mass moves exactly the quantity a schedule acts on.

---

## 3. §6 item 4a — Which row represents a cell, where two exist

### The fact

7 `uk` cells and 10 `it` cells carry two rows. Spain carries none. **No pair is redundant** — every
one differs in fabric, and most differ in size:

| fold | cell | the two rows | `A_C_Ref` m² | numeric fields differing (of 10 checked) |
|---|---|---|---|---|
| `uk` | AB × GB.04 | `AB.04-08.ApartmentBuildings.SyAv.005` / `AB.04.Gen.ReEx.001` | 1,080.2 / **4,357.1** | 6 |
| `uk` | SFH × GB.01 | `SFH.01.Detached.SyAv.001` / `SFH.01.Gen.ReEx.001` | 216.4 / 198.0 | 5 |
| `uk` | SFH × GB.02 | `SFH.02-03.Detached.SyAv.002` / `SFH.02.Gen.ReEx.001` | 149.4 / 153.4 | 5 |
| `uk` | SFH × GB.04 | `SFH.04-08.Detached.SyAv.005` / `SFH.04.Gen.ReEx.001` | 144.3 / 123.1 | 5 |
| `uk` | TH × GB.01 | `TH.01.Terraced.SyAv.001` / `TH.01.Gen.ReEx.001` | 110.1 / 104.6 | 5 |
| `uk` | TH × GB.02 | `TH.02-03.Terraced.SyAv.002` / `TH.02.Gen.ReEx.001` | 91.2 / 93.0 | 5 |
| `uk` | TH × GB.04 | `TH.04-08.Terraced.SyAv.005` / `TH.04.Gen.ReEx.001` | 85.6 / 85.3 | 5 |
| `it` | MFH × IT.01 | `MFH-AB.01-03.Gen` / `MFH.01.Gen` | **1,035.0 / 549.9** | 4 |
| `it` | MFH × IT.04 | `MFH-AB.04-05.Gen` / `MFH.04.Gen` | 822.0 / 817.1 | 5 |
| `it` | MFH × IT.06/07/08 | `MFH-AB.0n.Gen` / `MFH.0n.Gen` | ≈ equal | 2–3 |
| `it` | SFH × IT.01 | `SFH-TH.01-03.Gen` / `SFH.01.Gen` | 115.0 / 139.0 | 4 |
| `it` | SFH × IT.04 | `SFH-TH.04-05.Gen` / `SFH.04.Gen` | 156.3 / 162.0 | 3 |
| `it` | SFH × IT.06/07/08 | `SFH-TH.0n.Gen` / `SFH.0n.Gen` | **identical** | 1–2 (`U_Wall_1`, `U_Window_1`) |

🔴 **Two pairs are not a choice between similar buildings.** `uk AB × GB.04` differs by a factor of
**4.0** in reference floor area (1,080 against 4,357 m²) and `it MFH × IT.01` by a factor of **1.9**.
Whatever rule is adopted, those two cells move a lot.

⚪ In `it` at IT.06/07/08 the composite and the simple row are the **same building** — identical
areas, differing only in `U_Wall_1` (and `U_Window_1` at IT.08). The choice is nearly vacuous there
and bites only at IT.01–IT.05.

⚪ The two families are distinguishable by name: `…Gen.ReEx.001` against
`…<SpecificName>.SyAv.00N` in `uk`, and `…MFH-AB…/…SFH-TH…` against `…MFH…/…SFH…` in `it`. What those
suffixes mean inside TABULA was **not** verified from the workbook and is not asserted here.

### The decision

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. Prefer the `Gen` row wherever one exists; use the specific/composite row only where no `Gen` row does.** | One rule, stated once, applied identically in `uk` and `it`, and vacuous in `es` — so the selection rule adds **no fourth country asymmetry**. It also resolves every one of the 17 duplicate cells, because a `Gen` row exists in all of them |
| **(b)** | Prefer the most specific row — map census dwelling type onto `Detached` / `Terraced` / `ApartmentBuildings`, composite only as fallback. | Closer to the real stock, and it uses information TABULA took the trouble to publish. But the mapping is written per country, so the **method itself becomes country-dependent**, and for Italy `MFH-AB` is *less* specific than `MFH`, so "most specific" points in opposite directions in the two folds |
| **(c)** | Both as a pre-registered two-arm sensitivity; report the spread. | Turns the choice into a measured number instead of an assumption. Doubles the campaign. `es` has no duplicates at all, so one third of the design contributes nothing to the arm — it measures a `uk`/`it` effect only |
| **(d)** | Population-weight the two rows within the cell. | Avoids discarding either. Requires stock shares TABULA does not give, so it would import a new unsourced number — `FINDING 47` class |

---

## 4. §6 item 4b — The three `uk` cells that read as empty

Read `FINDING 108` (§0.3) first: `GB.ENG.AB.04-08` already declares GB.05, GB.06 and GB.08.

### The decision

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. A merged-period row represents every period its own code declares.** `AB.04-08` is expanded across GB.04–GB.08; `AB.02-03` across GB.02–GB.03. The `uk` grid then closes at 32 of 32 with nothing invented, and where the expansion collides with a single-period row the item-4a rule (`Gen` preferred) settles it. | Nothing is fabricated; TABULA's own scope statement is honoured. **Requires a builder change** — the row key becomes the declared span, not `Code_ConstructionYearClass` — plus a re-run of `tools/4thJ_step8_tabula.py`. Additive: no parameter value changes, only which cells point at which row |
| **(b)** | Drop the three cells and re-normalise the `uk` population weights over the 29 that remain. | Nothing invented and no builder change. But it discards a published row that names those periods, and it means the `uk` fold silently covers a smaller share of its census grid than `es`/`it` — a coverage difference that then has to be reported per fold |
| **(c)** | Fill each empty cell from the nearest construction period of the same type, ignoring the merged rows. | One rule, no builder change, and it happens to land on roughly the right buildings. It is also **the wrong reason** — it treats as a gap something TABULA filled, and it would be indefensible if a reader opened the workbook |

⚪ Under (a), if the AB `Gen` row at GB.07 is preferred over the expanded `04-08` row by the item-4a
rule, GB.07 keeps its own building and only 05/06/08 take the merged one. That is the intended
interaction of the two rulings, not a conflict.

---

## 5. What this document does NOT settle, and what stays blocked either way

* 🔴 **Decision 14 (chaining) still blocks the whole step.** `4thJ_08_bemSimulation.md` says it
  plainly: without a chaining rule there is no annual schedule to run. All four rulings above can be
  taken today and **no IDF can be simulated** until 14 closes.
* 🔴 **The weather files for the ruled §6 item 6 are not acquired**, and the AMY licence question
  (`L27` Part B) is unverified. Until all three are on disk **no weather-driven number may be quoted
  at all**.
* 🔴 **The TABULA licence was never verified** — `RL24`'s claim about redistribution of derived tables
  remains unchecked. It blocks **publishing** a derived parameter table, not using one internally.
* 🔴 `G8.1`–`G8.4` still have no reference series; `D-S8-1` (a) re-pointed them to reproducibility
  gates and nothing here changes that. **No Step 8 gate has been run, and none has been seen failing.**
* ⚪ Items **8.2–8.6 are untouched**.

---

## 6. How to answer

Four letters is enough — for example *"1(a), 3(a), 4a(a), 4b(a)"*. Anything ruled other than (a) is
equally fine and will be applied as written; the recommendations are argued above, not assumed.

If a ruling lands on (d) anywhere, say so explicitly, because those are the ones that change the size
of the campaign rather than only its content.

Once ruled, the sequence is: apply 4a and 4b to the builder (additive, re-runnable, no parameter value
moves), then items 1 and 3 become the IDF writer — which is work item 8.1 proper, and the first Step 8
artefact that has ever existed.
