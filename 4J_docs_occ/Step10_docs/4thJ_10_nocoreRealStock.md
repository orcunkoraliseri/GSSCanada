# Step 10 — campaign `C2`: no-core real-stock UBEM simulation

### 4J HETUS LLM pipeline. Implementation specification.
#### Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 10. Campaign `C1` (core-era, closed): `archive_C1_core_era/4thJ_10_ubemRealStock.md`. Validation: `4thJ_10_nocoreRealStock_val.md`.
#### Origin: `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` (I-1 through I-7), ruled `D-IMP-1/2/3` (a) on all three, docket `IMP/docs/DONE/2026-09-03_D-IMP-1_D-IMP-2_D-IMP-3_nocore-review-rulings.md`.
#### Engine: **OpenUBEM**, no-core build — does not exist yet. `D-EU-79`–`D-EU-88` (owner's ruling, OpenUBEM side). `D-EU-55` binds: no EnergyPlus without the owner's own sentence.

---

## STATUS

🔴 **SPEC ONLY. NOTHING COMPUTED, NOTHING SIMULATED, NO CELL RUN, 2026-09-03.**

🟢 **Re-homed 2026-09-03 under `D-IMP-4`** (author's ruling: *"I want a clean pipeline, not an
extra step like 12"*). This document was first filed as `Step12_docs/4thJ_12_nocoreRealStock.md`
under `D-IMP-2`(a); **the pipeline ends at Step 11 and there is no Step 12.** The no-core campaign
is **Step 10's second campaign, `C2`**, at `Step10_docs/` (its `C1` predecessor archived beside it in `archive_C1_core_era/`). Step 10 now declares two
campaigns:

* **`C1` — core-era** (`archive_C1_core_era/4thJ_10_ubemRealStock.md`, `archive_C1_core_era/4thJ_10_ubemRealStock_val.md`): run,
  scored and **CLOSED** — 410 cells, 18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2
  NOT_EVALUABLE. 🔴 Retained as the **method and reproducibility record only. No `C1` result is
  reported.** Frozen: not re-opened, not re-scored, not deleted.
* **`C2` — no-core** (this document and its validation companion): the campaign that will be
  reported. Nothing computed.

🔴 **`Overview.md:683`'s registration rule is honoured by the gate namespace, not by a step
number.** `C1`'s `G10.x` stays spent on the core-era basis; `C2` opens **`G10N.x`**, one row per
`G10.x` with the inheritance stated on it, so no gate ID ever claims two bases.

Step 10 `C2` waits on the OpenUBEM blockers of §8 and on `D-EU-55`; **`C1` and Step 11 do not
re-open.**

---

## 1. AIM

Re-test the Step 10 real-stock hypotheses (`H10`, the coincidence-factor shape) under the owner's
**no-core** dwelling-subdivision rule instead of the core-era layout the OpenUBEM engine still
implements. A floor plate divides into **dwellings only** — no core, corridor, access band or
unconditioned zone; every square metre belongs to a flat; nothing narrower than 2 m; one flat = one
zone (`D-EU-79`/`80`/`81`). This changes the **population** (which buildings emit a layout, and
how many dwellings each one carries) — it does not change the injection formula, the chaining
convention, or any Step 10/11 gate that does not depend on the layout geometry.

## 2. What is carried from Step 10 **unchanged**

* `H10` and the `CF(N_u)` formalism (`CF = P_peak,bldg / Σ P_peak,zone`, the `g_inf + (1−g_inf)/√N`
  shape) — geometry-agnostic; only the population it is measured over changes.
* The injection formula `φ_int(t) = (1−f)·3.0 + f·3.0·g(t)/mean(g)`, the `f` set
  `{0, .15, .30, .50, 1.00}`, per-zone **and** per-building conservation (`G10.13`'s discipline),
  the chaining convention `independent`, seed 1 (decision 14), and `rotate_to_midnight()`
  (`D-S9-3`(a)). Any campaign `C2` emission path inherits these verbatim.
* Step 7's interface: presence **fraction** `g(t)`, never watts (`D-S7-7`(a)); one
  `Schedule:File` + `People` pair per dwelling; `Interpolate to Timestep = No`.
* Every closed board: Steps 1–9, Step 10's 24 gates, the `EU-09` restated board, `prereg.md` and
  its md5, `D-EU-31` Option A, the never-quote list. `G10.1`–`G10.4` stay on 40 paired cells
  (`es` 30 / `it` 10 / `uk` 0) and that naming travels with every number.
* The refusals on record: option (c) of `D-S10-1`; Option B of `D-EU-31`; any re-run of the 149;
  any retrofit of a manifest.

## 3. What changes — the population

**Four districts**: Madrid, Lyon, London, Bologna. **France (Lyon) is a physical baseline —
never a 4J denominator** (`G10.11` carries over intact, extended `G10N.11`); no French fold, no
French held-out fold, no French diary.

### 3.1 `N_u` under no-core (I-3)

$$N_u := k \times \text{storeys}, \qquad k = \max(1, \text{round}(\text{dwellings\_total} / \text{storeys}))$$

Source table: `IMP/docs/2026-09-03_nocore_projection_41.csv` (41 buildings; columns
`k_nocore`, `n_u_nocore`, `dwelling_deficit_nocore`). The deficit `N_u − observed_dwellings` per
building is **reported, never gated** — it is a census-arithmetic property of the projection, not
a model result. The 41-building figures **332 / 312 / 230** on that table (and any figure derived
from it) are **census arithmetic, never a result** — no plate has been cut and no campaign exists.

The spec names, per gate, which `N_u` it means: the Step 10 sense (`zone_count_built`, the
core-era engine's own count) or the no-core sense (`n_u_nocore`, this section). A gate row that
does not say which is a defect in the row, not a free choice.

### 3.2 Arm F, redefined (carried from I-1/I-9)

Arm F was `one_zone_per_floor` under the core-era layout. Under no-core it is redefined as:
**check-FAIL or unusable footprint → one box per floor** (no longer a convexity refusal alone —
any layout-route failure, for whatever reason, falls back to one box per floor). `G10.22`'s
LOWER BOUND wording is kept verbatim: an Arm F total under-predicts systematically because it
spatially averages non-coincident gains, so it is a lower bound, publishable, never presented as
an estimate. `G10.19`'s 30-per-fold floor is **reachable on census arithmetic only** — nobody has
counted how many no-core Arm D buildings the four-district population yields; that count does not
exist until the layout route runs, which needs the engine carry-in.

## 4. Binding rule — one series per drawn flat (I-5, `D-IMP-3`(a))

Every drawn flat gets its **own independent series** (Case B semantics) by rank order from a
per-fold emission **sized to the district's dwelling count**. Sizing is done **on paper, from the
census `k × storeys`**, labelled **"projected, not measured"** — `tools/4thJ_step7_schedules.py`
(selftest 61/61) is **not invoked**; nothing is emitted now. All drawn storeys are eligible;
non-residential ground floors are a declared limitation, reported not gated. Case A stays the
paired control, exactly as in Step 10. `G10.8` (content-located fold) and `G10.20` (Case A/Case B
distinct) carry over as `G10N.8` / `G10N.20` rows.

## 5. Manifest fields (I-6)

Every campaign `C2` manifest, when one is ever written, carries all of: `weather_sha256`,
`energyplus_build_hash`, `energyplus_version` (measured, not literal — `FINDING 187`),
`openubem_version`, `openubem_git_commit`, measured `platform`, `rotated_to_midnight`,
`diary_origin_hour`, `completed`, `completion_status`, `scheme`, `status`, `k`,
`observed_dwellings`, `dwelling_deficit`. See `4thJ_10_nocoreRealStock_val.md` `G10N.14` (the `G10.14`
twin) for the blank-field perturbation.

## 6. Replicate arm (I-7)

A named subset re-run `R` times on one host measures re-run tolerance. The **quotation rule**:
inside tolerance → quotable, with the tolerance stated; outside → **barred**, named as barred, and
the barring is never silent. The `.err` marker census (`PsyPsatFnTemp` / `PsyTwbFnTdbWPb`,
`FINDING 182`/`193`) rides along as an **INFO column**, never a gate. See
`4thJ_10_nocoreRealStock_val.md` `G10N.replicate` for the out-of-tolerance perturbation. **No
compute is authorised now**; this section specifies the arm for when it runs.

## 7. Preflight guard

`tools/4thJ_step10_nocore_preflight.py` — read-only. Asserts, per manifest: `scheme ==
"nocore_equal_area"`, `status == "direct"`, a check verdict present, and the sha256 of
`openubem/geometry/european_residential.py` against a pinned no-core digest
(`ENGINE_DIGEST_PIN = "TBD_by_owner"`, so the digest arm fails by construction until the owner
pins it after carry-in). No EnergyPlus, no network, no cluster. **Seen failing today, 410 of 410,
on the retained Step 10 manifests** — record: `impl/2026-09-03_preflight-seen-failing.md`.

## 8. What waits on the OpenUBEM side (§4 of the governing review)

Engine carry-in of the no-core rule into `european_residential.py` ("identified, not ordered"),
`D-EU-84` (no aspect rung at FAIL 0), `D-EU-87` (`C10` pinch test not implemented), `D-EU-88`
(district viewer, not started), and `D-EU-55` (no EnergyPlus without the owner's own sentence).
None of these is 4J's to fix.

---

## Progress Log

Append-only. Never delete or reformat an existing entry; if a decision changes, edit that entry.

### 2026-09-03 — spec created, boxes 4/5/6 of the execution run-book

Implementation and validation documents written; population (four districts), `N_u` formula
(I-3), Arm F redefinition, binding rule (I-5, `D-IMP-3`(a)), manifest field list (I-6), replicate
arm and quotation rule (I-7) all specified. Preflight guard written and **seen failing** on all
410 retained Step 10 manifests (`impl/2026-09-03_preflight-seen-failing.md`). Prereg draft filed
at `prereg_step10_nocore_DRAFT.md` (DRAFT, not frozen, no md5 sidecar). No compute, no EnergyPlus, no
cell, no emission. `Step6_docs/outputs_step6/prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`)
never opened for writing.
