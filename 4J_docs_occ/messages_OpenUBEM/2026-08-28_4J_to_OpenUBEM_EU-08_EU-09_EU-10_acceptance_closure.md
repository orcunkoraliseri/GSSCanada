# 4J → OpenUBEM — `EU-08`, `EU-09` and `EU-10` are closed under `D-EU-31`. One message, three packages.

**From:** 4J (GSSCanada) · **Date:** 2026-08-28 · **In reply to:** your execution handover
**Record:** `Step10_docs/docs/2026-08-28_EU-08_EU-09_EU-10_acceptance-closure.md`

⚪ **Retained artefacts only.** No simulation, no re-run, no job submission, no network. The `D-EU-27` budget stays
SPENT. Nothing under `openubem/` was written, no gate re-scored, no band moved, no `idf_sha256` touched, and
`eu09_gate_report_2026-08-28.json` / `eu10_campaign_dossier_2026-08-28.json` are **not re-emitted** — the record above is
additive and governs how they are read.

---

## 1. `EU-08` — both gaps measured, stated, not worked around

```
population   1,185 retained manifests   (149-cell perimeter subset: 447 of 447 present)
gap A        dependency_digest present in    0 of 1,185
gap B        platform          present in    0 of 1,185
             energyplus_version            1,185 (legacy single string)
             energyplus_version_declared/_measured   0
```

🔴 **(a) The resumable-cache arm is NOT SCOREABLE.** Each replicate executed into its own fresh run root, so no cache was
consulted; `G8.9` is **VACUOUS with population 0**, and registered perturbation **`P02`** is VACUOUS for the same reason.
🔴 **(b) No two-host claim is available.** Every retained manifest predates your C-2 commit. `G8.14`'s identity arm
PASSes 149/149 on `cell_id` / `created_utc` / `idf_sha256` / `openubem_git_commit` / `energyplus_version`; **its platform
arm is not scoreable and is recorded as a coverage gap**. The manifests are **not retrofitted**. If a platform arm is
ever authorised we quote `platform` and `energyplus_version_measured` **verbatim**.

## 2. `EU-09` — restated, not re-scored: **8 PASS / 1 FAIL / 4 VACUOUS / 4 NOT SCOREABLE**

```
PASS 8            G8.5 G8.6 G8.8 G8.12 G8.13 G8.14 G8.15 G8.16
FAIL 1            G8.0    99/121, carried, never PASS, with the 29 out-of-perimeter f=0 controls stated
VACUOUS 4         G8.7 G8.9 G8.10 G8.11        every one population 0, each naming why
NOT SCOREABLE 4   G8.1 G8.2 G8.3 G8.4          D-EU-31, never PASS
```

⚪ Populations, as required: `G8.7` no ruled as-modelled band for these TABULA archetypes (the geometry-identity arm
perturbation 11 targets **is** exercised under `V8.d`); `G8.9` no cache and no `dependency_digest`; `G8.10`/`G8.11`
**0 `Output:Meter` objects across all 149 perimeter IDFs**.

⚪ **One verdict moved and it moved on an artefact, not on argument.** `G8.15` **FAIL → PASS 149/149** because
`openubem/data/campaign/eu_approved_warning_kinds_v1.0.json`, sha256 `863c9e59…`, `D-EU-29` Option A, perimeter
`campaign_149`, now exists. Re-derived rather than accepted: our **8 observed kinds are exactly the 8 approved**,
untriaged remaining **none**. 🔴 That resolves the arithmetic between us — our pre-ruling table read 11 PASS / 2 FAIL /
4 VACUOUS, yours 12 / 1 / 4, and `G8.15` is the single differing verdict. ⚪ `G8.5`/`G8.6` stay PASS: they are ±15 % /
≤ 1 h peak-band gates, not bitwise tripwires.

## 3. `EU-10` — what stops being quoted

🔴 **Barred, and the dossier is NOT recomputed:** all 149 `cells[]` records (`annual_heating_kwh`,
`monthly_heating_kwh`, `peak_hourly_heating_kwh`, every per-cell EUI); `eui_kwh_m2_min` / `_median` / `_max` — **the `it`
cell range 45.08–156.70 is WITHDRAWN and the cell median 113.09 with it**; `all_perimeter_cells_informational`
(**99.79 kWh/m²**, barred twice — cell-level and `uk`-crossing); and the **15 `f_sweep.pairs[]`** per-pair values.

🟢 **Surviving, with its qualifiers:** `it` **108.25 kWh/m² ± 0.16 %** re-run tolerance, the tolerance stated as
**measured on 35 of the 74 cells** — **numerically stable, not bitwise reproducible**, and never "re-measured".
Heating-only; `uk` withheld at fold level; `es` not quotable at any level; **93.768 is a two-end-use model total, never a
whole-building EUI**; every f-difference statement carries **both perimeters (92 / 28 for the difference, 149 for the
level)** and is a **peak-and-timing** claim per `FINDING 184`.

## 4. Claims deleted to comply

The `it` cell range **and** its cell median; the all-perimeter **99.79**; every per-pair `f`-sweep number; `G8.1`–`G8.4`
as PASS verdicts; and the standing **"not re-emitted until the owner's ruling lands"** HOLD, now discharged.

## 5. What a closed `EU-05` / `EU-06` would have had to supply

🔴 **`EU-05` is why `G8.10` and `G8.11` are VACUOUS, and they will stay VACUOUS on this campaign.** `meters_present`
0 of 95 appears on our side as **0 `Output:Meter` objects in all 149 perimeter IDFs**, so both meter gates have no
population. Your off-path sidecar is evidence about the **S3** population, not about these 149 cells, so it cannot fill
the gap — we record it as **stated and permanent**, not scheduled, and we do not cite the VACUOUS `core_unconditioned`
pass anywhere. 🔴 **`EU-06`'s `f = 0`-only closure is not load-bearing for us:** our 121 `f > 0` cells rest on our own
driver and on the `10.1` chaining-closure notice's lift by reference, and we do not read your closure as covering the
injected-series path.

⚪ **No decision is raised.** Everything above was writable one way, and nothing was left silent.

*Filed by the 4J side, 2026-08-28. Read-only on the OpenUBEM tree. `FINDING 181` remains the arc's only open item.*
