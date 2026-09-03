# Step 12 — No-core real-stock UBEM simulation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_12_nocoreRealStock.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`.

---

## STATUS

⚪ **PRE-REGISTERED, 2026-09-03. Nothing scored — no cell exists.** Every threshold below is
registered before any Step 12 cell exists, exactly as Step 10's own gate table was. 🔴 **A
threshold registered here is not moved to make a gate pass.**

## 🔴 THE GATE-ID RULE

`G10.x` is already spent on the Step 10 basis (core-era engine, 410 retained cells). Step 12 opens
a **new `G12.x` series** on the no-core basis. **Inheritance from `G10.x` is stated on every row**,
verbatim, so a reader can see whether a bar moved. No Step 12 result is ever filed under a `G10.x`
ID, and no `G10.x` ID is re-scored by Step 12.

---

## THE GATE TABLE

All rows currently read **NOT_EVALUABLE — no Step 12 cell exists.** The verdict column is what
each row *will* score once a cell exists; nothing below is a claim about any number.

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G12.0`** | Uninjected control first | Same as `G10.0`: `f=0` read before any `f>0` quoted | `G10.0` verbatim |
| **`G12.1`–`G12.4`** | NMBE / CV(RMSE), monthly/hourly | ±5% / ±10% / 15% / 30%, same reference clause | `G10.1`–`G10.4` verbatim. **Reproducibility tripwire, not accuracy** |
| **`G12.5`, `G12.6`** | Peak magnitude / timing | ±15% / ≤1h | `G10.5`/`G10.6` verbatim |
| **`G12.7`** | Per-building EUI vs published band | INFO permanently, no band | `G10.7` / `G8.7` verbatim |
| **`G12.8`** 🔴 Fold correctness | A dwelling driven by the fold that held it out | Per dwelling, content-located (name + md5) | `G10.8` verbatim, extended to the no-core `N_u` |
| **`G12.9`** | Arm D / Arm F never pooled | 0 buildings carrying both arms | `G10.9` verbatim |
| **`G12.10`** | CRS / rotation-origin tripwire | Reported, never gated (per `FINDING 194`) | `G10.10`, itself retargeted 2026-08-26 |
| **`G12.11`** 🔴 France is not a fold | 0 French diaries, 0 `f>0` French cells | `G10.11` verbatim |
| **`G12.12`** | Weather-basis firewall | No absolute Step-8-basis EUI beside a Step-12-basis EUI | `G10.12` verbatim |
| **`G12.13`** | Conservation, per zone and per building | `phi_int` annual mean exactly 3.0 W/m² | `G10.13` verbatim |
| **`G12.14`** 🔴 Manifest completeness | All 15 fields of §5 present on every manifest | 0 blank fields | `G10.14` twin, extended list (I-6). **Perturbation seen felling — see below** |
| **`G12.15`** | Convergence and warnings | Zero severe; classes triaged by kind | `G10.15`, inherited OPEN as on the OpenUBEM side |
| **`G12.16`** | Schedule ingestion, both arms, per zone | md5 + assignment arm | `G10.16` verbatim |
| **`G12.17`** | Arm label survives aggregation | Arm F never silently pooled into an aggregate | `G11.17` / `G10.9` |
| **`G12.18`** | Declaration arm, `rotated_to_midnight` | Field present and true | `G10.18` twin |
| **`G12.19`** | `H10` population floor | ≥30 qualifying Arm D buildings per fold | `G10.19`, floor reachable on census arithmetic only (§3.2) |
| **`G12.20`** 🔴 Binding rule, Case A/B paired | Present within footprint; cross-building `delta_div` refused | `G10.20` verbatim. **Perturbation seen felling — see below** |
| **`G12.21`** | `CF` and √N fit | Residuals reported; Case A `CF≠1` is a harness defect | `G10.21` verbatim |
| **`G12.22`** | Arm F is a LOWER BOUND | Direction only, magnitude refused | `G10.22` verbatim, restated §3.2 |
| **`G12.23`** | Geometry remedy vacuity | 0 remedies entered = `NOT_EVALUABLE_VACUOUS` | `G10.23` verbatim |
| **`G12.replicate`** 🔴 Re-run tolerance, quotation rule | A named subset re-run `R` times on one host; outside tolerance → barred, never quoted | New, I-7. **Perturbation seen felling — see below** |

## VACUITY GUARDS

* **`V12.a`** — every gate above prints `NOT_EVALUABLE` with its population named as `0` (no Step
  12 cell exists), never a vacuous PASS.
* **`V12.b`** — a failing gate's perturbation demonstrates nothing; Step 12 inherits nothing
  failing yet because nothing has been scored.
* **`V12.i`** (`V10.i`'s twin) — a recorded blocker carries the date it was last **measured**, not
  the date it was first written; the preflight guard's engine digest was re-measured 2026-09-03,
  not copied from the review document.

---

## Perturbations seen felling, on scratch fixtures — 2026-09-03

No production tool exists yet (spec only). Each perturbation below is demonstrated on a minimal
scratch fixture built for this check alone, per `feedback_gates_must_be_seen_failing.md`. Script:
`impl/2026-09-03_box5-6_scratch_perturbations.py` (not a shipped tool; deleted after the run is
not required since it makes no claim about any real cell — kept as the record of the check).

### `G12.14` — blank one field in a scratch manifest

A scratch manifest with all 15 required fields (§5) present scores **0 blank**. Blanking one field
(`weather_sha256 = null`) at a time, for all 15 fields in turn, must each independently fell the
gate. **Result: 15 of 15 single-field blanks felled `G12.14`; the all-fields-present baseline did
not fell it.** Seen felling.

### `G12.replicate` — one cell beyond tolerance

A scratch replicate set of `R=5` values, tolerance ±0.5%: four values inside tolerance of their
mean, one value planted 2.0% off. The quotation rule must read the whole subset as **BARRED**, not
average around the outlier. **Result: the 5-value set with the planted outlier reads BARRED; a
control set with all 5 values inside tolerance reads QUOTABLE.** Seen felling.

### `G12.20` binding rule — two dwellings sharing a series in Case B

A scratch building with `N_u=3` drawn flats, each assigned an independent series by
`gain_sha256`. Two dwellings pointed at the **same** `gain_sha256` (the collision mutation) must
fell the binding gate. **Result: the collision fixture (2 of 3 dwellings sharing one
`gain_sha256`) FAILS; the independent-series baseline (3 distinct `gain_sha256`) PASSES.** Seen
felling.

### Wrong-fold series — the `G10.8` mutation, extended

A scratch dwelling assigned a series whose bundle manifest names a different fold than the
dwelling's own country. Must fell `G12.8`. **Result: the mismatched-fold fixture FAILS; the
matched-fold baseline PASSES.** Seen felling.

All four checks: baseline clean, mutation fells its target, 0 false positives, 0 no-ops. No real
manifest, cell, or campaign artefact was touched.
