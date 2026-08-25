# `D-S8-3` — the equal-facade box conserves floor area and volume. It does not conserve envelope area, and what it loses is country-correlated.

**Date:** 2026-08-24 (night)
**Raised by:** the item 8.1 build, from measurement — not from reading the ruling again
**Status:** 🟢 **CLOSED 2026-08-25 — ruled (a) by the author and IMPLEMENTED.** See §7 for the
ruling, and the Step 8 progress log entry of 2026-08-25 for what the implementation measured. 🔴 The
brief said "a few archetypes" would fall back; **38 of 88 do**, and `FINDING 117` records why that is
structural rather than numerical, and what artefact survives.
**Evidence:** `Step8_docs/outputs_step8/archetype_idf_manifest.csv` (88 rows, written by
`tools/4thJ_step8_idf.py`); `4thJ_08_bemSimulation.md`, entry 2026-08-24 (night), `FINDING 110`.

---

## 0. This is not a request to revisit `1(a)` on the grounds it was ruled on

`1(a)` was ruled to neutralise `FINDING 109` — that all 36 British archetypes carry zero South and
zero North glazing while the Spanish and Italian sheets use all four faces. **It does that, and
nothing here weakens it.** The equal split over four facades is not in question.

What is in question is the **other half** of `1(a)`: the fixed 1 : 1.5 aspect ratio, and the fact
that the box is derived from `A_C_Ref` and `n_Storey` alone. That half was ruled without the number
below, because the number did not exist until 88 IDFs were built.

---

## 1. The fact

The box is built as `A_plate = A_C_Ref / n_Storey`, `W = sqrt(1.5 · A_plate)`, `D = sqrt(A_plate / 1.5)`,
`H = n_Storey · h_room`. **Floor area is conserved exactly. Volume is conserved exactly.** Nothing in
that derivation reads `A_Wall_1..3`, `A_Roof_1..2` or `A_Floor_1..2`, so TABULA's published envelope
areas are not used — and are not reproduced.

Modelled opaque envelope area over published, and the consequence for the transmission heat loss
coefficient `H_transmission = Σ U·A` (the quantity the whole of Step 8 turns on):

| fold | envelope area, box / TABULA | `H_transmission`, box / TABULA |
|---|---|---|
| `es` | median **0.889** (0.515 – 1.926) | median **0.924** |
| `uk` | median **0.946** (0.699 – 1.552) | median **0.956** |
| `it` | median **0.718** (0.361 – 1.322) | median **0.765** |

🔴 **Italy's transmission loss is understated by 23.5 %. The UK's by 4.4 %. The spread is 19
percentage points, and it is deterministic per country.**

By class, the driver is visible — and it is not the class mix, because every fold carries the same
four classes in equal numbers:

| class | `es` | `uk` | `it` |
|---|---|---|---|
| `SFH` | 0.873 | 0.871 | 0.792 |
| `TH` | 0.961 | 1.139 | 1.063 |
| `MFH` | 0.906 | 0.934 | **0.703** |
| `AB` | 1.022 | 1.058 | **0.656** |

The Italian reference buildings for `MFH` and `AB` are shaped nothing like a compact box.
`IT.MidClim.AB.02` publishes `A_Wall = 3,257 m²`. The box built from its own `A_C_Ref = 2,448 m²`
over 4 storeys has **473 m²** of wall — a factor of **6.9**.

⚪ Note the direction is not uniform even within a fold: the maxima above are over 1.0. Spain's
`ES.ME.MFH.03` box has *more* envelope than TABULA publishes. It is not a bias that can be divided
out; it is a per-archetype shape error whose **median** happens to be country-correlated.

## 2. Why it matters here and not in an ordinary BEM study

In a study that reported one country, an equivalent-box envelope error is a known and declared
approximation. **This study holds one country out at a time and asks whether a model trained on two
others transfers.** An artefact that is fixed per country and worth 19 pp of transmission loss sits
in exactly the channel the claim is measured in — the same shape as `FINDING 53` (three day bases),
`FINDING 60` (two household conventions) and `FINDING 109` (three glazing conventions). Every one of
those was caught because somebody measured instead of assuming, and every one of them changed how a
result may be read.

---

## 3. The decision

**May the box stop being 1 : 1.5 where TABULA's own areas say it should not be?**

| | option | what it does | cost |
|---|---|---|---|
| 🟢 **(a)** | **Keep the equal four-facade glazing split. Replace the fixed aspect ratio with the aspect that reproduces TABULA's published wall area.** Solve `2(W+D)·H = A_Wall_total` with `W·D = A_plate` — one quadratic per archetype, no new data, no new assumption. Where no real solution exists (the wall area is below the minimum perimeter for that footprint), fall back to 1 : 1.5 and **record which archetypes fell back**. | Conserves floor area, volume **and** wall area. `FINDING 110` collapses to whatever the roof/floor terms alone contribute. `FINDING 109` stays neutralised — the glazing split is untouched. | The box is no longer one shape; the aspect ratio becomes an output, and a few archetypes get very elongated. Requires re-running the 88 builds and the selftest — about four minutes, no GPU, no Speed job. |
| **(b)** | **Keep `1(a)` exactly as ruled, and declare `FINDING 110` as a limitation.** Report the three medians in the paper and state that Italian transmission is understated relative to British. | Nothing to rebuild. The rulings stand untouched. | A 19 pp country-correlated error sits inside the LOCO channel and is defended in prose rather than removed. Any Italian result that differs from the others has a second explanation nobody can exclude. |
| **(c)** | **Derive the box from `A_Wall` and let floor area follow.** Perimeter from the published wall area, footprint from perimeter at 1 : 1.5. | Conserves envelope exactly. | Breaks `A_C_Ref`, which is the basis of `c_m`, of `phi_int` and of every EUI we will report. Trades a known error for a worse one. **Not recommended.** |

🟢 **Recommendation: (a).** It is additive — it changes one derived quantity in one function, it
removes a country-correlated artefact rather than declaring it, and it leaves both things `1(a)` was
actually ruled *for* — the equal glazing split and the conservation of floor area — exactly as they
are. The fallback list makes the residue visible instead of silent.

⚪ If **(b)**, say so explicitly and the limitation goes into the paper with these three numbers in
it, not a hand-wave.

---

## 4. What does not change whichever way this goes

* The **88** archetypes, the `4a`/`4b` resolution, and the exclusion of Italy's ten combined-class
  rows. Selection is not touched.
* `3(a)`'s two-layer construction. The areal capacity is distributed over whatever envelope the box
  has, so it re-conserves automatically.
* The equal four-facade glazing split.
* `FINDING 111` — the ISO 6946 / EnergyPlus film-convention gap — is independent of this and is
  already handled correctly in the code.

## 5. Still blocked regardless

* **Item 8.2 has no weather file.** 8.3 cannot start.
* `G8.1`–`G8.4` have no reference series; no Step 8 gate has ever been run.
* 🔴 **Decision 14 (chaining) is open** and closes here, on a watt.

---

## 6. How to answer

One line is enough: `D-S8-3 = (a)`, `(b)` or `(c)`. If (a), the rebuild and the full 88-run
EnergyPlus selftest run immediately and the fallback list comes back with the result.

---

## 7. AUTHOR'S ANSWER

> **`D-S8-3` Ruling:** 🟢 **Option (a) — Replace fixed aspect ratio with archetype-specific aspect ratio that reproduces TABULA published wall area, while preserving the equal four-facade glazing split.**
>
> Solve $2(W+D)\cdot H = A_{\text{Wall\_total}}$ with $W\cdot D = A_{\text{plate}}$. For archetypes where no real solution exists (wall area below minimal perimeter), fall back to $1:1.5$ aspect ratio and explicitly log the fallback in `archetype_idf_manifest.csv`.

---

## Author's Directives & Action Plan

| # | Item | Ruling | Core Action | Impact / Invariants |
|---|---|---|---|---|
| **1** | `D-S8-3` (Archetype Envelope Area Conservation) | 🟢 **Option (a)** | **Calculate aspect ratio per archetype from TABULA $A_{\text{Wall}}$ quadratic**; conserve $A_{\text{plate}}$, volume, and wall area; maintain equal 4-facade glazing distribution; log any minimal-perimeter fallbacks to $1:1.5$. | Eliminates the 19 pp country-correlated transmission artifact (`FINDING 110`) before running EnergyPlus simulations. |

### Execution Directives:
1. Update `tools/4thJ_step8_idf.py` with the quadratic wall-area aspect ratio solver.
2. Re-emit the 88 archetype IDFs and re-run the 88-archetype EnergyPlus selftest suite.
3. Record all fallback archetypes in `Step8_docs/outputs_step8/archetype_idf_manifest.csv`.
4. Invariants: Floor area $A_{\text{C\_Ref}}$, thermal capacitance $c_m$, internal gain baseline, and the equal 4-facade glazing split (`1(a)`) remain strictly conserved.

---

## 8. WHAT THE IMPLEMENTATION FOUND — read this with §7

Executed 2026-08-25. All four directives carried out; all four invariants hold (selftest `A6`, `A7`,
`A8`, `A10`, `A11`). 26 of 26 checks pass, all 88 archetypes still run in EnergyPlus with zero severe
errors, and every new check was **seen failing** under injection before being trusted — one of them,
`A5`, was a **no-op** as first written and the battery is what caught it.

🟢 **The ruling delivered what it names.** Wall area box/TABULA is now **1.000 / 1.000 / 1.000** by
fold. `H_transmission` box/TABULA: **0.982 `es` / 0.995 `uk` / 0.933 `it`**. The 19.1 pp
country-correlated spread of `FINDING 110` falls to **6.1 pp** — a 68 % reduction.

🔴 **Two things the brief did not anticipate, both recorded as `FINDING 117`:**

1. **38 of 88 archetypes fall back, not "a few".** 26 because no real box exists
   (`S < 2√A_plate`) — and **19 of those 26 are terraced houses**, whose TABULA `A_Wall` excludes
   the party walls a free-standing box must have. That is a modelling-convention collision, not a
   data error, and no aspect ratio repairs it. A further 12 fall back because the solved box is so
   elongated that a quarter of the glazing will not fit on the narrow facade (`IT.MidClim.AB.02`
   wanted 186.4 m × 3.3 m and **409 %** of that facade as glass). Since directive 4 makes the equal
   split a strict invariant, the **aspect** gives way and the split is never broken.
2. **The 6.1 pp that survives is not a remainder — it is the fallbacks.** Among the 50 solved
   archetypes the spread is **4.8 pp**; among the 38 fallbacks it is **43.1 pp**. By class the
   residue is two opposite-signed cells: **`it`/`AB` still 0.656** (10 of the 12 glazing fallbacks
   are Italian `AB`/`MFH`) and **`uk`/`AB` now 1.137**. Never quote the 6.1 pp headline without
   them: an Italian `AB` result and a British `TH`/`AB` result are the two places a LOCO difference
   is still explainable by geometry.

⚪ **One follow-on is available and is NOT taken here**, because it is a new rule rather than an
application of (a): the 12 `glazing_does_not_fit` rows could be clamped to the most elongated
*admissible* aspect — the shape that just fits the glazing — instead of reverting all the way to
1 : 1.5. That would recover part of the Italian `AB` deficit while keeping the equal split intact.
It needs a ruling.
