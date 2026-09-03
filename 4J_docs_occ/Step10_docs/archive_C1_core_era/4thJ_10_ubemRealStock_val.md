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


### 2026-08-28 (evening) --- 🟢 **THE SUITE IS SCORED IN FULL: ALL 24 `G10.x` GATES, ON THE SIMULATED 410**

⚪ The board carried **8 of 24**. The other 16 were **NOT CHECKED on a simulated cell**,
and several had been scored at 10.4 / 10.9 on the **emitted** artefacts --- a different
basis, which does not carry. All 24 are now scored on the simulated cells.

| Verdict | Gates | n |
|---|---|---|
| **PASS** | `G10.0` `G10.1` `G10.2` `G10.3` `G10.4` `G10.5` `G10.6` `G10.8` `G10.9` `G10.10` `G10.11` `G10.12` `G10.13` `G10.16` `G10.17` `G10.20` `G10.21` `G10.22` | **18** |
| 🔴 **FAIL** | `G10.14` `G10.18` | **2** |
| INFO, permanently | `G10.7` | 1 |
| OPEN_INHERITED | `G10.15` | 1 |
| `NOT_EVALUABLE_FAIL_BY_POPULATION` | `G10.19` | 1 |
| `NOT_EVALUABLE_VACUOUS` | `G10.23` | 1 |

🔴 **NO ENERGYPLUS WAS INVOKED.** Every number is read off an artefact that already
existed. `D-EU-31` untouched; no certified EU cell read, quoted or recomputed; `prereg.md`
md5 `e4243e07cdd80c9c846b91f40e3e8c45` unchanged. Batteries **7 of 7** and **4 of 4** felled.

⚪ **`G10.1`-`G10.4`** against the **Speed re-run** (`D-S8-1`(a) extended verbatim): worst
|NMBE| monthly **5.348e-15**, hourly **5.509e-15**; worst CV(RMSE) monthly **1.109e-14**,
hourly **6.338e-14**. 🔴 **A REPRODUCIBILITY TRIPWIRE, NOT A MEASURED-ACCURACY
CLAIM** --- the `FINDING 44` inversion on the gate row. 🔴 **Population: 40 paired
cells, `es` 30 / `it` 10 / `uk` 0.**

⚪ **`G10.5`** worst relative peak difference **5.388e-14** and **`G10.6`** worst
peak-hour separation **0 h**, both on all **410**. **`G10.0`** 82 controls / 328 injected /
0 violations. **`G10.8`** **2,300 dwelling zones**, 0 unlocatable, 0 wrong-fold. **`G10.9`**
41 buildings, 0 carrying both arms. **`G10.13`** 210 zone rows, bound **derived** from the
10-decimal write format (1.667e-11), worst zone residue **1.102e-12**. **`G10.16`** 210
zones, 0 disagreeing sha256. **`G10.17`** 210 `Schedule:File` objects, **0 not `No`**, field
count **10** --- the real shape, not `FINDING 126`'s 8-field fixture.

🔴 **`G10.14` FAIL, and it is the data, not the parser.** `weather_sha256`,
`energyplus_build_hash`, `openubem_version`, `openubem_git_commit` and a measured
`platform` are on **0 of 410** cells. A campaign-level value is **not** a per-cell manifest
field. **The manifests are NOT retrofitted** (the `EU-08` precedent). The battery ran the
**inverse** mutation --- supply the five fields and the gate moves FAIL to PASS.

🔴 **`G10.18` FAIL --- on the DECLARATION arm only.** The two **phase** arms, scored
**once per bundle** as `G7.19` writes them, **PASS**: `es` 05:00 fraction 1.000 / trough
hour 15, `it` 1.000 / hour 13. **0 of 410 manifests carry `rotated_to_midnight`**, and
`V10.c` says an unchecked arm is never a pass. ⚪ **A four-hour shift would have moved
the 05:00 maximum; it did not move on any scored zone**, so this is a missing field and not
a `FINDING 141` repeat. Per-zone INFO (a **stricter** basis, reported and never scored): 42
rows excluded as degenerate --- at `f = 0` the gain series is the constant 3.0 W/m2 and has
no phase --- and 4 troughs before hour 8, **all four the same single zone**.

⚪ **`G10.23`** `NOT_EVALUABLE_VACUOUS`: **0 geometry remedies entered this campaign**.
A gate with an empty population has not been satisfied, it has not been ASKED.

### 🟢 `FINDING 194` --- `G10.10`'s RECORDED DEFECT DOES NOT REPRODUCE

🔴 The 2026-08-26 retarget put `G10.10` on *"`european_residential.py:504` rotating
about the literal origin"*. Re-measured on disk by `inspect.getsource`, the code reads
**`rotation_origin = footprint.centroid`**, with a comment stating the invariance
explicitly. **The defect no longer exists.** Measured consequence: **the yield is invariant
on 297 of 297 buildings across `EPSG:32631` -> `EPSG:2154`**, so the gate's stated risk ---
*a layout census whose yield is an artefact of the projection* --- **is absent**, and
`G10.10` **PASSES** on its own pass condition.

⚪ Reported, **never gated**: 7 of 297 buildings move their area **shares** under a pure
100 km translation, by **1.3e-9 to 5.0e-7**; cross-CRS worst **5.18e-6**, median
**4.37e-9**. 🔴 **No numeric area-share tolerance is pre-registered for this gate**,
so choosing one now would be a band change. ⚪ An OpenUBEM-side observation, and the
exact class `V10.i` and `G10.23` exist for.

⚪ **Evidence.** `impl/2026-08-28_step10-validation-suite-scored.md` ·
`outputs_step10/realstock_campaign/realstock_gate_board_extension.json`,
`realstock_g10_10_crs.json`, `realstock_g10_1_4_nmbe.json` · tools
`4thJ_step10_val_extension.py`, `4thJ_step10_g10_10_crs.py`,
`4thJ_step10_g10_1_4_nmbe.py` · Speed job **1288393** (`speed_series40.json`).

🔴 **ONE DECISION IS OPEN: `D-S10-1`** --- the artefact-reading gates are scored on
**40 of 410** cells and `uk` is absent. **(a)** widen on Speed's 410 retained trees by
`sbatch`, no re-run **(recommended)**; **(b)** keep the 40 and carry the naming; **(c)**
re-run the 410 locally with `--keep-all`. `G10.14` and `G10.18` do **not** wait on this ---
both fail because a field was never written, and neither is repaired by a wider population.

---

### 2026-08-28 (late) --- INTAKE: the `10.1` chaining closure notice, measured against the Step-10 manifests

The author supplied `Step10_docs/docs/2026-08-26_10.1_chaining-closure-notice.md` (Decision 14
formally closed; convention `independent`, production seed `1`; the `f > 0` lock lifted for the
**European** campaign's 408 cells). Three claims in it touch gates already scored, so they were
**re-measured on the Step-10 artefacts** rather than accepted.

| claim in the notice | measured on Step-10's 410 cell manifests | effect on the board |
|---|---|---|
| convention is `independent`, seed 1 | `chaining_rule = independent` on **328 of 328** `f > 0` cells; `not_applicable_f0` on the **82** controls. No cell disagrees | none --- the campaign already ran under the closed convention |
| `rotated_to_midnight: true`, `diary_origin_hour: 4` "as recorded in **every shipped bundle manifest**" | **TRUE at the bundle level**: all three `Step7_docs/outputs_step7/schedules/leg5_{es,uk,it}_independent_seed1/manifest.json` carry both fields | see below |
| the `f > 0` lift covers 408 runs | that is the **European** campaign's population (`EU-06`/`EU-08`). Step-10's `f > 0` population is **328 of 410**. Different perimeters --- never conflate the two counts | none |

🔴 **`G10.18`'s declaration-arm FAIL STANDS, but its CHARACTER NARROWS.** The gate row reads
*"declaration arm **per run**"*. Measured: **0 of 410** Step-10 cell manifests carry
`rotated_to_midnight`, and **0 of 410** name the Step-7 bundle they drew from, so the declaration
that demonstrably exists upstream is **not reachable from the cell**. This is a
**provenance-link gap, not an undeclared convention** --- the convention IS declared, in all three
shipped bundles. It is still a FAIL under `V10.c` (a field the gate asks for on the run is absent
on the run), still **NOT retrofitted**, and still repairable only by writing the field --- or a
bundle reference --- in a **future** campaign. It remains **not** a `FINDING 141` repeat: the
05:00 maximum did not move on any scored zone.

**A contradiction was suspected and disproved.** The per-zone `independent` flag inside
`manifest["schedules"]` is `false` on 164 `f > 0` cells and `true` on the other 164 while
`chaining_rule` reads `independent` throughout. Measured: the split is **exactly** `case A` /
`case B` --- the flag is the **diversity contrast** (A = one shared diary, B = `N_u` independent
diaries per `4thJ_step10_realstock_campaign.py:712`), **not** the Decision-14 chaining rule.
Two fields, two meanings, one word. **No finding.**

Evidence: `Step10_docs/outputs_step10/realstock_campaign/manifests/*.json` (410),
`Step7_docs/outputs_step7/schedules/leg5_{es,uk,it}_independent_seed1/manifest.json`,
`tools/4thJ_step10_realstock_campaign.py:104,497,712`.

---

### 2026-08-28 (late+1) --- `D-S10-1` RULED **(a)**: THE ARTEFACT-READING GATES ARE RE-SCORED ON SPEED'S 410

The author ruled **option (a)**. Speed's **410 retained run trees** were packed by `sbatch`
(job **1290892**, `COMPLETED 0:0`, 00:00:03; `g10_widen.tar.gz`, 5,215,611 B), pulled down and
extracted to `_local_runs/step10_realstock_speed410`. **410 IDFs and 2,300 `*_gain.csv`** ---
matching `G10.8`'s 2,300 dwelling zones exactly. 🔴 **No re-run, no EnergyPlus, no new
simulation: the job copied bytes that already existed.** `D-EU-31` untouched.

⚪ **The plumbing was controlled before it was trusted.** The same scorer was first run against
the widened output directory with the **old 40-tree** runroot: `G10.13`, `G10.16`, `G10.17` and
`G10.18` came back **byte-identical** to the scored board. Only then was the runroot swapped.

| gate | scored on the 40 | **re-scored on the 410** | verdict |
|---|---|---|---|
| `G10.13` conservation on disk | 210 zone rows, 40 buildings | **2,300 zone rows, 410 buildings**, 0 wrong length, 0 CSVs missing | 🟢 **PASS** |
| `G10.16` schedule provenance per zone | 210 zones | **2,300 zones**, 0 naming no schedule, 0 absent, 0 wrong file, **0 whose sha256 disagrees with the manifest**, 0 whose presence md5 is in no bundle | 🟢 **PASS** |
| `G10.17` `Schedule:File` interpolation | 210 objects | **2,300 objects**, **0** not `No`, field count **10** on every one | 🟢 **PASS** |
| `G10.18` phase arms, per bundle | `es`, `it` only | **all three folds** --- `es` **1.000** / trough **13 h**, `it` **0.9769** / **12 h**, **`uk` 0.9986 / 11 h** | 🟢 **PASS** (arm) |
| `G10.18` declaration arm | 0 of 410 | **still 0 of 410** | 🔴 **FAIL** |

🔴 **`uk` IS NO LONGER ABSENT.** That was the whole content of `D-S10-1`, and it is discharged
for these four gates.

🔴 **`G10.1`--`G10.4` COULD NOT BE WIDENED AND ARE NOT CLAIMED TO HAVE BEEN.** They are a
**paired** local-vs-Speed comparison; only **40 local run trees** survive, so the pair does not
exist for the other 370. They stay on **40 cells --- `es` 30, `it` 10, `uk` 0**, and that naming
must travel with every number they produce. Widening them needs option **(c)**, a local re-run.

⚪ **`G10.13`'s derived bound moved, and the gate passes either way --- reported, not used.**
The bound is derived from the write format as `(0.5 x 10^-dec)/3.0`, with `dec` the **minimum
first-line decimal count** over the population. On the 40 that was 10 (bound **1.667e-11**); on
the 410 the least-precise first line carries **1** decimal, so the derived bound loosens to
**1.667e-2**. 🔴 **Nothing was re-banded to reach a pass**: the measured residue is
**1.434e-12** worst zone and **1.250e-12** worst building, which clears the **tighter** 40-cell
bound by four orders of magnitude. The bound's sensitivity to a single first line is an
**observation on the derivation**, recorded here and **not acted on**.

⚪ **`G10.18`'s per-zone INFO grew with the population and is STILL NOT SCORED** --- it is a
stricter basis than the gate row, and a basis change is a band change. On the 410: **1,840**
phase rows scored, **460** excluded as the degenerate `f = 0` flat control, **23** zones below
the 0.90 morning threshold (worst **0.428**), **84** troughs before hour 8. All eight recorded
examples are `es`, over **4 distinct zones**. 🔴 Reported so it is not lost; **not** a gate
movement, and **not** a `FINDING 141` signature --- the per-bundle 05:00 maximum did not move
in any fold.

⚪ **A stale label was fixed in the scorer, not in the evidence.** `4thJ_step10_val_extension.py`
hard-coded `"population": "the RETAINED local run trees only"` on four gates; on a widened run
that string is simply false. It now reports the runroot it actually read. The already-scored
`realstock_gate_board.json` and `realstock_gate_board_extension.json` under
`outputs_step10/realstock_campaign/` are **untouched**; the widened run writes to a **separate**
directory, `outputs_step10/realstock_campaign_widened/`.

🔴 **PROCESS INCIDENT, RECORDED BECAUSE IT TOUCHES A STANDING RULE.** The first attempt to stage
the pack script sent a heredoc through the remote shell, which is **tcsh**; it mangled, and the
`find`/`tar` lines executed **on the login node** instead of a compute node. The output was
**deleted** and the work resubmitted properly with `sbatch`. Scripts are now uploaded by `scp`
and never composed inline over `ssh`.

⚪ **Evidence.** `outputs_step10/realstock_campaign_widened/realstock_gate_board_extension.json`
(410 trees) · `_local_runs/step10_realstock_speed410/` (410 IDFs, 2,300 gain CSVs) ·
Speed job **1290892**, `/speed-scratch/o_iseri/step10_realstock/widen_pack.{sh,out}` ·
tool `tools/4thJ_step10_val_extension.py`.

⚪ **Board after the widening: unchanged in verdict, wider in population.** 18 PASS, 2 FAIL.
`G10.14` and `G10.18` fail for the same reason as before --- **a field was never written** ---
and a wider population does not repair either. Neither is retrofitted.


---

### 2026-08-28 (late+2) --- OPTION **(c) DECLINED** BY THE AUTHOR: STEP 10 IS FORMALLY CLOSED

🟢 **The ruling, recorded by the author in section 9 of
`Step10_docs/impl/2026-08-28_step10-validation-suite-scored.md`.** Option **(c)** --- a local
re-run of the 410 with `--keep-all` to pair `G10.1`-`G10.4` on the full population --- is
**DECLINED**. No local re-run is authorised, and none was started. `D-S10-1` is closed in full:
**(a)** taken for the artefact-reading gates, **(c)** refused for the paired gates.

⚪ **What that fixes permanently.** `G10.1`-`G10.4` stay scored on **40 paired cells ---
`es` 30, `it` 10, `uk` 0**, and that naming travels with every number they produce. They are a
**reproducibility tripwire, not a measured-accuracy claim** (the `FINDING 44` inversion, written
on the gate row), and the author's rationale rests on that reading: machine agreement at 1e-14
to 1e-15 is already established there; `G10.5` and `G10.6` already carry the **peak** arms on all
**410**; and `G10.13`, `G10.16`, `G10.17`, `G10.18`-phase already reach all 410 (2,300 zones,
`uk` present) through option (a). Nothing is claimed for the 370 unpaired cells, and the
declared population is the disclosure that makes declining honest.

🔴 **What the decline does NOT do.** It does not move a verdict, loosen a band, or repair
a FAIL. `G10.14` and `G10.18`'s declaration arm remain **FAIL on 0 of 410** because a field was
never written; they were never waiting on a population, and they are **not retrofitted**.
`G10.15` stays `OPEN_INHERITED`, `G10.19` `NOT_EVALUABLE_FAIL_BY_POPULATION`, `G10.23`
`NOT_EVALUABLE_VACUOUS`, `G10.7` INFO. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
remains frozen and untouched.

⚪ **Final suite, as ruled: 18 PASS, 2 FAIL, 1 INFO, 1 OPEN_INHERITED, 2 NOT_EVALUABLE.**
PASS = `G10.0`-`G10.6`, `G10.8`-`G10.13`, `G10.16`, `G10.17`, `G10.20`-`G10.22`.

⚪ **Evidence.** `Step10_docs/impl/2026-08-28_step10-validation-suite-scored.md` section 9 ·
`outputs_step10/realstock_campaign_widened/realstock_gate_board_extension.json` ·
`outputs_step10/realstock_campaign/realstock_g10_1_4_nmbe.json` (the 40-cell population, named
in the artefact itself).

---

### 2026-09-03 --- `FINDING 195` / `FINDING 196` recorded; no gate re-opens

A plate-coverage census over the 410 retained IDFs (`tools/4thJ_imp_nocore_void_census.py`) found
six Arm D buildings whose upper storeys carry fewer dwelling zones than the storeys below (15 of 73
Arm D storeys, 997 m² of declared floor area with no zone) and that every manifest's `floor_area_m2`
is `footprint × observed_storeys`, so `eui_heating_kwh_m2` on those six is a lower bound. **No
registered gate scores plate coverage**; `G10.13` (per-zone conservation), `G10.7` (INFO
permanently), `G10.19`–`G10.22` are untouched; the suite stays **18 PASS / 2 FAIL / 1 INFO /
1 OPEN_INHERITED / 2 NOT_EVALUABLE**; `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45`
unchanged. The check was seen felling on edge and interior removals (0.398 / 0.400) and its
convex-hull variant was seen **not** felling on the edge removal (demoted). Details: the Step 10
main-doc entry of the same date and `IMP/docs/2026-09-03_nocore-pipeline-review-improvements.md` §2.

---

### 2026-09-03 (`D-IMP-4`) --- this gate board becomes campaign `C1`'s; the no-core suite is `G10N.x`, not `G12.x`; nothing re-scored

Step 10 now declares **two campaigns** and the pipeline **ends at Step 11**. The author ruled
*"no need new step … i want clean process"*, so the no-core campaign filed this morning as
`Step12_docs/` (under `D-IMP-2`(a)) is re-homed as **Step 10 campaign `C2`** and `Step12_docs/`
no longer exists. Docket:
`IMP/docs/DONE/2026-09-03_D-IMP-4_no-step-12-fold-into-step-10.md`.

* **This board is `C1`'s** — the core-era engine, 410 retained cells. It stays exactly as scored:
  **18 PASS / 2 FAIL / 1 INFO / 1 OPEN_INHERITED / 2 NOT_EVALUABLE**, `G10.1`–`G10.4` on 40 paired
  cells (`es` 30 / `it` 10 / `uk` 0), the two FAILs still "a field was never written" on 0 of 410
  and still never retrofitted, `G10.15` still OPEN_INHERITED, `G10.19` still
  NOT_EVALUABLE_FAIL_BY_POPULATION, `G10.23` still NOT_EVALUABLE_VACUOUS. 🔴 **No gate was
  re-scored, re-banded, re-opened or retracted by `D-IMP-4`** — it moved documents, not verdicts.
* **`C2`'s board is `../4thJ_10_nocoreRealStock_val.md`**, gate series **`G10N.x`** (formerly
  `G12.x`), vacuity guards **`V10N.x`** (formerly `V12.x`), every row still carrying its stated
  inheritance from the `G10.x` row above. Renaming a gate does not re-measure it: the four
  scratch perturbations recorded on 2026-09-03 (manifest blank-field 15 of 15, replicate
  tolerance, binding-rule collision, wrong-fold) keep their verdicts verbatim under the new IDs.
* **The gate-ID separation is what the Step 12 number was carrying** (`Overview.md:683`: two
  documents claiming one ID on two bases is how a basis change hides as a fix). `G10.x` stays
  spent on `C1`'s basis; `G10N.x` is a different namespace on the no-core basis. A step number
  was never needed for that, so there is none.
* **Reporting.** `C1` is retained as the **method and reproducibility record and is not
  reported**. This is a reporting decision, not a re-scoring: `G10.7` was INFO permanently,
  `FINDING 196` made the six Arm D EUIs lower bounds, and no stock-level Arm D EUI was ever
  quotable, so no quotable number is lost.
* **Guard re-verified, not assumed.** `tools/4thJ_step12_preflight.py` →
  `tools/4thJ_step10_nocore_preflight.py`, logic unchanged, re-run under the new name on the same
  410 `C1` manifests: `checked=410 failed=410`, **exit 1**, engine digest `316fe7a6…150b`
  identical to this morning's measurement — **still SEEN FAILING**, not vacuously passing under a
  new filename (`impl/2026-09-03_preflight-seen-failing.md`, second section).

⚪ **Location.** This document moved to `Step10_docs/archive_C1_core_era/` (archived, **not
deleted** — author's own follow-up). `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` was never
opened. No EnergyPlus, no cell, no compute. See `Step10_docs/README.md` for the path redirect.
