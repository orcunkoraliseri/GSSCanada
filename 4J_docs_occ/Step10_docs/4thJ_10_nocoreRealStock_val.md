# Step 10 — campaign `C2`: no-core real-stock UBEM simulation. Validation.

### 4J HETUS LLM pipeline. Validation specification.
#### Implementation: `4thJ_10_nocoreRealStock.md`. Campaign `C1` (core-era, closed): `archive_C1_core_era/4thJ_10_ubemRealStock_val.md`. Parent: `../4thJ_00_HETUS_LLM_Pipeline.md`.

---

## STATUS

⚪ **PRE-REGISTERED, 2026-09-03. Nothing scored — no cell exists.** Every threshold below is
registered before any Step 10 `C2` cell exists, exactly as campaign `C1`'s own gate table was.
🔴 **A threshold registered here is not moved to make a gate pass.**

🟢 **Re-homed 2026-09-03 under `D-IMP-4`.** Filed first as
`Step12_docs/4thJ_12_nocoreRealStock_val.md`; **there is no Step 12.** This is Step 10's second
campaign, `C2`. Campaign `C1` (core-era, 410 cells) keeps its closed `G10.x` scoring at
`archive_C1_core_era/4thJ_10_ubemRealStock_val.md` and is **not re-opened, not re-scored**.

## 🔴 THE GATE-ID RULE

`G10.x` is already spent on campaign `C1`'s basis (core-era engine, 410 retained cells). Campaign
`C2` opens a **new `G10N.x` series** on the no-core basis. **Inheritance from `G10.x` is stated on
every row**, verbatim, so a reader can see whether a bar moved. No `C2` result is ever filed under
a `G10.x` ID, and no `G10.x` ID is re-scored by `C2`. 🔴 **This is the whole of what the Step 12
number was carrying** (`Overview.md:683`: two documents claiming one ID on two bases is how a basis
change hides as a fix) — the separation lives in the gate namespace, so the pipeline needs no
twelfth step.

---

## THE GATE TABLE

All rows currently read **NOT_EVALUABLE — no campaign `C2` cell exists.** The verdict column is what
each row *will* score once a cell exists; nothing below is a claim about any number.

| Gate | What it catches | Threshold | Inheritance |
|---|---|---|---|
| **`G10N.0`** | Uninjected control first | Same as `G10.0`: `f=0` read before any `f>0` quoted | `G10.0` verbatim |
| **`G10N.1`–`G10N.4`** | NMBE / CV(RMSE), monthly/hourly | ±5% / ±10% / 15% / 30%, same reference clause | `G10.1`–`G10.4` verbatim. **Reproducibility tripwire, not accuracy** |
| **`G10N.5`, `G10N.6`** | Peak magnitude / timing | ±15% / ≤1h | `G10.5`/`G10.6` verbatim |
| **`G10N.7`** | Per-building EUI vs published band | INFO permanently, no band | `G10.7` / `G8.7` verbatim |
| **`G10N.8`** 🔴 Fold correctness | A dwelling driven by the fold that held it out | Per dwelling, content-located (name + md5) | `G10.8` verbatim, extended to the no-core `N_u` |
| **`G10N.9`** | Arm D / Arm F never pooled | 0 buildings carrying both arms | `G10.9` verbatim |
| **`G10N.10`** | CRS / rotation-origin tripwire | Reported, never gated (per `FINDING 194`) | `G10.10`, itself retargeted 2026-08-26 |
| **`G10N.11`** 🔴 France is not a fold | 0 French diaries, 0 `f>0` French cells | `G10.11` verbatim |
| **`G10N.12`** | Weather-basis firewall | No absolute Step-8-basis EUI beside a Step-12-basis EUI | `G10.12` verbatim |
| **`G10N.13`** | Conservation, per zone and per building | `phi_int` annual mean exactly 3.0 W/m² | `G10.13` verbatim |
| **`G10N.14`** 🔴 Manifest completeness | All 15 fields of §5 present on every manifest | 0 blank fields | `G10.14` twin, extended list (I-6). **Perturbation seen felling — see below** |
| **`G10N.15`** | Convergence and warnings | Zero severe; classes triaged by kind | `G10.15`, inherited OPEN as on the OpenUBEM side |
| **`G10N.16`** | Schedule ingestion, both arms, per zone | md5 + assignment arm | `G10.16` verbatim |
| **`G10N.17`** | Arm label survives aggregation | Arm F never silently pooled into an aggregate | `G11.17` / `G10.9` |
| **`G10N.18`** | Declaration arm, `rotated_to_midnight` | Field present and true | `G10.18` twin |
| **`G10N.19`** | `H10` population floor | ≥30 qualifying Arm D buildings per fold | `G10.19`, floor reachable on census arithmetic only (§3.2) |
| **`G10N.20`** 🔴 Binding rule, Case A/B paired | Present within footprint; cross-building `delta_div` refused | `G10.20` verbatim. **Perturbation seen felling — see below** |
| **`G10N.21`** | `CF` and √N fit | Residuals reported; Case A `CF≠1` is a harness defect | `G10.21` verbatim |
| **`G10N.22`** | Arm F is a LOWER BOUND | Direction only, magnitude refused | `G10.22` verbatim, restated §3.2 |
| **`G10N.23`** | Geometry remedy vacuity | 0 remedies entered = `NOT_EVALUABLE_VACUOUS` | `G10.23` verbatim |
| **`G10N.replicate`** 🔴 Re-run tolerance, quotation rule | A named subset re-run `R` times on one host; outside tolerance → barred, never quoted | New, I-7. **Perturbation seen felling — see below** |

## VACUITY GUARDS

* **`V10N.a`** — every gate above prints `NOT_EVALUABLE` with its population named as `0` (no Step
  12 cell exists), never a vacuous PASS.
* **`V10N.b`** — a failing gate's perturbation demonstrates nothing; campaign `C2` inherits nothing
  failing yet because nothing has been scored.
* **`V10N.i`** (`V10.i`'s twin) — a recorded blocker carries the date it was last **measured**, not
  the date it was first written; the preflight guard's engine digest was re-measured 2026-09-03,
  not copied from the review document.

---

## Perturbations seen felling, on scratch fixtures — 2026-09-03

No production tool exists yet (spec only). Each perturbation below is demonstrated on a minimal
scratch fixture built for this check alone, per `feedback_gates_must_be_seen_failing.md`. Script:
`impl/2026-09-03_box5-6_scratch_perturbations.py` (not a shipped tool; deleted after the run is
not required since it makes no claim about any real cell — kept as the record of the check).

### `G10N.14` — blank one field in a scratch manifest

A scratch manifest with all 15 required fields (§5) present scores **0 blank**. Blanking one field
(`weather_sha256 = null`) at a time, for all 15 fields in turn, must each independently fell the
gate. **Result: 15 of 15 single-field blanks felled `G10N.14`; the all-fields-present baseline did
not fell it.** Seen felling.

### `G10N.replicate` — one cell beyond tolerance

A scratch replicate set of `R=5` values, tolerance ±0.5%: four values inside tolerance of their
mean, one value planted 2.0% off. The quotation rule must read the whole subset as **BARRED**, not
average around the outlier. **Result: the 5-value set with the planted outlier reads BARRED; a
control set with all 5 values inside tolerance reads QUOTABLE.** Seen felling.

### `G10N.20` binding rule — two dwellings sharing a series in Case B

A scratch building with `N_u=3` drawn flats, each assigned an independent series by
`gain_sha256`. Two dwellings pointed at the **same** `gain_sha256` (the collision mutation) must
fell the binding gate. **Result: the collision fixture (2 of 3 dwellings sharing one
`gain_sha256`) FAILS; the independent-series baseline (3 distinct `gain_sha256`) PASSES.** Seen
felling.

### Wrong-fold series — the `G10.8` mutation, extended

A scratch dwelling assigned a series whose bundle manifest names a different fold than the
dwelling's own country. Must fell `G10N.8`. **Result: the mismatched-fold fixture FAILS; the
matched-fold baseline PASSES.** Seen felling.

All four checks: baseline clean, mutation fells its target, 0 false positives, 0 no-ops. No real
manifest, cell, or campaign artefact was touched.

---

## PROGRESS LOG

Append-only. Never delete or reformat an existing entry; if a decision changes, edit that entry.
The GATE TABLE above stays the FROZEN pre-registration text (registered 2026-09-03, before any
`C2` cell existed) and is not edited by this entry — the real state lives here, as `G10.x`'s own
val doc already does it.

### 2026-09-16 — 🟢 THE SUITE IS SCORED IN FULL: ALL 24 `G10N.x` GATES (+ `G10N.replicate`), ON THE REAL `C2` CAMPAIGN

Authorisation: `tools/4thJ_step10_nocore_campaign.py`, `AUTHORISED` dict, all three districts,
2026-09-16: *"Score the finished C2 cells for Madrid, London and Bologna as G10N.x results."*
Scorer: `tools/4thJ_step10_nocorereal_score.py` (ported from `4thJ_step10_realstock_score.py` +
`4thJ_step10_val_extension.py`, `C1`'s own two-part `G10.x` scorer). 🔴 **NO ENERGYPLUS WAS
INVOKED, NO CELL WAS RE-RUN.** Every number is read off a manifest or a retained run tree that
already existed. `AUTHORISED`, `D-EU-55` and everything closed about `C1` are untouched.

**Population.** 35,090 real, completed `C2` cells (`es` 11,340 / `uk` 12,070 / `it` 11,680), all
`arm="D"`, all with 0 blank manifest fields — read directly from
`_local_runs/4J_{ES,UK,IT}_local/out/<DISTRICT>/cells/*.json` (the actual finished campaign; the
1,427-cell snapshot at `Step10_docs/outputs_step10_nocore/` is an early, incomplete Bologna-only
subset and was NOT used). A second, much smaller population — 417 `runs/<district>/<slug>/`
directories that still carry a saved `.idf` plus per-zone gain CSVs, the campaign's own
`RETAIN_RUN_DIRS` policy, the same kind of subset `C1` scored its own `G10.13`/`16`/`17` on — backs
`G10N.13`, `G10N.16`, `G10N.17`.

| Verdict | Gates | n |
|---|---|---|
| **PASS** | `G10N.0` `G10N.8` `G10N.9` `G10N.11` `G10N.12` `G10N.13` `G10N.14` `G10N.16` `G10N.17` `G10N.18` `G10N.19` `G10N.21` | **12** |
| 🔴 **FAIL** | `G10N.20` | **1** |
| INFO, permanently | `G10N.7` | 1 |
| OPEN_INHERITED | `G10N.15` | 1 |
| `NOT_EVALUABLE` (population 0) | `G10N.1` `G10N.2` `G10N.3` `G10N.4` `G10N.5` `G10N.6` `G10N.10` `G10N.22` `G10N.replicate` | **9** |
| `NOT_EVALUABLE_VACUOUS` | `G10N.23` | 1 |

Mutation battery: **11 of 11 felled**, covering `G10N.0`, `G10N.8` (two clauses), `G10N.9`,
`G10N.11`, `G10N.12`, `G10N.14`, `G10N.18`, `G10N.19` (the inverse mutation — capping the qualifying
population back under 30), `G10N.20` (the inverse mutation — de-duplicating the real collisions and
confirming the gate can also PASS), and `G10N.21`(i). `V10N.a`: no gate here is only capable of one
verdict.

**Nine gates are `NOT_EVALUABLE` because their reference population is genuinely zero, not because
this scorer declined to look:**
* `G10N.1`–`G10N.6` need an independent second-host re-run of the FINAL population. The Speed
  campaigns (jobs `1314969`/`1314970`/`1315014`/`1315015`) were cancelled 2026-09-08 (Defect 8) and
  never restarted; the floor-averaging and courtyard fixes that produced the cells scored here ran
  **only on the local Windows host** afterward (`impl/2026-09-12_C2_campaign_dashboard_final.html`:
  *"Speed cluster stays frozen and ignored — all numbers here are from local runs only"*). No
  matching reference run exists to pair against.
* `G10N.10` needs the OpenUBEM geometry tree to re-measure the CRS invariance (`V10N.i`); that tree
  is not present in this checkout.
* `G10N.22` (Arm F): the executed campaign never simulated a single Arm F cell — 100% of the 35,090
  manifests are `arm="D"`. Arm F's own projected population (75/12/175 buildings per the
  2026-09-08 census) never reached a `build_cells()` row.
* `G10N.replicate`: section 6 states compute was never authorised for it; none was run.

**Two results are worth the author's attention.**

🟢 **`G10N.19` PASSES, unlike `C1`'s own `G10.19`.** Qualifying Arm D buildings (Case B, completed,
≥2 REAL distinct diaries, floor-averaged buildings excluded) measure **es 845 / uk 157 / it 1070**,
all clear of the pre-registered 30-per-fold floor by a wide margin — `C1` measured es 9 / uk 5 / it 3
and was ruled FAIL-by-population in writing (`Q1(a)`, 2026-08-28). The threshold was not moved; the
no-core population is simply larger. `H10`'s `CF(N_u)` fit is therefore REPORTED, not just INFO, per
fold at `f > 0` — see `g10n_h10_report.json`.

🔴 **`G10N.20` FAILS on REAL data, not only a scratch mutation.** Within 320 real Case B, `f > 0`
cells (`uk` 120 / `it` 200 / `es` 0), at least two dwellings that hold DIFFERENT, real Step 7
diaries (distinct `presence_md5`, confirmed 0 `presence_md5` collisions anywhere) produced a
BYTE-IDENTICAL emitted `gain_sha256`. Example: `uk__way/1057529442__caseB__f015` — three distinct
household diaries (`presence_HH_uk_20020211.csv`, `presence_HH_uk_19230310.csv`,
`presence_HH_uk_18061006.csv`) all hash to `61b273a57f…` after the injection formula. The raw gain
CSVs for this building are no longer on disk (not a retained building), so the mechanism is not
diagnosed here — reported as a measured fact, not a guess, and left for engineering follow-up. This
is exactly the failure mode `G10N.20`'s own scratch perturbation demonstrated on a fixture
("two dwellings pointed at the same gain_sha256… must fell the binding gate"), now seen on real
cells. Pairing itself (Case A/B present, geometry/basis fields matching) is clean: 17,545 of 17,545
pairs, 0 missing, 0 mismatched.

🔴 **`G10N.21` clause (ii) — AN AMBIGUITY FLAGGED, NOT RESOLVED.** The frozen row above reads *"Case A
CF≠1 is a harness defect | G10.21 verbatim"*, with no real-stock exception written on the `C2` row
itself. `C1`'s own scorer (`4thJ_step10_realstock_score.py::gate_g10_21`) carved this exact clause
out as `CARRIED, NOT SCORED ON SIMULATED POWER`, because on simulated power the zones sharing one
synchronised diary still differ in envelope area, orientation and solar exposure — physics, not a
harness defect. This file PORTS that carve-out rather than literal-scoring it, and measures real,
non-trivial deviations doing so: 1,917 of 17,545 Case A cells have `CF ≠ 1` beyond `1e-9`, worst
deviation **0.0238** (es/uk/it mixed). **If the author intends the `C2` row to be read literally
(no carve-out), `G10N.21` becomes FAIL on this clause, on all three folds.** Not decided here.

⚪ **One methodology note, not a threshold move.** `G10N.13`'s tolerance, ported from `C1`
(`0.5 × 10^-decimals / 3.0`, decimals read off the write format), assumed a FIXED-width decimal
write. Measured on `C2`'s own retained files, the write format is variable (0 to 12 decimals seen
on the same population, e.g. `"3"`, `"2.1"`, `"2.98863381429"`), so `C1`'s formula would derive an
artificially loose bound (~1.7%) dominated by the shortest value. A fixed `1e-6` relative bound is
used instead; it does not decide the verdict — the actual worst measured residues (`1.43e-12` per
zone, `1.26e-12` per building) are five to six orders of magnitude inside either bound.

**Outputs:** `Step10_docs/outputs_step10_nocore/g10n_gate_board.json` (full per-gate detail),
`g10n_h10_report.json` (the `H10` fit per fold), `g10n_g8_failing_rows.json` (empty — `G10N.8`
PASSED). Scorer: `tools/4thJ_step10_nocorereal_score.py`. Backup of this file before this entry:
`archive/backups_g10n_scoring_20260916/4thJ_10_nocoreRealStock_val.md.bak_pre_g10n_scoring`.

⚪ **Owed to the author: two decisions, neither compute.** (1) whether `G10N.21`(ii) inherits `C1`'s
real-stock carve-out or is read literally; (2) whether `G10N.20`'s 320 real collision cells need an
engineering fix before any `H10` number drawing on those specific buildings is quoted (the `H10`
fit itself excludes floor-averaged buildings already but does NOT currently exclude the 320
collision cells — they are Case B cells with a real, if suspicious, `cf` value, and this entry does
not decide whether that value is trustworthy).

---

## Author ruling on the two owed decisions (2026-09-17)

Both decisions above are now made, given together with the Figure 1 cards 10/11 closure:

1. **`G10N.21` clause (ii): the `C1` real-stock carve-out is KEPT.** The scorer's ported behavior
   (`CARRIED, NOT SCORED ON SIMULATED POWER` for zones sharing one synchronised diary but differing
   in envelope/orientation/solar exposure) is confirmed correct and final. `G10N.21` is not
   re-scored literally; the 1,917 Case A cells with `CF ≠ 1` remain outside this clause's FAIL
   condition, as physics, not a harness defect.
2. **`G10N.20`'s 320 collision cells are EXCLUDED from any number quoted in the manuscript**, until
   the underlying diary-collision mechanism gets an engineering fix. Any `H10` fit, count, or figure
   drawn from `C2` that could include these 320 UK/Italy cells must state the exclusion explicitly
   or be recomputed to leave them out; none currently exist in the manuscript (checked 2026-09-17,
   no `C2`/`G10N` numbers are quoted anywhere in `writing/submission/4J_manuscript_submission.md`),
   so this is a forward-looking rule, not a correction to existing text.

Figure 1 cards 10 and 11 are closed (`open` → `validated`) on the strength of this same real score;
see `writing/submission/figures/Prompts_Images/4thJ_pipeline_steps_figure.md`'s 2026-09-17 banner.
