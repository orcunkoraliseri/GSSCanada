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
