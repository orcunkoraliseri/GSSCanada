# `EU-08`, `EU-09`, `EU-10` — acceptance closure under `D-EU-31`

**Filed:** 2026-08-28 · **Owner:** 4J side · **Basis:** retained artefacts only
**Handover:** `openubem-92`, 2026-08-28 — *"EU-08, EU-09 and EU-10 are the only open work packages and all three are yours … from RETAINED ARTEFACTS ONLY."*

⚪ **No simulation, no re-run, no job submission, no network.** The `D-EU-27` re-run budget stays **SPENT**. No gate was
re-scored, no band moved, no promoted artefact edited, no `idf_sha256` touched. `eu09_gate_report_2026-08-28.json` and
`eu10_campaign_dossier_2026-08-28.json` are **not re-emitted**; this document is the additive record that governs how
they may be read.

Retained run root `openubem/outputs/eu_certified_rerun_2026-08-28/` (`rep1`/`rep2`/`rep3`), **1,185 manifests** over the
395-cell campaign, of which **447** (149 cells × 3 replicates, all present) carry the ruled perimeter.

---

## 1. `EU-08` — the accounting is closed with **two measured coverage gaps**

Both are stated in the acceptance record rather than worked around, and both are **properties of the retained
manifests**, not of the campaign's physics.

### 1.1 🔴 Gap A — no `dependency_digest`, so the resumable-cache arm of acceptance is **NOT SCOREABLE**

```
population:  1,185 retained manifests  (149-cell perimeter subset: 447)
measured:    dependency_digest present in 0 of 1,185
```

Each replicate executed into its **own fresh run root**, so no cache was ever consulted and the stale-output guard has
**no population at all** — not a pass. `G8.9` is therefore **VACUOUS with its population named as 0**, and registered
perturbation **`P02`** (*schedule changes without clearing cache*) is reported **VACUOUS** for the same reason.
🔴 **This is a coverage gap, not a defect to route around:** a resumable cache is exactly the mechanism `G8.9` exists to
catch, and on this campaign nothing exercised it.

### 1.2 🔴 Gap B — no `platform` field, so **no two-host claim is available**

```
population:  1,185 retained manifests
measured:    platform present in 0 of 1,185
             energyplus_version present in 1,185 (legacy key, single string)
             energyplus_version_declared / _measured present in 0
```

Every retained manifest **predates OpenUBEM's C-2 commit**, which added `platform` (seven keys, including
`energyplus_sha256`) and the `energyplus_version_declared` / `_measured` split. `G8.14`'s identity arm PASSes 149/149 on
`cell_id`, `created_utc`, `idf_sha256`, `openubem_git_commit` and `energyplus_version`; **its platform arm is not
scoreable here**. 🔴 **These manifests must never be retrofitted**, and no result from this campaign may be presented as
a two-host or cross-platform finding. If a platform arm is ever authorised, `platform` and `energyplus_version_measured`
are to be quoted **verbatim**, never restated as "23.1".

### 1.3 ⚪ What `EU-08` does close

395 cells run, the ruled 149 reproduced independently from the campaign table alone, the `f > 0` lift read from
`2026-08-26_10.1_chaining-closure-notice.md` **by identity** and recorded in every cell manifest, the presence series
taken from `eu_cell_presence_binding_v2.json` and never re-derived at run time.

---

## 2. `EU-09` — the gate table is **RESTATED, not re-scored**

**8 PASS / 1 FAIL / 4 VACUOUS / 4 NOT SCOREABLE**, seventeen gates.

| status | gates | population |
|---|---|---|
| **PASS** (8) | `G8.5` `G8.6` `G8.8` `G8.12` `G8.13` `G8.14` `G8.15` `G8.16` | 149 cells / 298 replicate pairs / 37 archetype × fold groups as each gate declares |
| 🔴 **FAIL** (1) | `G8.0` | 121 `f > 0` perimeter cells |
| ⚪ **VACUOUS** (4) | `G8.7` `G8.9` `G8.10` `G8.11` | **0** in every case, and each names why |
| 🔴 **NOT SCOREABLE** (4) | `G8.1` `G8.2` `G8.3` `G8.4` | 149 cells — the engine, not the population, is the reason |

**Every vacuous gate names its population, as required:**

* `G8.7` — **0**. No as-modelled published band has been ruled for these TABULA archetypes, so there is nothing to grade
  against. The geometry-identity arm perturbation 11 targets **is** exercised, under `V8.d`.
* `G8.9` — **0**. §1.1: fresh run root per replicate, no cache consulted, no `dependency_digest` retained.
* `G8.10` and `G8.11` — **0**. **0 `Output:Meter` objects across all 149 perimeter IDFs**; heating comes from the Zone
  Ideal Loads hourly variable, never a meter. No meter population exists to score.

🔴 **`G8.0` is carried FAIL and is never PASS.** 99 of 121 `f > 0` perimeter cells have an `f = 0` control that
completed in **all three** replicates — the same strictness the perimeter itself is defined at; **12 of the 22 failures
completed in replicate 1 and failed in a later replicate**. Separately, **29 of 121** `f > 0` cells have an `f = 0`
control that is **not itself inside the ruled perimeter**, so **no f-versus-baseline difference may be quoted for those
29**.

🔴 **`G8.1`–`G8.4` are NOT SCOREABLE on this engine (`D-EU-31`)** and are never reported as PASS, exactly as `G8.0` is
carried as FAIL. They read 298/298 replicate pairs within band; `FINDING 188`–`191` establish that a bitwise
reproducibility comparison cannot pass reliably on any cell of this engine, so the verdict is withdrawn rather than
inverted. ⚪ `G8.5`/`G8.6` stay PASS: they are **peak-band** gates at ±15 % / ≤ 1 h, not bitwise tripwires.

### 2.1 The one verdict that moved, and the artefact that moved it

⚪ **`G8.15` FAIL → PASS 149/149.** It did **not** move on argument. The artefact is
`openubem/data/campaign/eu_approved_warning_kinds_v1.0.json`, sha256
`863c9e594277b5b4ef1197d5f35d68096c3ee8c71ef09f6115097d1d93b16f0c`, ruled **`D-EU-29` Option A, 2026-08-28**, perimeter
string **`campaign_149`**. Re-derived here rather than accepted: the **8 distinct warning kinds** our scorer observed —
`calculated design cooling load for zone`, `calculatezonevolume`, `entered zone volumes differ from calculated zone
volume(s).`, `fixviewfactors`, `getsurfacedata`, `getvertices`, `managesizing`, `processscheduleinput` — are **exactly**
the 8 approved under `campaign_149`; **untriaged kinds remaining: none**. ⚪ Four of the eight are recorded as **stated
design assumptions**, not benign notices, and `indicated zone volume <` stays **REFUSED — repaired, not approved**.

🔴 **The pre-ruling report on disk still reads `11 PASS / 2 FAIL / 4 VACUOUS`.** It is not re-emitted; this section is
the restatement, and the restated table is the one to quote.

---

## 3. `EU-10` — the dossier under `D-EU-31`: what stops being quoted

🔴 **The dossier is NOT recomputed.** `D-EU-31` bars *use*, not emission: the fields below remain on disk and stop being
quoted.

### 3.1 Barred outright — no cell-level number from the 149, anywhere

* `cells[]` — **all 149 records**: `annual_heating_kwh`, `monthly_heating_kwh`, `peak_hourly_heating_kwh` and every
  derived per-cell EUI. Not in text, not in a table, not as a plot label, not as an illustration.
* `headline_heating_eui.it_fold_level.eui_kwh_m2_min` / `_median` / `_max` — the **`it` cell range 45.08–156.70 is
  WITHDRAWN**, and the median with it: a median over cells is a cell-level statistic.
* `headline_heating_eui.all_perimeter_cells_informational` — pools `uk` into a fold-crossing aggregate, so it is barred
  twice over (`D-EU-26` and the cell-level bar). **Never quote 99.79 kWh/m².**
* `f_sweep.pairs[]` — the 15 per-pair `annual_heating_kwh`, `pct_vs_f0`, `peak_hourly_heating_kwh` and
  `peak_hour_index_0based` values are cell-level numbers and stop being tabulated.

### 3.2 What survives, with its qualifiers attached

🔴 **Exactly one fold-level figure exists:** `it`, **108.25 kWh/m²**, area-pooled over 74 cells, **± 0.16 % re-run
tolerance**, and the tolerance is itself stated as **measured on 35 of those 74 cells** (`FINDING 192`, the cells that
completed in all ten replicates). The claim is **numerically stable, not bitwise reproducible**; the stronger claim is
barred and **"108.25 was re-measured" must never be written**.

* **Heating-only.** Every EUI is space heating from the Zone Ideal Loads hourly variable; it may never be compared to a
  whole-building EUI or a measured total. **93.768 is a two-end-use model total, never a whole-building EUI**, and
  **66.868 kWh/m² is heating-only**.
* **`uk` is withheld at fold level** (`D-EU-26`); **`es` is not quotable at any level** (`D-EU-28`, `FINDING 182`).
* **Every f-difference statement carries BOTH perimeters** — **92 cells / 28 archetypes** for the difference, **149**
  for the level — and, per `FINDING 184`, is a **peak-and-timing** claim, never an annual-demand claim: the injection
  formula conserves the annual mean by construction and OpenUBEM asserts that conservation to rtol 1e−8.
* `hourly_sum_reconciles_to_manifest` — 149 of 149, **0 mismatched** — stands as a consistency statement about the
  artefacts, carrying no cell-level value.

---

## 4. Claims deleted to comply

1. The **`it` cell range 45.08–156.70** — withdrawn from the quotable set, and with it the `it` cell **median 113.09**.
2. The **all-perimeter pooled 99.79 kWh/m²** — withdrawn, as a `uk`-crossing aggregate.
3. **Every per-pair `f`-sweep number** — the 15 pairs stop being tabulated; only the aggregate statement, at both
   perimeters, survives.
4. **`G8.1`–`G8.4` as PASS verdicts** — withdrawn and carried as NOT SCOREABLE.
5. The board and dossier line **"HOLD: not re-emitted until the owner's ruling lands"** — discharged, the ruling landed.

---

## 5. What a closed `EU-05` or `EU-06` would have had to supply

Raised now rather than worked around, as instructed.

🔴 **`EU-05` is the reason `G8.10` and `G8.11` are VACUOUS and will stay VACUOUS on this campaign.** `meters_present`
stays **0 of 95** because `write_outputs()` is not wired into either campaign runner; on our side that appears as **0
`Output:Meter` objects across all 149 perimeter IDFs**, so both meter gates have no population. ⚪ The off-path sidecar
(95/95, all five meters, `max_abs_diff` 0.0) is **evidence about the S3 population, not about these 149 cells**, and
cannot fill the gap. Wiring it in place would re-run the promoted campaign and change every hash, refused on the same
ground as `D-EU-24`'s geometry remedy — so the gap is **stated and permanent**, not scheduled.
⚪ `EU-05`'s `core_unconditioned` pass is **VACUOUS — 0 of 95 emit a core zone by design — and is not cited anywhere in
this record**.

🔴 **`EU-06` is closed at `f = 0` ONLY, and our 121 `f > 0` cells do not rest on it.** They rest on our own driver and on
the `10.1` chaining-closure notice, which lifted the block **by reference**; `f > 0` remains blocked upstream by
`D-EU-09` and the Step 7 chaining rule, which was never OpenUBEM's to lift. **This closure must never be read as
covering the injected-series path.**

⚪ Nothing else in `EU-08`/`EU-09`/`EU-10` needed something a closed `EU-05` or `EU-06` would have supplied.

---

## 6. What did not change

⚪ Perimeters unchanged — **149 level, 92 difference**. `D-EU-28` and `D-EU-30` are **not reopened**, and re-deriving
certification from the ten `FINDING 181` replicates was **rejected explicitly** and must not be re-proposed without new
evidence. `FINDING 181` remains the arc's **only open item**: contention excluded, mechanism unidentified, and the
phenomenon reaches inside the 149. ⚪ `FINDING 186`'s odds ratio **4.12 is struck from all citation**; its qualitative
association stands.
