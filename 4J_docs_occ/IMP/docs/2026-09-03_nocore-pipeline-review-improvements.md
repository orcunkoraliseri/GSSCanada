# No-core review — pipeline-wide improvements, implementation document

**Created** 2026-09-03 · **Status** 🟡 **PROPOSALS. NOTHING APPLIED. Three decisions wait on the author (`D-IMP-1`, `D-IMP-2`, `D-IMP-3`, §11); everything else is additive housekeeping the next session executes once they are ruled.**
**Origin** The owner's **no-core ruling** on the OpenUBEM side — `D-EU-79` / `D-EU-80` / `D-EU-81` (2026-09-02), `D-EU-82`–`D-EU-88` (2026-09-03) — plus a full read of Steps 0 to 11 asked for by the author on 2026-09-03.
**Inputs**
`OpenUBEM/docs/docs_ACTIVE/europeanLocations/rules/RULES_dwelling_layout_groups_nocore_2026-09-02.html` ·
`…/rules/RULES_context_geometry_simulation_nocore_2026-09-02.md` · `…/rules/EXAMPLE_dwelling_layout_validation_nocore_2026-09-02.md` ·
`…/STATE_european_locations_v5.md` · `…/implementation/PLAN_eu21-nocore-2026-09-02.md` · `…/implementation/PLAN_eu21-district-viewer-2026-09-03.md` · `…/messages_GSSCanada/DONE/` ·
`4thJ_00_HETUS_LLM_Pipeline.md` · `4thJ_00_HETUS_LLM_Pipeline_Overview.md` · `Step0_docs` … `Step11_docs` ·
the retained Step 10 run trees `_local_runs/step10_realstock_speed410/` (410 IDFs) and `Step10_docs/outputs_step10/realstock_campaign/manifests/` (410 manifests).
**Targets** `Step8_docs/IMP_step8/` · `Step10_docs` · `Step11_docs` · `4thJ_00_HETUS_LLM_Pipeline.md` · the board `4thJ_CHECKLIST.html` · `writing/4thJ_writeup_notes.md`.
**Tool written today** `tools/4thJ_imp_nocore_void_census.py` → `IMP/docs/2026-09-03_nocore_void_census.csv`, `IMP/docs/2026-09-03_nocore_projection_41.csv` (read-only over retained artefacts; no EnergyPlus, no network, no cluster).

> **Nothing here is applied.** Every item below is a proposal with its evidence, its cost and the
> perturbation that must be seen felling it. No registered basis moves: the closed Step 10 board
> (18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE) is **not re-scored**, `prereg.md`
> md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched, the 149 stay barred at cell level
> (`D-EU-31`), option (c) is never re-proposed, and **no compute is proposed for now** — `D-EU-55`
> binds the OpenUBEM side (no EnergyPlus run without the owner's own sentence) and nothing on the
> 4J side is authorised. What this document does is say **where the ruling lands, what it changes,
> what it does not change, and what the 4J side can write now so that the next campaign starts
> with the fields, the binding and the tolerance it needs.**

---

## 0-bis. Provenance firewall

Two categories, both ours to use:

| Category | Status | Items |
|---|---|---|
| **A. Audit of our own docs and retained artefacts** | ✅ ours outright | `FINDING 195`, `FINDING 196`, the N_u projection, every stale-text item, the contract items |
| **B. The owner's own ruling in the sibling tree, and the author's own published method** | ✅ ours, cited to the ruling | `D-EU-79`–`D-EU-88` quoted verbatim from `STATE_european_locations_v5.md`; Iseri et al. (2025), *Energy & Buildings* 337, 115620, Fig. 4 (the author's own paper); the literature ranges in `DR02`/`DR03`, which are public and cited there |

**The test for any future item:** *could I have arrived at this by reading the ruling, by auditing our own artefacts, or from a published source?* Everything below passes it. No third-party manuscript is involved.

---

## 0. Summary — where the ruling lands, in one paragraph

The no-core ruling lands on **exactly three places** in our tree and nowhere else. **(1)** The **unexecuted** Step 8 "unified OpenUBEM" plan (`Step8_docs/IMP_step8/`) and its `DR01`–`DR04` dossier recommend the very thing the owner has now retired: an unconditioned stair core at 6–12 % of gross floor area, a double-loaded corridor spine, `b_u` = 0.50–0.80, the `units_corridor` diagram. **(2)** Step 10's **population basis** — the Arm D / Arm F split, "the census decides the arm", `G10.19`'s 30-per-fold floor, the 18-of-297 yield — all of which are properties of the **parked** layout generator's refusal taxonomy, not of the building stock. Step 10's **numbers** are not touched: measured today, the 18 Arm D buildings carry **no core zone at all** and fill the census footprint on **58 of 73 storeys**; on the other **15 storeys in 6 buildings** the upper storeys are stepped back (`FINDING 195`), which the no-core storey rule removes by construction. **(3)** Step 11's unbuilt items 11.3–11.7 and their Arm D / Arm F vocabulary. **Steps 0–7 and 9 have no exposure** (grep-verified by the scanners, patterns listed in §14), and **Step 8 as executed has none either**: all 88 archetype IDFs contain exactly one zone, `Z_DWELLING`.

On the way the full read found stale text that has nothing to do with the ruling and is listed in §9 so it stops being re-discovered.

| # | Item | Where | Effort | Decision | Why it matters |
|---|---|---|---|---|---|
| **I-1** | Supersede the core/corridor plan with a dated no-core header | `Step8_docs/IMP_step8/` | S | 🟡 **`D-IMP-1`** | a plan that contradicts the owner's ruling is read as current the moment nobody says otherwise |
| **I-2** | 🔴 `FINDING 195` / `FINDING 196` — stepped Arm D geometry, EUI denominator counts the missing area | `Step10_docs` | S | ⚪ none — additive record | the only measured consequence of the read on a closed step; moves no gate |
| **I-3** | The no-core storey rule does not conserve the census dwelling count | new campaign spec | S | folds into `D-IMP-2` | `H10` is stated in N_u and the two definitions differ by up to ±4 per building |
| **I-4** | 🔴 Pre-register the no-core real-stock campaign as a **new** gate series, never a retrofit of `G10.x` | new `Step12_docs` | M | 🟡 **`D-IMP-2`** | two documents claiming one ID on two bases is how a basis change hides as a fix |
| **I-5** | Household → dwelling binding and storey eligibility for the no-core stock | new spec + Step 7 emission | M | 🟡 **`D-IMP-3`** | thousands of dwellings per district against 100 emitted series per fold |
| **I-6** | Write the manifest fields that were never written, from day one | new spec | S | ⚪ none | `G10.14` / `G10.18` FAIL on 0 of 410 "because a field was never written"; the future campaign is this one |
| **I-7** | Carry the reproducibility arm into the spec | new spec | S | ⚪ none | `FINDING 181` is still the arc's only open item; a campaign without a tolerance basis ends barred at cell level, like the 149 |
| **I-8** | Step 11's Arm vocabulary and item 11.7's input | `Step11_docs` | S | ⚪ none | 11.7 must read the `D-EU-88` viewer, not the pre-no-core `outputs_3D` |
| **I-9** | Housekeeping found by the full read | master plan, IMP doc, Step 7 IMP doc, board | S | ⚪ none | three countries vs four; OPEN headers on closed steps; 510/102 conflation; three stale board cards |

---

## 1. I-1 — Supersede the core/corridor plan (`D-IMP-1`)

### What our documents say

* `Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md:44` — *"`openubem.geometry.layoutGenerator` Dwelling Subdivision (1x1, 2x1, 2x2, 3x2, 4x2) Unconditioned Stair Core (6 % – 12 % GFA)"*.
* `…IMP.md:129` — comparative table row *"Zoning & Compartmentalization … Multi-Dwelling + Unheated Stair"*.
* `…IMP.md:153-181` (§4) — *"Multi-Family (`MFH`): 2×2 grid … surrounding a central unconditioned stairwell core"*, *"Apartment Blocks (`AB`): 3×2 or 4×2 grid … along a central double-loaded circulation corridor spine"*, *"Circulation Core Area: 8 % of gross floor area (12.0–25.0 m²), unconditioned floating temperature zone (12–16 °C winter mean, `b_u` = 0.50–0.80)"*, the diagram labelled `units_corridor`.
* `…IMP.md:196-197` (§5.2) — an independent diary per dwelling unit inside multi-family archetypes.
* `IMP_step8/outputs/floor_layout_generation_report.md:44-51, 290-299, 313-330` — the same design as a decision tree (n = 3–4 → 2×2, 5–6 → 3×2, ≥ 7 → 4×2, "Embed Centroidal Staircase Core"), "Geometric Core Rules", the windowless-unit diagnostic.
* `IMP_step8/DeepResearch/DR01` §C, `DR02:31, :68`, `DR03:30`, `DR04:45` — each recommends *"an unconditioned central staircase core (8 %–10 % of floor area)"* / *"unit-level + unconditioned stair core thermal discretization"* as a Medium-effort design change for Step 8.
* `IMP_step8/outputs/step8_master_results_dossier.md:217` — claims *"First Watertight Multi-Dwelling Procedural UBEM"* for a plan that was never built.

### What the owner ruled (verbatim, `STATE_european_locations_v5.md:170-183`)

* **`D-EU-79`** — *"i have decided with nocore option for all, becasue core is getting complex everything"* / *"no more core options, only nocore options, lets go, it is easier to handle."* A plate divides into **dwellings only**; no circulation zone, no core, no corridor is drawn; no rule, check or sheet names one.
* **`D-EU-80`** — *"no empty space per floor, add these empty spaces inside the closest falt"*. Every square metre belongs to exactly one flat (`C1`, coverage 0.999–1.001).
* **`D-EU-81`** — nothing narrower than 2.00 m (`C10`).
* Also live: `D-EU-69` (≥ 2.50 m of outer façade per flat, `C6`), `D-EU-76` (one flat = one zone, `C4`/`C5`), `D-EU-65` (ceiling 12 flats per floor, above refuses by design), `D-EU-82`–`D-EU-84` (flat proportion `C11`, grid-first, aspect ladder), `D-EU-87` (`C10` to be rebuilt as a pinch test — **not yet implemented**), `D-EU-88` (district viewer, whole neighbourhoods, geometry only).
* Superseded and **parked with its engine intact, owner-restart only**: `D-EU-64`–`D-EU-78` (the one-circulation-zone law, the 1.80 m access band, the corridor-drawing clauses, the per-group schemes). The parked regime's own measurement of what it set aside, by shape group, was **6.3 % to 16.3 %** of the plate (`prompts/DIRECTOR_PROMPT_group_floor_planning_2026-09-01.md:71-146`; a rule-bench number, never a district number).

### Measured today — none of the plan was ever built

* **Step 8 as executed:** 88 of 88 archetype IDFs in `Step8_docs/outputs_step8/archetypes/` contain exactly **one** zone, named `Z_DWELLING`. Ruled `D-S8-2` §6 item 2 (*one thermal zone per dwelling*, `4thJ_08_bemSimulation.md:606-614`) and item 1(a) (*one equivalent box per archetype*, `:747`). The corridor content lives only in the IMP plan and the dossier.
* **Step 10 as executed:** the 410 retained IDFs contain **2,300 zones**: **1,430** named `…_F<n>_dwelling_<i>` and **870** named `…_F<n>_whole`; **zero** zones named core, corridor, stair, unheated or unconditioned (`grep -i` over all 410). Per unique building (41): 143 dwelling zones in the 18 Arm D buildings, 87 whole-floor zones in the 23 Arm F buildings (`IMP/docs/2026-09-03_nocore_void_census.csv`).
* The parked engine `openubem/geometry/european_residential.py` does carry a circulation carve-out (`_centred_circulation_region`, `EuropeanGridLayout.circulation_polygon`, `:250, :275, :319-325`) but it was **not active** in the 2026-08-28 emission: on **58 of 73** Arm D storeys the dwelling floor polygons sum to the census footprint to five decimals (§2 for the other 15).

### The proposal — `D-IMP-1`

* **(a) Recommended.** Add a dated **no-core regime header** to `4thJ_08_bemSimulation_IMP.md` (the same device the OpenUBEM tree used on 2026-09-02), mark §4, §5.2 and the §3 table row **SUPERSEDED by `D-EU-79`**, and add one paragraph under the `DR01`–`DR04` links saying the core recommendation was **considered and retired by the owner's ruling**, with the quotation. Nothing is deleted; the plan stays readable as the record of what was considered. The dossier's *"First Watertight Multi-Dwelling Procedural UBEM"* sentence gets the same marker.
* **(b)** Leave the plan as a parked alternative with no header. Rejected: the IMP doc has no STATUS line and no Progress Log, so a reader cannot tell it was never built.
* **(c)** Delete the corridor sections. Rejected: additive only.

**Manuscript consequence, written whichever way (a) is ruled:** a new limitation beside F2 — *no unconditioned circulation zone is modelled; every square metre of a plate is conditioned dwelling. Published estimates place the circulation share of multi-family plates at roughly 6–12 % of gross floor area (`DR02`, `DR03`, public sources cited there); the parked regime's own census measured 6.3–16.3 % by shape group. The conditioned area is therefore over-stated by that share and no correction is applied.* This is a statement about the **basis**, not a number to be tuned.

**Perturbation that must be seen felling the check:** `grep -n -i "units_corridor\|b_u\|stair core\|circulation" Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md` must return hits **only** inside sections carrying the SUPERSEDED marker and in the header itself. Run today it returns `:44, :129, :153-181, :196` with no marker anywhere — the check is currently failing, which is what makes it a check.

**Cost:** about 40 lines of additive text, no code, no compute.

---

## 2. I-2 — 🔴 `FINDING 195` and `FINDING 196`: the retained Arm D geometry is stepped, and the EUI denominator counts the missing area

Found by writing the void census for I-1 and running it on the **real** artefacts first. The hull-based version of the check read 0.000 on every building and was believed for about a minute; referenced against the census footprint instead, six buildings lit up.

### `FINDING 195` — six Arm D buildings are stepped-back masses, not full stacks

The parked engine distributed `observed_dwellings` over `observed_storeys` **unevenly** (11 dwellings over 4 storeys as 3 + 3 + 3 + 2; 28 over 6 as 5 + 5 + 5 + 5 + 4 + 4; and so on). On every storey that carries fewer dwellings than the storey below, the dwelling polygons are **copies of the lower storey's first k′ columns** and the remaining plate area has **no zone**. The dwelling beneath the missing column gets a `roof` surface with outside boundary condition `outdoors` (verified on `es__BATIMENT0000000240877130_part0`, zone `F2_dwelling_2`). The thermal model is therefore **consistent** — no hole, no massless enclosure — but the building is a stepped mass whose top storeys are physically narrower than the census footprint.

| fold | building | dwellings | storeys | allocation | storeys stepped | plate share with no zone on those storeys |
|---|---|---|---|---|---|---|
| es | `…240877130` | 11 | 4 | 3+3+3+2 | 1 | 31.96 % |
| es | `…240879449` | 28 | 6 | 5+5+5+5+4+4 | 2 | 19.98 % |
| es | `…240881223` | 28 | 8 | 4+4+4+4+3+3+3+3 | 4 | 25.03 % |
| it | `…240880162` | 10 | 3 | 4+3+3 | 2 | 24.16 % |
| uk | `…240879632` | 6 | 4 | 2+2+1+1 | 2 | 50.55 % |
| uk | `…240881152` | 20 | 8 | 3+3+3+3+2+2+2+2 | 4 | 33.24 % |

**15 of 73 Arm D storeys**, 6 of 18 Arm D buildings, **997 m²** of declared floor area with no zone (sum of the missing columns × storeys). The 23 Arm F buildings read ≤ 1e-5 on every storey — a whole-floor zone equals the footprint. `storeys_without_a_dwelling` in the manifests is **0** for all six, because that field counts storeys with *no* dwelling, not storeys with *fewer*.

Source: `tools/4thJ_imp_nocore_void_census.py`, output `IMP/docs/2026-09-03_nocore_void_census.csv`, columns `void_share_vs_footprint_max` / `_mean`; the per-storey breakdown is reproduced by the same parser (§14).

### `FINDING 196` — `floor_area_m2` is `footprint × observed_storeys` in all 41 manifests, so `eui_heating_kwh_m2` is a lower bound on the six

Read from the manifests: `floor_area_m2 / (footprint_area_m2 × observed_storeys)` = 1.0000 on all 41 buildings, and `eui_heating_kwh_m2 × floor_area_m2 / annual_heating_kwh` = 1.0000. On the six stepped buildings the denominator therefore includes 20–51 % of plate area on the stepped storeys that **no zone heats**. Their per-building `eui_heating_kwh_m2` is **under-stated** by exactly the missing share. Nothing else moves: the per-zone gain conservation `G10.13` scores each zone on its own area; `H10` and `CF(N_u)` are within-building peak ratios and do not read the denominator.

### What this does NOT change — stated so it is not re-litigated

* **No gate re-opens.** No `G10.x` scored plate coverage. `G10.7` is INFO permanently (`D-S8-5` item 1) and no stock-level EUI may be quoted from Arm D (`4thJ_10_ubemRealStock.md:432-434`, §11). The board stays 18 / 2 / 1 / 1 / 2.
* **No manifest is retrofitted** (`EU-08` precedent). The two findings are recorded additively in the Step 10 log and travel with any Arm D number as a caveat.
* **The `D-S10-1` option (c) refusal stands.** A local re-run would not repair a geometry the engine no longer produces.
* **Under the no-core storey rule the stepping disappears by construction** — the same `k` on every storey (`RULES…nocore…html`, *"repeated unchanged on every storey"*) — at the price described in I-3.

### Perturbation — seen felling, and seen NOT felling

* **Footprint-referenced check, edge removal:** `dwelling_0` deleted on every storey of `…240879449` → `void_share_vs_footprint` **0.398** (FAIL). **Interior removal:** `dwelling_2` deleted → **0.400** (FAIL).
* **Convex-hull check, edge removal:** **0.000** — the hull shrank with the removed edge column and the check **did not fire**. Interior removal: 0.251 (fires). 🔴 The hull variant is therefore demoted to INFO inside the tool and is never the verdict; the census footprint is the reference. Written down because the first version of the tool used the hull and reported "no void anywhere" — an instrument with a blind spot that happens to point away from the defect.

**Cost:** two dated Progress Log entries (Step 10 main and val docs), one caveat sentence in the Arm D set. No compute, no decision.

---

## 3. I-3 — The no-core storey rule does not conserve the census dwelling count

Under no-core the flats per storey are `k = max(1, round(dwellings_total / storeys))`, computed once per building and repeated on every storey (`PLAN_eu21-district-viewer-2026-09-03.md:73-75`, `load_universe`; `RULES…nocore…html` group sheets). Applied to the 41 retained buildings (`IMP/docs/2026-09-03_nocore_projection_41.csv`):

| quantity | value |
|---|---|
| zones built 2026-08-28 (unique buildings) | 230 |
| observed dwellings (census) | 312 |
| N_u under the no-core rule, `k × storeys` | **332** |
| buildings where `k × storeys ≠ observed dwellings` | **29 of 41** |
| largest deficit / largest surplus per building | −4 / +4 |
| Arm F buildings with `k ≥ 2` (would become dwelling-partitioned) | 9 of 23 |
| Arm D buildings with `k = 1` (one flat per storey, geometry identical to Arm F) | 10 of 18 |
| buildings refused by design, `k > 12` (`D-EU-65`) | 0 |

Under the parked engine, built = observed on all 18 Arm D buildings (exactly, at the cost of `FINDING 195`). Under no-core, **N_u changes meaning**: from the census count to `k × storeys`. `H10` is stated in N_u (*"at fixed f, the occupancy effect on building peak grows with N_u"*, master plan M:1837-1841) and `CF(N_u)` is fitted on it. 🔴 This is arithmetic on the census, never a result — no plate was cut, nothing was run — and it is here because the campaign spec of I-4 has to say **which N_u it means** before the first cell exists.

**Proposal (folds into `D-IMP-2`):** the spec declares `N_u := zones built = k × storeys`, records `observed_dwellings`, `k` and `dwelling_deficit` per building in the manifest, and reports the deficit **as a distribution, never gated** — no tolerance is pre-registered, the same discipline `G10.10` applies to its area-share residue.

**Perturbation:** not applicable — the projection is one line of integer arithmetic and its only check is the CSV identity `n_u_nocore == k_nocore × observed_storeys`, which is trivially true. Said plainly rather than dressed up.

---

## 4. I-4 — 🔴 Pre-register the no-core real-stock campaign as a **new** gate series (`D-IMP-2`)

### Why a new series and not a second Step 10 campaign

The Overview registered Steps 10 and 11 as new steps *"rather than as edits to Steps 8 and 9 … because two documents claiming one ID on two bases is how a basis change hides as a fix"* (`4thJ_00_HETUS_LLM_Pipeline_Overview.md:683`). The no-core campaign changes the **population basis** of every geometry-dependent Step 10 gate:

* the refusal taxonomy (`NON_CONVEX_FOOTPRINT`, `NARROW_FOOTPRINT_LT_8M`, courtyard) **no longer exists** — *"No refusal path. … every plate with a usable footprint is cut"* (`RULES…nocore…html`, every group sheet);
* the 18-of-297 yield, the 256-of-297 non-convex count and the 1-of-12 ladder result (`4thJ_10_ubemRealStock.md:30-34, 416-419`; master plan M:1873-1889) are properties of the parked generator, presumptively stale;
* "the census decides the arm, never the probe" (`impl/2026-08-28_realstock-campaign-two-platform.md:121-146`) was written against `REFUSED / FALLBACK / EMITTED`; the new status vocabulary is `nocore_equal_area / direct` plus the check verdict (`07_nocore_tests.py:868`);
* Arm F **survives but is redefined**: *"A building without a real plan is not skipped — it is simulated as a single empty box per floor, one thermal zone, no interior walls"* (`RULES…nocore…html`, COVERAGE section), so Arm F = plates that FAIL a check or have no usable footprint, no longer a convexity refusal. `G10.22`'s LOWER BOUND wording survives unchanged;
* `G10.19`'s floor (≥ 30 buildings per fold with N_u ≥ 2) becomes **reachable**: Madrid alone has 669 of 961 census rows with `k ≥ 2` (`PLAN_eu21-district-viewer-2026-09-03.md`, `load_universe` distribution — census arithmetic, not a result). The `NOT_EVALUABLE_FAIL_BY_POPULATION` on `G10.19` was a property of the old yield, not of the stock;
* the four districts are the population (2,544 buildings; Madrid, Lyon, London, Bologna), with `G10.11`'s rule intact: France is a physical baseline and **never** enters a 4J denominator.

### What waits on the OpenUBEM side, and must be seen holding before any cell is built

| blocker | state today (`STATE_european_locations_v5.md`, `CHECKLIST_v5.md`) |
|---|---|
| engine carry-in of the no-core rule into `european_residential.py` | *"identified, not ordered"* — the engine is still core-era; only the rule-bench `scripts/eu21/07_nocore_tests.py` implements no-core |
| `D-EU-84` aspect ladder | no rung of {2.5, 3.0, 3.5, 4.0} has reached FAIL 0 on the 550 plates (`FINDING 238`, `FINDING 240`) |
| `D-EU-87` / `FINDING 241` — `C10` rebuilt as a real pinch test | ruled, **not implemented** (T05c not started); 182 of 550 plates hold sub-2 m regions the current `widest_fit` certifies |
| `FINDING 221` — 939 buildings lose a sound plan at IDF-writing time | a separate defect, not a morphology failure; unfixed |
| `D-EU-55` | 🔴 no EnergyPlus run without the owner's own sentence |
| `D-EU-88` district viewer | in flight, not started |

So: **spec now, compute never before those**. The 4J side can write the specification, the gate table, the binding rule and the manifest schema today; it cannot cut a plate or run a cell.

### The decision — `D-IMP-2`

* **(a) Recommended.** Register **Step 12 — no-core real stock**, `Step12_docs/4thJ_12_nocoreRealStock.md` + `_val.md`, gate series **`G12.x`**, its own `prereg` frozen before the first cell. Inherits per gate from `G10.x` with the inheritance stated on each row (the Step 10/11 convention). Carries I-3, I-5, I-6, I-7 as its first work items. Its preflight refuses to build a cell while the engine is core-era (below).
* **(b)** Amend Step 10 in place as "campaign 2". Rejected: a basis change hiding as a fix; the closed board would carry two populations under one ID.
* **(c)** Write nothing until OpenUBEM finishes. Rejected: the spec is the only thing the 4J side can do now, and it is what makes the manifest fields (I-6) and the tolerance (I-7) exist from day one instead of "in a future campaign".

**Perturbation that must be seen felling the preflight:** the Step 12 driver asserts the cutter identity from the manifest (`scheme == "nocore_equal_area"`, `status == "direct"`, the check verdict present) and the engine module digest against a pinned no-core digest. Run against today's tree it **must FAIL** — the engine is core-era — and that failure is the evidence the guard is wired in. `V10.i` applies: the written reason for a blocker is re-measured before it is designed around.

**Cost:** M — two documents and a gate table, no code beyond the preflight, no compute.

---

## 5. I-5 — Household → dwelling binding and storey eligibility for the no-core stock (`D-IMP-3`)

### The facts the binding sits on

* Step 5's population is a **person table with no household identifier** (`FINDING 93`; `4thJ_07_constrainedGeneration.md:267-273`); Step 7 borrows **real-corpus** households for the chaining experiment (`D-S7-6`(a)), and 3–13.5 % of those are multi-person homes represented by one diarist (`FINDING 98`).
* Step 7 emits **100 `Schedule:File` + `People` pairs per fold**, 8,760 hourly values, rotated to midnight (`4thJ_07_constrainedGeneration_val.md:187-193`; `G7.13`–`G7.17`, `G7.19`). Generated diaries exist in the 10⁵ range per fold (`G7.7` sizing: `es` 75,531 / `uk` 16,795 / `it` 48,809 draws), so the bottleneck is emission, not generation. The emitter is built, CPU-only, selftest 61/61.
* Step 10 bound **N_u independent series per building** by rank order in Case B and one replicated series in Case A (`4thJ_10_ubemRealStock.md:484-495`, work item 10.9); the OpenUBEM archetype campaign binds **one series per cell** (A1, `eu_cell_presence_binding_v2.json`). No document on either side connects the archetype binding to the real-footprint cuts (`extract_openubem_eu.md` §F, §H) — a genuine gap, stated by both trees.
* **Storey eligibility:** 6 of 41 retained buildings carry a storey with **no** dwelling (`storeys_without_a_dwelling` > 0, manifests). Under `D-EU-80` every storey the cutter draws is flats, and the census carries no per-storey use field.
* Scale: at `k × storeys` per building over ~1,000–2,500 buildings per district the dwelling count per district is in the **thousands**; against 100 emitted series per fold, every series would be re-used tens of times.

### The decision — `D-IMP-3`

* **(a) Recommended.** Every drawn flat receives its **own independent series** (Case B semantics), drawn by rank order from a per-fold emission **sized to the district's dwelling count** (emission is CPU, no GPU); **all drawn storeys are eligible**, and non-residential ground floors are declared as a limitation (the census cannot tell them apart). Case A stays the paired control. `G10.8`'s content-located fold check and `G10.20`'s Case A/B distinctness carry over as `G12` rows.
* **(b)** Residential storeys only, where the census gives a per-storey use. Moot: no such field exists in `morphology_census.csv` or the manifests; recorded so it is not re-proposed without a source.
* **(c)** Re-use the existing 100 series with replacement. Rejected: it manufactures coincidence between dwellings, which is exactly the effect `H10` measures.

**Perturbation that must be seen felling it:** two dwellings of one building sharing a series in Case B must FAIL the binding gate (a `sha256` collision check per building); a series bound to a dwelling of the wrong fold must FAIL the fold check (the `G10.8` mutation, already seen firing on the 410).

**Cost:** M — emission sizing per district (measured, not projected), one binding artefact per district, no GPU.

---

## 6. I-6 — Write the fields that were never written, from day one

`G10.14` FAILS on 0 of 410 because `weather_sha256`, `energyplus_build_hash`, `openubem_version`, `openubem_git_commit` and a **measured** `platform` were never written; `G10.18`'s declaration arm FAILS because `rotated_to_midnight` / `diary_origin_hour` were never written; `FINDING 187`: `energyplus_version` is a hard-coded literal. All three are *"repaired only in a future campaign"* (`4thJ_10_ubemRealStock_val.md:403-404`). **The Step 12 campaign is that future campaign.** Its manifest schema lists every one of them as required, plus `completed: bool` and `completion_status` (granted by OpenUBEM in the InternalMass letter), `scheme`, `status`, `k`, `observed_dwellings`, `dwelling_deficit` (I-3), and the check verdict vector `C1 C3 C4 C5 C6 C10 C11`.

**Perturbation:** the `G12` twin of `G10.14` must be seen failing on a manifest with one required field blanked — the inverse of the mutation that flipped `G10.14` FAIL → PASS on the 410. **Cost:** S.

---

## 7. I-7 — Carry the reproducibility arm into the spec

`FINDING 181` (a cell can finish `completed: true` and be numerically meaningless; a diverging heat balance is only a Warning) is still the arc's only open item. Its consequences are the shape of what the 4J side may quote: the 149 barred at cell level, `G8.1`–`G8.4` NOT SCOREABLE, the platform arm on the 410 quotable only as *"numerically stable across the two hosts, NOT bitwise reproducible, over 410 paired cells"*, `G10.1`–`G10.4` on 40 paired cells by ruling. A campaign that starts without a tolerance basis ends with its cell-level numbers barred after the fact.

**Proposal:** the Step 12 spec pre-registers a **replicate arm** — a named subset of cells re-run R times on one host — and the re-run tolerance is the quotation rule for every cell-level number (inside tolerance → quotable with the tolerance; outside → barred, named). It also pre-registers the `.err` marker census (`PsyPsatFnTemp` / `PsyTwbFnTdbWPb`, `FINDING 182` / `FINDING 193`) as an INFO column from the first cell. **No compute now**; the arm is written into the spec so it is run *with* the campaign, not after it.

**Perturbation:** a replicate set with one cell diverging beyond tolerance must be seen failing the quotation rule. **Cost:** S.

---

## 8. I-8 — Step 11's Arm vocabulary and item 11.7's input

Step 11 (11.3–11.7 unbuilt) inherits Arm D / Arm F, the `one_zone_per_floor` fallback and the LOWER BOUND labelling wholesale (`4thJ_11_stockEndUseLoads.md:222-243`; `G11.17`), and item 11.7 reads *"the existing OpenUBEM 3D export `…/outputs_3D`"* (`:273`) — a pre-no-core geometry. None of Step 11's four documents anticipates the ruling (no hit for core, corridor, no-core, unconditioned, lift).

**Proposal (no decision):** one dated amendment note in Step 11 §2.1 — *Arm F = check-FAIL or unusable footprint, simulated as one box per floor; no longer a convexity refusal; `G11.17` unchanged* — and one on item 11.7 re-pointing its input to the `D-EU-88` district-viewer output (no-core cuts, verdict-coloured, geometry only, *"not one EUI, kWh or run id on the page"*) once it exists. `G11.13` (no per-dwelling value at any zoom) is compatible with per-dwelling zones and stays. Nothing is built until Step 12 exists. **Cost:** S.

---

## 9. I-9 — Housekeeping found by the full read (no decision needed)

* **Master plan, three countries vs four.** `4thJ_00_HETUS_LLM_Pipeline.md:649` (Step 1 header) and `:2069` (KEY DESIGN DECISIONS) still read *"four countries"*; decision 16 (`:2913`, 2026-08-15) made it three. The doc's own rule (`:2278-2279`) says edit the entry rather than append a contradiction.
* **Master plan, stale status lines.** Step 2 `:849` OPEN (closed 2026-08-14/18), Step 7 `:1557` OPEN (decision 14 closed 2026-08-25), Step 8 `:1644` OPEN (closed 2026-08-25, re-run 2026-08-26), Step 9 `:1704` OPEN (scored 2026-08-25/27), Step 10 `:1814` PLANNED (validated and closed 2026-08-28). Step 10D `:1873-1889` — the 18/297, 256/297 and 1/12 figures must carry *"measured under the parked layout regime"*.
* **Overview box**, same status lines (`Overview.md:307-484`) — the box is a 2026-08-14 snapshot and says so; one dated line above it suffices.
* **Two campaigns called "510".** `IMP_step8/4thJ_08_bemSimulation_IMP.md:27` and `outputs/step8_master_results_dossier.md:137` say *"510-cell … 102 archetypes"*. That is the **OpenUBEM archetype campaign** (`EU-08`, 102 archetypes × 5 f). The **4J Step 8** campaign is **88 archetypes × 5 f × 10 diaries** (`4thJ_08_bemSimulation.md:796-799`: *"The 510 figure … is superseded"*). Both exist; the IMP doc must say which it means.
* **Step 7 schedules IMP doc** `4thJ_07_schedules_and_chaining_IMP.md:706-708` still says `G7.18` is *"blocked behind an IDF that does not exist and five open §6 geometry/zoning decisions"* — stale since `D-S8-2` was ruled (2026-08-21/24) and the 9,000-run sweep ran (2026-08-25). One dated note.
* 🔴 **`FINDING 197` — the board had two lineages, and the local file was the stale one. MERGED 2026-09-03.** The live artefact (`9e07da64…`, published 2026-08-28 night) carried **128 cards** with dated, richer cards for Steps 1–9 and 11 and the `EU-08`–`EU-10` closure, but **not** the Step 10 campaign closure; the local `4thJ_CHECKLIST.html` (2026-08-28 15:38, 105 cards) carried the campaign-closure cards (10.3, 10.5–10.8, 10.10, 10.11, `G10.14`, `G10.18`, `FINDING 194`, `G10.1`–`G10.4`, `FINDING 181` platform arm, `FINDING 193`, the census card) on top of the **2026-08-24 snapshot** of Steps 0–9 — its own stamp at line 225 said so (*"THIS FILE IS A DATED SNAPSHOT, NOT THE CURRENT BOARD"*). Neither was a superset, and the last+29/last+31 log entries that say "board republished" describe a publish that never reached the live address. Merged today on the **live** base (scratchpad `merge_board.py`): the campaign cards ported, `EU-08`'s "asked, no reply" card and `D-S6-16` flipped on their own later evidence, the Step 10 note taken from the local lineage, 11.7 and the Step 11 standing bars added, the no-core card added — **139 cards, 130 done / 1 in progress / 8 not started**, `node --check` and the DOM-shim smoke green, republished at the same URL, and **the local file now equals the page**. The three "stale cards" this item first listed were stale only in the local lineage; on the live page `EU-09` and `EU-10` were already done. What remains stale on the merged board: `10.11 Rotation-origin fix (upstream)` still `todo` although `FINDING 194` showed the defect does not reproduce — flip in the execution session. 🔴 **Rule that travels:** never edit the local board file without first reading the live artefact; the artefact is the master.
* **Carried, not new:** the paper owes one row in the asymmetry table for `FINDING 98` (`4thJ_07_constrainedGeneration.md:701-705`); Fuentes et al. (2018) is bibliographically verified and substantively unread (`4thJ_11_stockEndUseLoads.md:441-444`) — a person's item; `V3.d` / `V3.h` stay NOT CHECKED by design.

---

## 10. What does NOT change

* **`H10` and the `CF(N_u)` formalism** (`CF = P_peak,bldg / Σ P_peak,zone`, the `g_inf + (1−g_inf)/√N` shape) — geometry-agnostic; only the population it is measured over changes (I-3, I-4).
* **The injection formula** `φ_int(t) = (1−f)·3.0 + f·3.0·g(t)/mean(g)`, the `f` set {0, .15, .30, .50, 1.00}, the per-zone **and** per-building conservation asserted on disk (`G10.13`), the chaining convention `independent`, seed 1 (decision 14), and `rotate_to_midnight()` (`D-S9-3`(a)). Any new emission path inherits them verbatim.
* **Step 7's interface**: presence **fraction** `g(t)`, never watts (`D-S7-7`(a)); one `Schedule:File` + `People` pair per dwelling; `Interpolate to Timestep = No`.
* **Every closed board**: Steps 1–9, Step 10's 24 gates, the `EU-09` restated board, `prereg.md` and its md5, `D-EU-31` Option A, the never-quote list in `Prompts/RESUME.md` §4. `G10.1`–`G10.4` stay on 40 paired cells (`es` 30 / `it` 10 / `uk` 0) and that naming travels with every number.
* **The Step 8 archetype results** — single-zone boxes, no corridor anywhere, nothing to supersede.
* **Context geometry** — `D-EU-40` / `D-EU-41` (20 m context, adiabatic party walls) is a separate rule and *"does not change the dwelling-layout scheme"*; it is not part of this document.
* **The refusals on record**: option (c) of `D-S10-1`; Option B of `D-EU-31`; any re-run of the 149; any retrofit of a manifest.

---

## 11. 🟡 Decisions for the author

One line each; the options and consequences are in the sections named.

| # | Question | Recommendation | Section |
|---|---|---|---|
| **`D-IMP-1`** | Mark the `IMP_step8` core/corridor plan SUPERSEDED by `D-EU-79` with a dated header, and write the "no circulation zone" limitation | **(a)** | §1 |
| **`D-IMP-2`** | Register the no-core real-stock campaign as **Step 12 / `G12.x`** with its own prereg, spec now, compute only after the OpenUBEM blockers clear | **(a)** | §4 |
| **`D-IMP-3`** | One independent series per drawn flat, emission sized per district, all drawn storeys eligible | **(a)** | §5 |

🔴 Whichever way they are ruled, nothing here moves a registered basis, re-scores a closed gate, re-runs a cell, or edits a promoted artefact.

---

## 12. Order of work — after the rulings, in this order

Tick a box only when the item is applied **and** its perturbation has been seen felling the check it guards.

- [x] 🟢 **1. I-2** — **DONE 2026-09-03 (same day):** `FINDING 195` / `FINDING 196` appended to `Step10_docs/4thJ_10_ubemRealStock.md` and `_val.md` (additive), the review entry appended to the master plan's Progress Log, the lead block of `Prompts/RESUME.md` rewritten (last+33, backup `RESUME.md.bak_next33`), one card added to the board. Perturbation seen: footprint check fell on edge (0.398) and interior (0.400) removals; hull check seen NOT felling on edge (0.000) and demoted. The caveat sentence in the Arm D set waits for the execution session.
- [ ] **2. I-1** — on `D-IMP-1`(a): dated no-core header on `4thJ_08_bemSimulation_IMP.md`, SUPERSEDED markers on §3 row / §4 / §5.2, the `DR01`–`DR04` paragraph, the dossier sentence; the limitation paragraph into `writing/4thJ_writeup_notes.md`. Check: the grep of §1 returns hits only inside marked sections.
- [ ] **3. I-9** — master plan banner and status-line edits; the 510/102 relabel; the Step 7 IMP note; the three board cards (`node --check` + DOM-shim smoke + republish at the existing URL, backup first).
- [ ] **4. I-4** — on `D-IMP-2`(a): create `Step12_docs/` (implementation + validation), gate table `G12.x` with inheritance per row, `prereg` draft, the preflight guard **seen failing on today's core-era engine**.
- [ ] **5. I-3, I-6, I-7** — into the Step 12 spec: `N_u := k × storeys` with the deficit distribution reported never gated; the required manifest fields with the blank-field mutation seen felling the `G12` twin of `G10.14`; the replicate arm and its quotation rule with one diverging cell seen felling it.
- [ ] **6. I-5** — on `D-IMP-3`(a): binding rule and emission sizing per district (CPU), the collision and wrong-fold mutations seen felling the binding gate.
- [ ] **7. I-8** — dated amendment notes in Step 11 §2.1 and item 11.7.
- [ ] **8.** Close this document; Step 12 waits on the OpenUBEM blockers of §4 and on `D-EU-55`. Step 10 and Step 11 do not re-open.

---

## 13. Ledger

| Date | Action | Result |
|---|---|---|
| 2026-09-03 | Read the no-core rules (HTML + two companions), `STATE_v5`, `PLAN nocore`, `PLAN district-viewer`, the 12 cross-tree letters | `D-EU-79`–`D-EU-88` transcribed; engine carry-in not ordered; `D-EU-84`/`D-EU-87` open |
| 2026-09-03 | Ten read-only scanners over Steps 0–11, the master plan, the OpenUBEM arc (extracts in the session scratchpad) | Steps 0–7, 9: no geometry exposure; exposure confined to `IMP_step8`, Step 10 population, Step 11 vocabulary |
| 2026-09-03 | Zone census over the 410 retained IDFs | 2,300 zones = 1,430 `dwelling_N` + 870 `whole`; 0 core/corridor/stair/unconditioned |
| 2026-09-03 | Zone census over the 88 Step 8 archetype IDFs | 88 × `Z_DWELLING`, one zone each |
| 2026-09-03 | Wrote `tools/4thJ_imp_nocore_void_census.py`; ran it on the 41 buildings; two perturbations | `FINDING 195` (6 buildings, 15 storeys stepped), `FINDING 196` (denominator); hull variant seen NOT felling on edge removal, demoted |
| 2026-09-03 | No-core projection on the 41 manifests | N_u 332 vs 312 observed vs 230 built; 29/41 differ, ±4 |
| 2026-09-03 | Verified the roof exposure under a missing top-storey dwelling (`F2_dwelling_2`, roof → outdoors) | thermally consistent stepped mass, not a hole |
| 2026-09-03 | §12 box 1: log entries appended (Step 10 main + val, master plan), `Prompts/RESUME.md` lead block last+33, memory updated | this document filed; `D-IMP-1/2/3` waiting on the author |
| 2026-09-03 | Read the live board artefact in full before republishing; diffed it against the local file per step | `FINDING 197`: two lineages, neither a superset (live 128 cards / local 105) |
| 2026-09-03 | Merged on the live base, ported the campaign cards, added the no-core card; `node --check` OK, smoke 12 steps / 139 cards / 130 done / 1 prog / 8 todo; republished at the same URL; local file replaced (backup `.bak_nocore`) | the board and the file agree again |

## 14. Verified — read from the artefacts, not from the logs

* **410 IDFs, 2,300 zones** — `grep -c -i "^ *ZONE,"` per file, distribution {1:20, 2:80, 3:100, 4:80, 5:10, 6:30, 7:20, 8:20, 10:10, 11:10, 20:10, 28:20} = 2,300; name suffixes 1,430 `dwelling_N`, 870 `whole`; `grep -l -i "corridor\|stair\|unheated\|uncondition"` → 0 files (sample of one IDF for the full string set → 0).
* **88 archetype IDFs, one zone each, `Z_DWELLING`** — `Step8_docs/outputs_step8/archetypes/*.idf`.
* **41 unique buildings, 18 Arm D / 23 Arm F** — `realstock_campaign_manifest.csv` (411 lines) and the 410 manifests; `case A` `n_u` = 1, `case B` `n_u` = zone count (e.g. `…240879449`: 28/28).
* **Void census** — `IMP/docs/2026-09-03_nocore_void_census.csv`: dwelling arm `void_share_vs_footprint_max` = 0.50549 max, 0.00000 median; whole arm ≤ 1e-5. Per-storey sums re-derived with the tool's own parser for the six buildings (table in §2).
* **Denominator** — `floor_area_m2 / (footprint_area_m2 × observed_storeys)` = 1.0000 and `eui × floor_area / annual` = 1.0000 on the six affected buildings and one control.
* **Projection** — `IMP/docs/2026-09-03_nocore_projection_41.csv`, totals as in §3.
* **Perturbations** — copies of `es__BATIMENT0000000240879449_part0__caseA__f000.idf` with the `floor` surface of `dwelling_0` (edge) or `dwelling_2` (interior) removed on every storey (6 floors each): footprint check 0.398 / 0.400, hull check 0.000 / 0.251.
* **The parked engine's carve-out exists in code and was not active** — `openubem/geometry/european_residential.py:250, :275, :319-325, :343-348` (`_centred_circulation_region`, `circulation_polygon`, `wants_circulation`), read from source; not active because 58 of 73 Arm D storeys sum to the footprint.
* **Scanner grep patterns for "no exposure"** (Steps 0–7, 9, case-insensitive): `corridor|circulation|\bstair|\bcore\b|b_u\b|layoutGenerator|units_corridor|2x2|3x2|4x2|footprint|thermal zone|zone count|unconditioned|Arm D|Arm F|OpenUBEM|adiabatic|context shading` — the only hits were English "tabulate/tabular" and "score".

## 15. WHAT I DID NOT VERIFY

* **I did not open the OpenUBEM engine's 2026-08-28 revision.** `european_residential.py` on disk is dated 2026-09-01 20:27; the code that emitted the 410 is inferred from the artefacts (58 of 73 storeys full, stepped upper storeys), not from a pinned commit.
* **I did not read `previous/MVP_european_locations.md`** (328 KB); the phrase *"MVP §12.11's receiving step is still stale"* in `IMP_step8/…IMP.md:334` was not located anywhere else and is carried as written.
* **I did not measure the circulation share on any real plate.** The 6–12 % (`DR02`/`DR03`) is literature; the 6.3–16.3 % is the parked regime's own rule-bench figure. Neither is a district number.
* **I did not size the per-district emission of I-5.** "Thousands of dwellings per district" is `k × storeys` arithmetic on the Madrid `k` distribution, not a count of drawn flats.
* **I did not check the London credential block** (GOV.UK One Login token, an OpenUBEM-side action) or whether any district can be cut end-to-end today; `FINDING 221`'s 939 demotions at IDF-writing time are OpenUBEM's number, quoted not re-derived.
* **I did not re-derive any EU figure**, quote any EUI, or touch the 149. Every barred number in `Prompts/RESUME.md` §4 was checked against this document by search before it was saved.
* **The extracts the scanners wrote live in the session scratchpad**, not in the tree; every claim taken from them that mattered was re-read at the cited `path:line` or re-measured, and the ones that were not are marked "quoted" above.
