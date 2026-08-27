# Step 10 — Real-stock UBEM simulation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_10_ubemRealStock.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md` Step 10.

---

## STATUS

⚪ **PRE-REGISTERED, 2026-08-26. Nothing scored.** Every threshold below is registered before any Step 10
cell exists. 🔴 **A threshold registered here is not moved to make a gate pass** — that is the one move
this project refuses, and Step 9 shipped three FAILs rather than make it (`G9.6`, `G9.7`, `G9.12`).

---

## 🔴 THE GATE-ID RULE, WHICH EXISTS BECAUSE TWO DOCUMENTS ALREADY CLAIM `G8.x`

`Step8_docs/IMP_step8/4thJ_08_bemSimulation_IMP.md` §8 and `MVP_european_locations.md` §9.11 both score
a suite called **`G8.0`–`G8.16`** on the OpenUBEM basis — real footprints, OSM geometry, ERA5 weather,
a different engine. Those IDs are **already spent** on the 4J side: they are scored, several were seen
failing, `G8.12`/`G8.16` report `NOT_EVALUABLE` on the 88 `f = 0` cells, and `D-EU-13` is an **open
off-by-one on the OpenUBEM copy of `G8.13`** (MVP §12.6), still awaiting an author ruling.

> **Rule.** Step 10 opens a **new `G10.x` series**. No Step 10 result is ever filed under a `G8.x` ID, and
> no `G8.x` ID is scored by Step 10. Where a `G10.x` gate inherits a Step 8 threshold, the inheritance is
> **written on that gate's row**, verbatim, so a reader can see whether the bar moved.

Two documents claiming one ID on two different bases is how a **basis change hides as a fix**. This rule
is the whole reason Step 10 is a new step rather than an edit to Step 8.

---

## THE GATE TABLE

### A. Inherited from Step 8, thresholds unmoved

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G10.0`** 🔴 Uninjected control first | An injected number quoted with no matched control | The `f = 0` control of a cell is read **before** any `f > 0` result from that cell is quoted. Count of violations: **0** | `G8.0` verbatim. Also MVP §12.11 receiving step 3 |
| **`G10.1`** | NMBE, monthly | ±**5 %** | `G8.1`. 🔴 Reference = **an independent re-run**, `D-S8-1`(a) extended verbatim. **A reproducibility tripwire, not a measured-accuracy claim** — the `FINDING 44` inversion |
| **`G10.2`** | NMBE, hourly | ±**10 %** | `G8.2`, same reference clause |
| **`G10.3`** | CV(RMSE), monthly | **15 %** | `G8.3`, same reference clause |
| **`G10.4`** | CV(RMSE), hourly | **30 %** | `G8.4`, same reference clause |
| **`G10.5`** | Peak magnitude vs the named comparison series | ±**15 %** | `G8.5` / `D-S8-5` item 2. 🔴 **The occupancy peak shift is REPORTED as an empirical result, never gated against the flat control** |
| **`G10.6`** | Peak timing | ≤ **1 h** | `G8.6`, same clause |
| **`G10.7`** | Per-building EUI vs a published band | **INFO, permanently — no band is created** | `G8.7` / `D-S8-5` item 1(a). 🔴 No numeric EUI band exists anywhere in this project and Step 10 does not create one |
| **`G10.8`** 🔴 Fold correctness | A dwelling driven by the fold that held it out | Every dwelling's diary is located **by content** (name + md5) among the Step 7 bundles and its fold read from the bundle's own manifest. Cells simulating a country under another country's fold: **0**. 🔴 Applies **per dwelling**, not per building | `G8.16`, extended to `N_u` diaries. Scored against 4J's assignment table, **never** against OpenUBEM's `held_out_country = null` |
| **`G10.14`** | Manifest completeness | Every cell carries schedule sha256, IDF sha256, weather sha256, EnergyPlus version **and build hash**, `openubem_version`, `openubem_git_commit`, and a **measured** platform field | `G8.14` + MVP §9.6 |
| **`G10.15`** | Convergence and warnings | Zero severe errors; warning classes itemised and triaged **by kind, not by frequency**. 🔴 **Inherited as OPEN**: this gate is a live FAIL on the OpenUBEM side (MVP §12.5, untriaged warnings). Step 10 does not report it clean because the engine changed | `G8.15` |
| **`G10.16`** | Schedule ingestion, both arms | The presence series EnergyPlus actually used, read back from the **saved IDF**, matches the Step 7 file by md5 (**value arm**), and the gain object still names that `Schedule:File` (**assignment arm**). 🔴 Scored **per zone** — with `N_u` schedules per building, a single-schedule check would pass a building whose dwellings all share one series | `G8.12`, extended per zone |
| **`G10.17`** | Interpolation setting | `Interpolate to Timestep = No` on every schedule object, asserted from the **saved IDF**, on the real **9-field** `Schedule:File` shape | `G8.13`. 🔴 `FINDING 126`: the old parser read only the LAST comma-field, so a `Yes` was invisible on a 9-field object and the row read PASS. 🔴 **`D-EU-13` is an OPEN off-by-one on the OpenUBEM copy of this gate** — Step 10 must **not** adopt the OpenUBEM scorer for `G10.17` until `D-EU-13` is ruled |
| **`G10.18`** | Schedule origin | The series is rotated to midnight: declaration arm per run, two phase arms once per bundle (05:00 ≥ **0.90** of daily max, trough at hour ≥ **8**, manifest declares `rotated_to_midnight`) | `G8.17` + `G7.19` verbatim. 🔴 `FINDING 141`: without this, occupancy is applied **four hours early** and 13,108 runs were wrong while every board stayed green |

### B. New to Step 10

| Gate | What it catches | Threshold |
|---|---|---|
| **`G10.9`** 🔴 Population separation | Arm D and Arm F silently pooled; a stock-level EUI quoted from a convexity-selected sample | (i) Rows pooling dwelling-partitioned (Arm D) and `one_zone_per_floor` (Arm F) buildings in one statistic: **0**. (ii) Stock-level EUI statistics quoted from Arm D: **0**. Both asserted by a search over the results artefacts, which prints the files it scanned |
| **`G10.10`** 🔴 CRS invariance | A layout census whose yield is an artefact of the projection | The layout audit runs in the manifest's **native** CRS with no reprojection, and the CRS is **declared in the manifest**. Seen failing by reprojecting a passing building to `EPSG:2154`. 🔴 **Retargeted 2026-08-26 (evening): this gate tests the ROTATION ORIGIN, not the tolerance units.** The recorded story — an absolute `1e-8 m²` tolerance crossed at `area_error_fraction` `5.09e-12` — **does not close**: the building is 544.206 m², so the implied gap is 2.77e-9 m², *inside* tolerance, which needs **~1 965 m²** to cross. The verified fact is `european_residential.py:504` rotating about the literal origin. Pass condition: the same building emits the same layout under a **centroid-translated** frame in both CRSs. (`../DeepResearchPrompts/VETTING_RL28_RL29.md` §1.6) |
| **`G10.11`** 🔴 France exclusion | A French cell counted in a 4J denominator | `FR` cells in any 4J denominator, any `f > 0` French cell, or any French cell carrying a diary: **0**. `FR-B` lives on its own manifest |
| **`G10.12`** 🔴 Weather-basis firewall | The weather reported as occupancy | No artefact places an **absolute** Step 8 EUI beside an **absolute** Step 10 EUI. Only control-referenced relative deltas cross, reported side by side and **never differenced**. Asserted by a search over the results artefacts, which prints the files it scanned. 🔴 Justification: `FINDING 120` puts the station alone at **5–11 %** of heating demand against an occupancy channel of a few per cent |
| **`G10.13`** 🔴 Per-zone conservation | A conservation clause that holds in the generator and not in the artefact | Annual mean `φ_int` is exactly `3.0 W/m²` **per zone** *and* **per building** at every `f`, asserted on the **emitted CSV on disk**, with the numeric bound derived from the write format. 🔴 `FINDING 132` is this exact failure at building level (4.01e-07 relative at `%.6f`); with `N_u` series it can now also fail per zone while the building mean is right |
| **`G10.19`** 🔴 `H10` vacuity | A hypothesis test with no population at one end | The `H10` test requires **≥ 30 buildings per fold with `N_u ≥ 2` and a full stack**. Below that it prints **`NOT_EVALUABLE`** with the population named — never a pass, never a fail. 🔴 `S1` measured **1 of 12** buildings reaching a dwelling layout and **18 of 297** in the full census; this gate is the reason that number is checked **before** the campaign, not after |
| **`G10.20`** 🔴 Paired control present | A diversity effect that is really a geometry effect | Every Step 10 building at every `f` carries **both** Case A (one diary replicated to all `N_u` zones) and Case B (`N_u` independent diaries), on the **same footprint, archetype, weather, `f` and seed policy**. Cells reporting `delta_div` from a **cross-building** comparison: **0**. Seen failing by deleting one Case A partner and confirming the row is refused rather than silently compared across buildings |
| **`G10.21`** 🔴 `CF` reported, and the fit reported with it | `H10` decided on a channel where the effect cannot be seen | (i) `CF(N_u) = P_peak,bldg / sum(P_peak,zone)` and the 99th-percentile hourly power are emitted for every cell. (ii) Case A returns `CF = 1.000` to the declared numeric bound — **it is 1 by construction, so a Case A `CF` ≠ 1 is a defect in the harness, not a result**. (iii) The `CF(N) = g_inf + (1-g_inf)/sqrt(N)` fit is reported **with residuals**; a monotone-but-not-`sqrt(N)` outcome is printed as its own verdict, never rounded into a PASS. 🔴 Annual EUI is reported but does **not** decide `H10` — `FINDING 143` died on exactly that channel |
| **`G10.22`** 🔴 Arm F declared as a bound | A biased fallback quoted as an estimate | Every artefact carrying an Arm F aggregate labels it a **lower bound** on heating demand and peak power, never an estimate, because `one_zone_per_floor` spatially averages non-coincident gains. ⚪ **Direction only.** `RL29`'s magnitudes (−5…−15 % annual, −10…−25 % peak) rest on a self-refuting citation (`[R2]`) and **may not be quoted**; the gate checks the label, not a number |
| **`G10.23`** ⚪ No dead-blocker remedies | A fix applied to a defect that no longer reproduces | Before any geometry remedy enters the pipeline, the defect it targets is **re-measured on disk** and the measurement is filed with the remedy. 🔴 This gate exists because the 173-vertex `EPLUS_FATAL` was carried in three documents while `s1_smoke_manifest.csv` already read **12 of 12 `EPLUS_COMPLETED`**, and an RDP remedy was proposed for it that would have altered every footprint in the corpus |

---

## VACUITY GUARDS

A gate is not accepted because it passes clean data. **Every gate must be observed failing its designated
mutation, while the null perturbation fells none.**

* **`V10.a`** — **The mutation battery.** Each `G10.x` has a named mutation. The battery reports
  `n ok / n FAILED` and `k of k injections HIT`. A gate with no injection that fells it is **not
  registered as passing**.
* **`V10.b`** — **Named empty populations.** Three-way scoring: `PASS` / `FAIL` / `NOT_EVALUABLE`. A gate
  scored over zero units prints `NOT_EVALUABLE` **and names the population**, never `PASS`. (MVP §12.4;
  `G8.12`/`G8.16` did exactly this on the 88 `f = 0` cells.)
* **`V10.c`** — **`NOT CHECKED` is never a `PASS`.** 🔴 `FINDING 149`: Step 9's runner tallied
  `16 PASS / 3 FAIL` by counting `G9.4`'s `NOT CHECKED` as a pass; the true board is
  `15 PASS / 3 FAIL / 1 NOT CHECKED`. The tally itself is checked, not just the per-gate verdicts.
* **`V10.d`** — **Search gates print their scope.** `G10.9`, `G10.11` and `G10.12` print the files they
  scanned and **FAIL if they scanned fewer than the declared artefact set**. (`V9.d` shape — a search gate
  that scans nothing passes everything.)
* **`V10.e`** — **Cache proved to HIT first.** Before any "it re-ran" claim, the cache is proved to hit on
  an unchanged cell. A cache that never hits makes stale-output evidence meaningless. (`G8.9`'s shape.)
* **`V10.f`** — **The caveat register travels.** Every Step 10 dossier carries the OpenUBEM caveat
  register; the entry **count is checked against the register, not asserted from memory** (22 at the time
  of writing, MVP §12.10). C-01, C-03 and C-09 are read before any number.
* **`V10.g`** — **Gate-ID hygiene.** No Step 10 artefact writes a `G8.x` or `G9.x` verdict. Asserted by a
  search over the Step 10 outputs.
* **`V10.h`** — **Conservation asserted on disk.** `G10.13` reads the emitted CSV, never the generator's
  in-memory array. 🔴 This guard exists because `FINDING 132` passed in the generator.
* **`V10.i`** — **🔴 A recorded blocker is re-measured before it is designed around.** Every blocker
  quoted in a Step 10 artefact carries the date it was **last measured**, not the date it was first
  written. A blocker older than the most recent regeneration of the artefact it lives in is
  **`STALE_UNVERIFIED`** until re-run. This guard exists because on 2026-08-26 two recorded blockers were
  checked and **both failed**: the 173-vertex `EPLUS_FATAL` no longer reproduces at all, and the CRS
  tolerance arithmetic does not close on its own building's area.

---

## 🔴 THE FAILURE MODES THIS SUITE IS BUILT AGAINST

Each is a real event in this project, not a hypothetical:

| Shape | Where it happened | The gate that answers it |
|---|---|---|
| A gate looked as though it had been seen firing, on a fixture whose shape differed from the real artefact | `FINDING 126` — `G8.13`'s 8-field injection vs a real 9-field `Schedule:File` | `G10.17` + `V10.a` |
| A pre-registered property held in the generator and not in the artefact | `FINDING 132` | `G10.13` + `V10.h` |
| A whole campaign ran on a systematically shifted schedule while every board stayed green | `FINDING 141` — 13,108 runs, occupancy four hours early | `G10.18` |
| The tally counted an unchecked gate as a pass | `FINDING 149` | `V10.c` |
| A histogram that looks like a diagnosis while the discriminating work happens elsewhere | `FINDING 154` (Step 7), `FINDING 151`, `FINDING 152` Control B | `V10.b` — named populations, no vacuous pass |
| A basis change reported as an effect | `FINDING 120` — the weather station worth 5–11 % of heating | `G10.12` |
| A yield measured on a sample selected by the outcome being tested | `D-EU-04-H`, resolved by ruling H1: run the ladder's own 12 and classify every failure | `G10.9`, `G10.19` |
| A blocker designed around long after it stopped reproducing, and a remedy proposed on a diagnosis nobody re-read | the 173-vertex `EPLUS_FATAL`, carried in three documents against a manifest reading **12 of 12 `EPLUS_COMPLETED`**; IDD limit measured non-existent | `G10.23` + `V10.i` |
| An external report returning our own unverified figure rated Tier 1 | `RL29` B15, the 120-vertex `BuildingSurface:Detailed` limit — `README` vetting step 6 | `G10.23`, and the vetting record itself |
| A hypothesis decided on a channel whose spread swamps the effect | `FINDING 143` — peak ratios 0.54 / 0.02 / 0.40 against the between-diary spread | `G10.21` — `CF` against a constant, not a spread |
| Diversity confounded with geometry by comparing different buildings | designed out before it happened | `G10.20` |

---

## PROGRESS LOG

### 2026-08-26 — pre-registered

Nineteen gates and eight vacuity guards registered before any Step 10 cell exists. Twelve gates inherit a
Step 8 threshold verbatim with the inheritance written on the row; six are new; one (`G10.15`) is
inherited **as an open FAIL** rather than reset by the engine change.

### 2026-08-26 (evening) - four gates added, one retargeted, after `RL28` and `RL29` were vetted

**Twenty-three gates and nine guards.** Record: `../DeepResearchPrompts/VETTING_RL28_RL29.md`.

* **`G10.20`** paired Case A / Case B within footprint - diversity can no longer be confounded with geometry.
* **`G10.21`** `CF` decides `H10`, not annual EUI, and the `sqrt(N)` fit ships with its residuals.
  Case A gives `CF = 1` **by construction**, so the test runs against a constant rather than a spread -
  which is the failure mode that killed `FINDING 143`.
* **`G10.22`** Arm F is labelled a **lower bound**. Direction carried, magnitude refused.
* **`G10.23`** no remedy enters the pipeline for a defect that was not re-measured on disk.
* **`G10.10` retargeted** to the rotation origin. Its recorded tolerance arithmetic does not close:
  544.206 m2 at a fraction of 5.09e-12 is a 2.77e-9 m2 gap, inside the 1e-8 tolerance.
* **`V10.i`** a recorded blocker carries the date it was last **measured**, not first written.

🔴 **No threshold was moved and no gate was loosened.** Every addition is a new check. `G10.21` changes
which channel decides `H10`, and that change is recorded **before any Step 10 cell exists** - the
pre-declared text of `H10` itself was left untouched.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched. No Step 8 or Step 9 threshold moved.

### 2026-08-27 — 🟢 first gates SCORED. `G10.20` PASS; `G10.21` NOT_EVALUABLE with its population named

Work item 10.9 (paired emission) is the first Step 10 item to put numbers on this table. Scored on
**297 buildings / 2,970 cells / 15,760 emitted CSVs**; record `4thJ_10_ubemRealStock.md` §9.2 and
`impl/2026-08-27_work-item-10.9_paired-case-a-case-b.md`.

| gate | verdict | basis |
|---|---|---|
| **`G10.20`** | **PASS** | 0 missing partners, 0 geometry mismatches, 0 cross-building `delta_div` rows, 0 refusals; **15,760 files scanned** and printed (`V10.d`) |
| **`G10.13`** | **PASS** | 15,760 zone rows, 0 zone fails, 0 building fails, scored **per case** |
| **`G10.8`** | **PASS** | 3,152 dwellings, 0 unlocatable, 0 wrong-fold |
| **`G10.9`** | **PASS** | 0 buildings carrying both arms |
| **`G10.19`** | **`NOT_EVALUABLE`** | es 9 · uk 5 · it 3 against 30 per fold |
| **`G10.21`** | **`NOT_EVALUABLE`** | population *simulated Step 10 cells*, **size 0** |

🟢 **Battery 10 of 10 with the null case moving nothing** (`V10.a`, both halves). `G10.20` was seen
failing on three distinct clauses of its own row — a deleted Case A partner, a cross-building pairing,
and Case A areas moved 10 % — so no single clause is carrying the gate.

Every other gate in this table is **NOT CHECKED** and is written as such — `V10.c`: an unchecked gate is
never a pass, and the tally is checked, not only the verdicts.

🔴 **`V10.a` did its job on a guard we wrote ourselves.** `W10.9` was first written to score
`G10.21`(ii) literally — *Case A returns `CF = 1.000`* — and the battery's `case_a_independent` case,
which is precisely the harness defect that clause names, **passed** it. `FINDING 158`: `CF_phi` is 1 for
the independent case too, because every Step 7 presence series reaches 1.0 and independent households
still share hours at which all are in — **1,450 of 1,450** Case B cells with `N_u ≥ 2`, minimum **396**
fully coincident hours. A guard whose discriminator is constant in the ground truth is not a guard.

**The repair is additive.** `W10.9` now scores **series identity** (sha256 of the emitted files, taken
before reduction); the `CF = 1` arm is kept, reported, and stamped **`CARRIED, NOT SCORED`** inside the
artefact. **`W10.12`** is added as permanent **INFO** publishing the degeneracy. No threshold moved, no
gate loosened, `H10`'s text unedited.

🔴 **A pre-registered consequence for `G10.21`, recorded before 10.6 runs.** §1.1a chose `CF` because in
the synchronised case it is 1 *by construction* — a comparison against a constant rather than a spread.
That is unchanged. What `FINDING 158` adds is that **the constant is not evidence**: on the driver the
independent case is also exactly 1, so **`CF_A = CF_B = 1.000` on simulated power would be a
`NOT_EVALUABLE`, not a null**. `FINDING 159` adds that `q99` equals the peak in **2,970 of 2,970** cells
here, so the two channels `G10.21`(i) asks for are one channel until EnergyPlus runs.

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` verified live. No Step 8 or Step 9 threshold moved.
