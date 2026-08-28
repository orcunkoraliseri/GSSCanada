# EU-09 and EU-10 scored over the D-EU-28 ruled perimeter (149) — implementation state

Task doc:   cross-session ruling from `openubem-92`, 2026-08-28 (`D-EU-28` RULED, Option B; proceed with EU-09/EU-10)
Status:     EU-09 DONE · EU-10 DONE · two genuine gate FAILs carried, not cured
Predecessor: `Step10_docs/impl/2026-08-28_EU-08-accounting-over-the-certified-191.md`

## Ledger

No cluster job. Speed queue EMPTY. **No simulation of any kind.** The single agreed re-run budget
remains spent; every mutation in the EU-09 coverage cross-tab is applied to a *copy* of a retained
artefact in a scratch directory and re-scored by the scorer, never re-run through EnergyPlus.
Nothing under `openubem/` was written; all reads there are read-only.

| Artefact | Path |
|---|---|
| EU-09 scorer | `4J_docs_occ/tools/4thJ_step10_eu09_scorer.py` |
| EU-09 gate report | `4J_docs_occ/Step10_docs/outputs_step10/eu09_gate_report_2026-08-28.json` |
| EU-10 dossier builder | `4J_docs_occ/tools/4thJ_step10_eu10_dossier.py` |
| EU-10 dossier | `4J_docs_occ/Step10_docs/outputs_step10/eu10_campaign_dossier_2026-08-28.json` (schema `eu10-dossier-campaign/1.0-deu28`) |

Bands and gate contracts are **imported** from `openubem.validation.step8_bands` and
`openubem.validation.step8_gates` (V8.c); no threshold is restated in our tree. The frozen
`PERTURBATION_MATRIX` is imported too, so a smaller or more convenient mutation set cannot be
substituted.

## Verified

### 1. The perimeter re-derives to the ruled 149

From `deu27_rerun_cells.csv` alone, in the same run as the scoring (V8.b):

```
table rows 1,530 · cells 510 · certified 191 · certified AND marker-free 149
by fold: uk 75 · it 74 · es 0
five-f archetype x fold pairs inside the perimeter: 15   (uk 8 · it 7)
```

Both the 149 and the 15 match the ruling exactly. `es` contributes nothing.

### 2. EU-09 — gate report over the 149

| Verdict | Gates |
|---|---|
| **PASS (11)** | G8.1, G8.2, G8.3, G8.4, G8.5, G8.6, G8.8, G8.12, G8.13, G8.14, G8.16 |
| **FAIL (2)** | **G8.0**, **G8.15** |
| **VACUOUS (4)** | G8.7, G8.9, G8.10, G8.11 — each naming its empty population |

- `G8.1`–`G8.4`: **298 replicate pairs** (149 cells × rep1-vs-rep2 and rep1-vs-rep3), all inside band.
  *G8.1–G8.4 are reproducibility gates. They compare a cell against a re-run of itself. They are not a
  validation of simulated energy against measured energy, and no such validation is claimed anywhere in
  this paper.*
- `G8.5`/`G8.6`: same 298 pairs, magnitude and timing; the comparison series is **the same cell's
  re-run**, never a measured series, and the dossier says so in the gate summary.
- `G8.8`: 37/37 archetype × fold groups carry distinct emitted-schedule digests across `f`
  (2 single-level groups excluded as having no population).
- `G8.12`/`G8.13`: 149/149 saved IDFs — the `Schedule:File` path and the **measured** file digest match
  the manifest, the consuming `OtherEquipment` object names that schedule, and `Interpolate to
  Timestep = No`. Read by OpenUBEM's independent text parser from the saved IDF on disk, never from an
  in-memory builder object.
- `G8.14`: 149/149 self-identifying and populated on `cell_id`, `created_utc`, `idf_sha256`,
  `openubem_git_commit`, `energyplus_version`. ⚪ The retained manifests carry **no `platform` field**, so
  the platform arm of G8.14 is not scoreable and is reported as a coverage gap rather than a pass.
- `G8.16`: 149/149, and `V8.g` is satisfied, so the gate is scored rather than forced to FAIL.

🔴 **`G8.0` FAILs — 99/121.** Of the 121 `f > 0` cells in the perimeter, **22 have an `f = 0` control
that did not complete in all three replicates** (12 of them completed in replicate 1 and failed later).
Separately and more consequentially, **29 of the 121 have an `f = 0` control that is not itself inside
the ruled perimeter**, so *no f-versus-baseline difference may be quoted for those 29 cells*. This is a
real gate failure at the strictness the perimeter is defined at, and it is carried, not cured.

🔴 **`G8.15` FAILs — 149/149 cells carry at least one untriaged warning kind, 8 distinct kinds**
(`calculatezonevolume`, `entered zone volumes differ from calculated zone volume(s).`, `fixviewfactors`,
`getsurfacedata`, `getvertices`, `managesizing`, `processscheduleinput`, `calculated design cooling load
for zone`). No `approved_warning_kinds` list has ever been ruled, so triage ran against an empty
approval set — exactly the standing MVP caveat C-08. Severe and fatal are 0 by the perimeter definition.
Triage is by **kind**, never by frequency (V8.f).

⚪ **The four VACUOUS gates each name their population.** `G8.9`: each replicate executed into its own
fresh run root, no cache was consulted, and no `dependency_digest` field exists in the retained
manifests. `G8.10`/`G8.11`: **0 `Output:Meter` objects across all 149 perimeter IDFs** — heating comes
from the Zone Ideal Loads hourly variable. `G8.7`: no as-modelled published EUI band has been ruled for
these TABULA archetypes, so there is nothing to grade against.

### 3. EU-09 — Table 17 coverage, every gate seen falling on real artefacts

**9 of 12 exercised, all 9 PASS; 3 VACUOUS.**

| Row | Result |
|---|---|
| P01 same schedule file across `f` | PASS — G8.8 falls; its clean arm (G8.10) has no population |
| P02 stale cache | **VACUOUS** — no cache layer, no `dependency_digest` retained |
| P03 obsolete `Gas:Facility` meter | **VACUOUS** — no meters exist |
| P04 zero one end-use meter | **VACUOUS** — no meters exist |
| P05 `OtherEquipment` re-pointed at another schedule | PASS — assignment arm falls, value arm stays clean |
| P06 `Interpolate to Timestep = Yes` | PASS — G8.13 falls, G8.12 clean |
| P07 another cell's manifest copied wholesale | PASS — G8.14 falls, G8.12 clean |
| P08 wrong held-out fold | PASS — G8.16 falls, G8.12/G8.14 clean |
| P09 profile shifted 2 h | PASS — G8.6 falls, G8.5 clean |
| P10 annual energy × 1.2 | PASS — G8.1 and G8.3 fall, G8.6 clean |
| P11 borrowed geometry | PASS — via **V8.d** (see below) |
| P12 null perturbation | PASS — every baseline checkpoint stays clean |

⚪ P11 is reported honestly: `G8.7` itself is vacuous, so the row's target was exercised on the geometry
identity arm instead — borrowed geometry FAILs the V8.d audit while the archetype's own geometry passes.

Vacuity guards `V8.a`–`V8.g` all pass; each carries its own measured detail in the JSON.

### 4. 🔴 FINDING 183 — OpenUBEM's saved-IDF geometry reader is too tight for its own serializer

`read_saved_idf_geometry` requires `V / (A · h)` to be integral to `abs_tol=1e-9`, but
`Zone.Ceiling_Height` is serialized to **7 significant figures**. Two of the 39 perimeter archetypes
(`GB.ENG.AB.03.Gen.ReEx.001.001` → 10.999998, `IT.MidClim.AB.05.Gen.ReEx.001.001` → 7.999999) therefore
raise instead of reading. **A reader tolerance defect, not a geometry defect.** Our scorer falls back to
the same positional parse with a relative tolerance and **flags every cell it did so for**; it does not
loosen anyone's gate and does not silently skip the archetype. Routed to OpenUBEM as a defect note, not
as a decision.

### 5. EU-10 — dossier over the same 149

`eu10_campaign_dossier_2026-08-28.json`, schema `eu10-dossier-campaign/1.0-deu28`. Per cell: annual,
12 monthly, hourly peak and its hour index, denominator area and storey count read per archetype from
that archetype's own saved IDF, heating EUI, weather id and calendar year, and the geometry-readback
mode. **The hourly series re-sums to the manifest's `heating_kwh` on 149 of 149 cells.**

- **EUI accounting mode: `single_simulated_end_use_no_reconstruction`.** Neither §9.10 mode applies —
  no service-load object is emitted and no reconstruction table is applied, so nothing can be double
  counted. Every EUI here is a **heating-only** EUI and must never be compared to a whole-building EUI
  or to a measured total.
- **Quotation bars are inside the dossier**, not left to the reader: `es` not quotable at any level;
  `uk` never at fold level or as nationally representative (D-EU-26); **`it` is the only fold that
  survives both bars at fold level**; any cross-fold absolute comparison names the meteorological year
  (uk 2014, it 2014) in the same sentence as the country.
- Fold-level figure, `it` only: **area-pooled heating EUI 108.25 kWh/m²**, cell range 45.08–156.70.
  The `uk` aggregate is deliberately withheld; its per-archetype records are in `cells[]`.

### 6. 🔴 FINDING 184 — the occupant manipulation is a NULL on annual heating and lives in the peak

Over the 15 five-`f` pairs, `f = 1.00` versus `f = 0.00`:

```
annual heating       it  min -0.38 %  median -0.10 %  max +0.45 %   (n = 7)
                     uk  min -0.21 %  median -0.04 %  max +0.10 %   (n = 8)
hourly peak          it  min -2.83 %  median -1.46 %  max +7.92 %
                     uk  min -0.74 %  median +1.91 %  max +6.32 %
peak-hour shift      it  0, -15, -41, -41, 0, 0, 0 hours
                     uk  +2, +20, -3, -27, 0, 0, +4, +1 hours
```

The annual effect is **under half a percent**, against a published European expectation of 15–50 % on
annual space heating. The reason is in the injection formula itself: `phi_int(t) = 3.0 · ((1-f) + f ·
g_norm(t))` with `g_norm = g / mean(g)`, so **the annual mean gain is conserved by construction and only
the shape changes**. The manipulation cannot move an annual total; what it moves is the peak magnitude
(up to ~8 %) and the peak timing (up to 41 hours). Any claim about this campaign must be a
**peak/timing** claim, not an annual-demand claim, and the published 15–50 % band is not the comparison
this design supports.

⚪ This is a statement about the *design*, and it is not a new decision. It is recorded here and routed
to OpenUBEM for their record.

## Decisions

- None taken. `D-EU-28` was ruled by the OpenUBEM owner (Option B) and is implemented exactly as ruled.
- Two gate FAILs (`G8.0`, `G8.15`) are **carried into the caveat list**, not cured, not re-scored, and no
  band was moved to make either green.
- No re-run requested; the spent budget is not re-opened.

## Next

The exact next action, for a cold agent: nothing is owed on EU-08/EU-09/EU-10. If OpenUBEM rules an
`approved_warning_kinds` list, re-score `G8.15` only — `python tools/4thJ_step10_eu09_scorer.py --out
<path>` — and re-run the dossier against the new gate report. Do not touch the perimeter.

## WHAT I DID NOT VERIFY

- The `.err` files were parsed for **warning kinds**; the physical meaning of the 8 kinds was not
  adjudicated, because adjudicating them is exactly what the missing ruled list would be.
- `G8.0`'s 22 control failures were not traced to a cause in the controls themselves.
- The dossier reads **replicate 1** for every series. Replicates 2 and 3 were used for reproducibility
  only; certification already establishes the annual totals are bitwise identical, but the monthly and
  peak series of rep2/rep3 were not exported.
- No 3J/2J artefact, no manuscript text, and no board card was touched. **The board is still not
  re-published.**
