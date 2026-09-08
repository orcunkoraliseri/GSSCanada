# Step 10 — campaign `C2`, no-core real-stock UBEM. Pre-registration. **DRAFT.**

🔴 **THIS IS A DRAFT. NOT FROZEN. NO MD5 SIDECAR.** `Step6_docs/outputs_step6/prereg.md`
(md5 `e4243e07cdd80c9c846b91f40e3e8c45`) is the project's one frozen pre-registration and is never
opened for writing by this document or any campaign `C2` tool. This draft becomes citable only when the
owner freezes it and a sidecar md5 is added; until then nothing here may be quoted as a
pre-registered bar.

**Written** 2026-09-03, box 4 of `IMP/Prompt/4thJ_imp_nocore_execution_2026-09-03.md`. **Re-homed 2026-09-03 under `D-IMP-4`** from `Step12_docs/prereg_step12_DRAFT.md` — there is no Step 12; this pre-registers Step 10 campaign `C2`, gate series `G10N.x`.

---

## What this pre-registers (draft)

* **Hypothesis**: `H10` unchanged from Step 10 — at fixed `f`, the occupancy effect on building
  peak grows with `N_u`, the number of independently diarised dwellings, measured via
  `CF(N_u) = P_peak,bldg / Σ P_peak,zone`.
* **Population**: the no-core layout of the four districts (Madrid, Lyon, London, Bologna),
  Arm D = dwelling-partitioned under the no-core rule, Arm F = check-FAIL-or-unusable-footprint
  fallback (§3.2 of `4thJ_10_nocoreRealStock.md`). France (Lyon) is a physical baseline, never a
  4J denominator.
* **Design**: paired Case A (one diary replicated to all `N_u` zones) / Case B (`N_u` independent
  series), same footprint/archetype/weather/seed policy, exactly Step 10's `10.9` design.
* **Gate series**: `G10N.x`, this document’s companion `4thJ_10_nocoreRealStock_val.md`.
* **What is NOT pre-registered here**: any numeric value from a cell, campaign or manifest — none
  exist. The `N_u` figures on `IMP/docs/2026-09-03_nocore_projection_41.csv` are census arithmetic,
  not a pre-registered population size.

## Freeze conditions (not yet met)

1. The OpenUBEM engine carry-in of the no-core rule into `european_residential.py` must land.
2. `D-EU-84` and `D-EU-87` must be ruled and closed.
3. The owner must pin `ENGINE_DIGEST_PIN` in `tools/4thJ_step10_nocore_preflight.py`.
4. The owner must give the sentence `D-EU-55` requires before any EnergyPlus run.
5. The owner freezes this document and a sidecar md5 is written beside it.

None of the five conditions is met as of 2026-09-03. This draft is not amended in place to record
that fact — this STATUS section is the record, and future edits to this file happen only to refine
the pre-registration itself, never to backdate a freeze that has not happened.

### STATUS, 2026-09-08 (additive — the 2026-09-03 sentence above is left standing)

**Conditions 1 and 2 are now MET. Conditions 3, 4 and 5 are the author's own and remain OPEN.**

* **1 — MET.** The OpenUBEM engine carry-in landed 2026-09-03 (`european_nocore.py`, bit-parity
  **0 mismatches on 2,529 / 2,529 compared plates**, all four districts); `D-EU-88` and `EU-19`
  complete.
* **2 — MET.** `D-EU-87` implemented (`C10` rebuilt as a created-pinch test). `D-EU-84` closed
  2026-09-08 as **`D-EU-110`, an accepted named residual**: `MAX_FLAT_ASPECT` stays at the
  strictest rung **2.5** per `D-EU-89` clause 2, and **81 of 550 plates across 57 unique buildings
  ship as an honest residual `FAIL`**, carried by 4J as a declared limitation. 🔴 The closure
  wording includes, and 4J froze against, the clause that **`EU-21` acceptance criterion 2 remains
  NOT met**. We did not ask for the threshold to be moved and did not move one of ours.
* **3, 4, 5 — OPEN.** All three are the author's actions and all three happen **before** the first
  district runs, never after.

🔴 **Two things must be settled before condition 5 is executed**, both recorded in
`impl/2026-09-08_openubem-layouts-reemitted-verified.md` and neither applied:

1. **Which population Step 11 consumes.** §3.1's `N_u := k × storeys` was census arithmetic written
   when no plate had been cut. The plates are now cut and the emitted zone list disagrees with the
   formula on the majority of buildings (§4 of that record). The recommendation is that the
   **emitted zone is the dwelling**, with `N_u` retained as the projection sense and its deficit
   reported, never gated. This is a pre-registration question, so it belongs here, before the
   freeze.
2. **The London coverage figure.** London ships **451 side-cars for 706 simulated buildings** — a
   named limitation on their side (`_gb_rows` yields no record for the 255-building
   coverage-recovery batch), not a defect and not something to wait for. **451 of 706** is the
   figure to pre-register; a `JSON count == published row count` check fails London by design.

Nothing on the OpenUBEM side blocks campaign `C2` any more. `C2` still has **no cell**, and this
document is still **DRAFT and unfrozen**.

#### Addendum, 2026-09-08 later the same day (additive — nothing above is rewritten)

Both open points above were answered by the OpenUBEM owner the same day. Record: §9 of
`impl/2026-09-08_openubem-layouts-reemitted-verified.md`.

* **The London figure is a DATED SNAPSHOT, not a final coverage.** The 255 are `D-EU-108`'s newly
  admitted London population (187 age-inherited + 68 straddle-disambiguated, never simulated) and
  they sit in a **1,534-case Speed array that has not run**; `D-EU-107`/`108`/`109` are all still in
  execution and **no date exists**. London coverage **will rise above 451**. 🔴 The decision stands —
  **pre-register 451 of 706 as of 2026-09-08, name the 255, do not wait** — but pre-register it *as
  a dated snapshot*, so that re-pre-registering when the recovery lands is an **explicit act with a
  visible before and after**, never a silent restatement. They undertake to announce the new counts
  before we could consume them, the same undertaking as for `FINDING 258`.
* **The `N_u` disagreement is explained and is not a defect on either side.** Their `FINDING 246`:
  the district census cuts one `k` **per building**, the engine re-derives `k` **per storey**.
  Verified from our side one for one — `N_u = k × storeys` reproduces the emitted zone count on
  exactly the uniform-per-storey buildings and fails on exactly the non-uniform ones (553 / 47 /
  880, matching 1,100−547 / 439−392 / 1,036−156). The owner independently gives the same
  recommendation we do: **the emitted zone is the dwelling**, `floors[].dwelling_count` is
  authoritative, and **`dwellings_total` is provenance — an attribute, never a check.** 🔴 Also:
  **`units_per_floor` is the maximum per-storey count, never a constant** — `units_per_floor ×
  storeys` is not a population and must not be written as one.

🔴 Still unruled and still the author's. Nothing in this pre-registration has been changed.
