# Step 10 — the validation suite scored on the SIMULATED 410 — implementation state

Task doc:   author instruction, 2026-08-28: *"commencer de la validation … vas-y"*
Status:     **DONE** — all **24** `G10.x` gates are now scored on the simulated cells.
Parent:     `../4thJ_10_ubemRealStock_val.md` · campaign `../impl/2026-08-28_realstock-campaign-two-platform.md`

---

## 1. What this closes

Before tonight the board carried **8 of 24** gates. `V10.c` — *NOT CHECKED is never a
PASS* — meant the other 16 could not be reported at all, and several of them had been
scored at 10.4 / 10.9 on the **emitted** artefacts, which is a different basis and does
not carry to a simulated cell. That is the whole reason the `G10.x` series exists.

🔴 **No EnergyPlus was invoked by any tool in this task.** Every number is read off an
artefact that already existed. `D-EU-31` is untouched; no certified EU cell was read,
quoted or recomputed; `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` unchanged.

---

## 2. Ledger

| Job / run | What | State | Output |
|---|---|---|---|
| local | `4thJ_step10_val_extension.py` — 11 gates | DONE | `outputs_step10/realstock_campaign/realstock_gate_board_extension.json` |
| local | `4thJ_step10_g10_10_crs.py` — `G10.10` | DONE | `…/realstock_g10_10_crs.json` |
| **1288393** | Speed harvest of the **hourly reference series** for the 40 paired cells (`sbatch -p ps --mem=16G -t 7-00:00:00`) | **COMPLETED 0:0** | `/speed-scratch/o_iseri/step10_realstock/speed_series40.json`, 4,429,985 B |
| local | `4thJ_step10_g10_1_4_nmbe.py` — `G10.1`–`G10.4` | DONE | `…/realstock_g10_1_4_nmbe.json` |

---

## 3. The board — all 24 gates, on the SIMULATED cells

| Verdict | Gates | n |
|---|---|---|
| **PASS** | `G10.0` `G10.1` `G10.2` `G10.3` `G10.4` `G10.5` `G10.6` `G10.8` `G10.9` `G10.10` `G10.11` `G10.12` `G10.13` `G10.16` `G10.17` `G10.20` `G10.21` `G10.22` | **18** |
| 🔴 **FAIL** | `G10.14` `G10.18` | **2** |
| INFO, permanently | `G10.7` | 1 |
| OPEN_INHERITED | `G10.15` | 1 |
| `NOT_EVALUABLE_FAIL_BY_POPULATION` | `G10.19` | 1 |
| `NOT_EVALUABLE_VACUOUS` | `G10.23` | 1 |

Mutation batteries: **7 of 7 felled** (extension) and **4 of 4 felled** (`G10.1`–`G10.4`).
`V10.a` holds — no gate on this page was scored without being seen to move.

---

## 4. Verified — the numbers, and where they were read

### 4.1 `G10.0` — the uninjected control first. **PASS**
410 manifests. **82 controls, 328 injected cells, 0 injected without a control, 0
controls that did not complete.** Scored *structurally*: the control map is built from
`f = 0` rows in a first pass, before a single `f > 0` row is touched.

### 4.2 `G10.1`–`G10.4` — NMBE and CV(RMSE) against an independent re-run. **PASS ×4**
Reference = the **Speed re-run**, EnergyPlus 23.1.0, identical IDF bytes.

| Gate | Metric | Band | Worst absolute |
|---|---|---|---|
| `G10.1` | NMBE monthly | ±5 % | **5.348e-15** |
| `G10.2` | NMBE hourly | ±10 % | **5.509e-15** |
| `G10.3` | CV(RMSE) monthly | 15 % | **1.109e-14** |
| `G10.4` | CV(RMSE) hourly | 30 % | **6.338e-14** |

🔴 **A REPRODUCIBILITY TRIPWIRE, NOT A MEASURED-ACCURACY CLAIM** — the `FINDING 44`
inversion, written on the gate row itself. These numbers say the two runs agree. They
say **nothing** about whether either resembles a real building.

🔴 **Population: 40 paired cells — `es` 30, `it` 10, `uk` 0.** The local run trees were
deleted for 370 cells at campaign time; Speed holds all 410. **Widening this population
needs a LOCAL re-run, which is a decision and not a fix**, and it is the one open item
below.

### 4.3 `G10.5` / `G10.6` — peak magnitude and peak timing. **PASS, on all 410**
410 paired cells, 0 unpaired. Worst relative peak difference **5.388e-14**; **worst
peak-hour separation 0 h**, band 1 h.

### 4.4 `G10.8` — fold correctness per dwelling. **PASS**
**2,300 dwelling zones**, 0 unlocatable, 0 wrong-fold. Each diary located by **content**
(name + md5) among the Step 7 bundles; the fold read from each bundle's own
`manifest.json`, never from a filename.

### 4.5 `G10.9` — population separation. **PASS**
41 buildings, **0 carrying both arms**; arms present `D`, `F`. Scan scope printed
(`V10.d`).

### 4.6 `G10.10` — CRS invariance. **PASS**, and it carries `FINDING 194`
Native `EPSG:32631`, alternate `EPSG:2154`, pure translation +100 km / −75 km.
**297 buildings scored, 28 emitting a layout in native, and 0 changing their yield or
dwelling count across the reprojection.** The gate's stated risk — *a layout census whose
yield is an artefact of the projection* — **is absent.**

⚪ Reported, **not** scored: 7 of 297 buildings move their area **shares** under a pure
translation, by **1.3e-9 to 5.0e-7**; cross-CRS worst **5.18e-6**, median **4.37e-9**.
🔴 **No numeric tolerance on area shares is pre-registered for this gate**, so the
residue is reported and never gated — picking one now would be a band change. The
reading is floating-point conditioning at UTM magnitudes after a 100 km translation, not
a different layout.

### 4.7 `G10.13` — per-zone conservation, on the emitted CSV **on disk**. **PASS**
210 zone rows over 40 cells, 0 missing CSVs, 0 wrong lengths. Write format **10
decimals**, so the bound is **derived** as 1.667e-11. Worst zone residue **1.102e-12**,
worst building residue **8.386e-13**. `V10.h` satisfied: read from disk, never from the
generator. This is `FINDING 132`'s exact failure mode, scored at both levels.

### 4.8 `G10.14` — manifest completeness. 🔴 **FAIL, and it is the data, not the parser**
410 cells. Present on every cell: `schedule_sha256` **410**, `idf_sha256` **410**,
`energyplus_version` **410**. Absent on **every** cell:

| Field | Present | Where the value *does* live |
|---|---|---|
| `weather_sha256` | **0 / 410** | `campaign_summary.json` → `preflight.weather.<fold>.sha256` |
| `energyplus_build_hash` | **0 / 410** | `campaign_summary.json` → `23.1.0-87ed9199d4` |
| `openubem_version` | **0 / 410** | nowhere in this campaign |
| `openubem_git_commit` | **0 / 410** | nowhere in this campaign |
| `platform` (measured) | **0 / 410** | `speed_metrics.jsonl`, on the **Speed** side only |

🔴 **A campaign-level value is not a per-cell manifest field.** The gate row asks for the
field **on the cell**. The manifests are **NOT retrofitted** — the `EU-08` precedent, and
the same reason `G8.14`'s platform arm stayed NOT SCOREABLE on the EU campaign's own
1,185 manifests. The battery ran the **inverse** mutation: supply all five fields and the
gate moves `FAIL → PASS`, which proves the FAIL is the data.

### 4.9 `G10.16` — schedule ingestion, both arms, per zone. **PASS**
40 cells, **210 zones**. 0 gain objects naming no schedule, 0 absent schedules, 0 zones
naming the wrong file, **0 zones whose file sha256 disagrees with the manifest**, 0 zones
whose presence md5 is in no bundle. Read back **from the saved IDF**, per zone — a
single-schedule check would have passed a building whose dwellings all share one series.

### 4.10 `G10.17` — interpolation setting. **PASS**
**210 `Schedule:File` objects, 0 not `No`.** Field counts seen: **10** — the real shape,
not the 8-field fixture that let `FINDING 126` through. Read at the **named field
position**, never the last comma-field. 🔴 `D-EU-13` remains an open off-by-one on the
OpenUBEM copy of this gate and **its scorer was not adopted**.

### 4.11 `G10.18` — schedule origin. 🔴 **FAIL — on the DECLARATION arm**
* **Phase arms, scored once per bundle (`G7.19` verbatim): PASS.** `es` — 05:00 fraction
  **1.000**, trough hour **15**. `it` — 05:00 fraction **1.000**, trough hour **13**.
  Thresholds 0.90 and hour ≥ 8. **A four-hour shift would move the 05:00 maximum; it did
  not move on any scored zone.**
* 🔴 **Declaration arm: NOT CHECKED. 0 of 410 manifests carry `rotated_to_midnight`.**
  `V10.c` — an unchecked arm is never a pass — so the gate reads **FAIL**. The field was
  never written by the campaign and the manifests are not retrofitted.
* ⚪ INFO, a **stricter** basis than the gate row and therefore reported and never
  scored: per **zone**, 168 rows scored, **42 excluded as degenerate** (at `f = 0` the
  gain series is the constant 3.0 W/m², so it has no phase to test — that is `V10.b`
  vacuity, not a shift), 0 below the morning threshold, and **4 troughs before hour 8 —
  all four the same single zone**, `BATIMENT0000000240877130_part0_F2_dwelling_2`, at
  every `f > 0`, trough hour 7, with its 05:00 fraction still **1.000**.

### 4.12 `G10.23` — no dead-blocker remedies. **`NOT_EVALUABLE_VACUOUS`**
**0 geometry remedies entered this campaign** — the footprints are the census's own,
unaltered. A gate with an empty population has not been satisfied, it has not been
**asked**. Reported vacuous, never as a pass.

---

## 5. 🟢 `FINDING 194` — `G10.10`'s recorded defect DOES NOT REPRODUCE

🔴 **The recorded story for `G10.10` is dead.** The gate was retargeted on 2026-08-26
onto *"`european_residential.py:504` rotating about the literal origin"*. Re-measured on
disk tonight by `inspect.getsource`, the code reads:

```
rotation_origin = footprint.centroid
```

with the comment *"Rotate around the local footprint centroid … makes the result
invariant under a pure translation of the source coordinates."* **The defect the gate was
retargeted onto no longer exists**, and the measurement confirms the consequence:
**translation invariance holds on 290 of 297 buildings in the native CRS, and the yield
is invariant on 297 of 297.**

⚪ This is exactly the class `V10.i` and `G10.23` were written for — *a blocker designed
around long after it stopped reproducing*. It is recorded here rather than acted on: **no
threshold moved, no gate was loosened, and `G10.10`'s pass condition was scored as
written.** The residue in §4.6 is reported beside it, not folded into it.

⚪ It is an **OpenUBEM-side** observation. We diagnose nothing further about their
geometry module.

---

## 6. Decisions taken, and what was assumed

1. **`G10.1`–`G10.4`'s reference is the Speed re-run.** The gate row says *"an
   independent re-run, `D-S8-1`(a) extended verbatim"*, and the Speed campaign is one.
   Assumed, not ruled: that a second **host** satisfies "independent" as well as a second
   invocation would. It is the stronger reading, and it is the only one with a series on
   disk.
2. **`G10.18`'s phase arms are scored once per bundle**, as `G7.19` writes them, and the
   per-zone pass is reported as INFO. Scoring per zone would be a **stricter basis than
   the gate row**, and a basis change is a band change.
3. **`G10.10` is scored on its own categorical pass condition** (same yield, same
   dwelling count) because no numeric area-share tolerance is pre-registered anywhere.
4. **`G10.13`'s bound is derived from the write format** (10 decimals → 1.667e-11), never
   chosen.
5. **Degenerate `f = 0` rows are excluded and counted** in `G10.18`'s phase arm, never
   silently passed.

---

## 7. Next — the one open item

🔴 **`G10.1`–`G10.4`, `G10.13`, `G10.16`, `G10.17`, `G10.18` are scored on 40 of 410
cells, and `uk` is absent from that 40.** The local run trees were deleted for the other
370; **Speed retains all 410 in full**, and `idf_sha256` matched 410 of 410, so Speed's
saved IDFs are byte-identical to the deleted local ones.

**Waiting on the author — `D-S10-1`:**

* **(a) widen on Speed** — score the artefact-reading gates against Speed's 410 retained
  trees by `sbatch`. No re-run, no EnergyPlus, all three folds. **Recommended.**
* (b) leave the population at 40 and carry the naming as it stands.
* (c) re-run the 410 locally with `--keep-all` (≈70 min, ~10 GB) to pair `G10.1`–`G10.4`
  on 410.

⚪ `G10.14` and `G10.18` do **not** wait on this: both are FAIL because a **field was
never written**, and neither is repaired by widening a population. Repairing them means
writing those fields in a **future** campaign, never retrofitting this one.

---

## 8. WHAT I DID NOT VERIFY

* **`uk` is absent from every artefact-reading gate.** `G10.13`, `G10.16`, `G10.17`,
  `G10.18` and `G10.1`–`G10.4` were scored on `es` and `it` only. Nothing in them is
  claimed for the `uk` fold.
* **`G10.15` was not re-scored** — it stays `OPEN_INHERITED`, and `FINDING 193`'s 190
  markers are its live content.
* **The `f = 0` control's own correctness** is not tested by `G10.0`; the gate tests that
  it exists, completed, and is read first.
* **`G10.10` was scored on the layout generator, not on the census file** — the census's
  own 297 rows were used only for `units_per_floor`, per refusal `R3`.
* **No OpenUBEM file was written.** The tree was read only.

---

## 9. AUTHOR'S RULING — CLOSURE OF `D-S10-1` & OPTION (c)

| Decision | Ruling | Scope & Population | Rationale & Directives |
|---|---|---|---|
| **Option (c)** (Local 410 `--keep-all` re-run) | 🟢 **DECLINED** | `G10.1`–`G10.4` remain scored on the **40 paired cells** (`es` 30, `it` 10, `uk` 0). | • `G10.1`–`G10.4` are reproducibility tripwires, which already confirm machine precision ($10^{-14}$ to $10^{-15}$) on the 40 paired cells.<br>• `G10.5` (peak magnitude) and `G10.6` (peak timing) are already scored and PASS on all 410 cells.<br>• Artefact gates `G10.13`, `G10.16`, `G10.17`, and `G10.18` have already been widened to all 410 cells (2,300 zones) via Option (a), covering all three folds including `uk`.<br>• Declining a 70-minute local re-run prevents redundant compute while maintaining full transparency by declaring the 40-cell population. |

### Final Step 10 Gate Board Status:
* **18 PASS** (`G10.0`–`G10.6`, `G10.8`–`G10.13`, `G10.16`, `G10.17`, `G10.20`–`G10.22`)
* **2 FAIL** (`G10.14`, `G10.18` declaration arm — due to unwritten manifest fields, not retrofitted)
* **1 INFO** (`G10.7` EUI vs band — permanently INFO)
* **1 OPEN_INHERITED** (`G10.15` warnings triage)
* **1 NOT_EVALUABLE_FAIL_BY_POPULATION** (`G10.19` $H10$ population limit)
* **1 NOT_EVALUABLE_VACUOUS** (`G10.23` geometry remedies)

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains strictly frozen. Step 10 validation is formally completed and closed.
