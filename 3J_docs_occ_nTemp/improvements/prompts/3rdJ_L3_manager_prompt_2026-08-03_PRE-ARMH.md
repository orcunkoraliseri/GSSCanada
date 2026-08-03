# Manager prompt — 3J Leg-3 Step 9, **2026-08-03** (written at the end of the 2026-08-02 evening session)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **Replaces `3rdJ_L3_manager_prompt_2026-08-02.md`.** Everything that file was waiting on is now
> done: FINDING 7 fixed, FINDING 8 fixed *and confirmed at the energy level*, decisions D-A/D-B
> answered and executed. A new defect (FINDING 9) was found by the FINDING 8 smoke test, fixed, and
> smoke-tested in the same session. The predecessor stays beside this file.

---

You are the manager on the 3J Leg-3 four-channel mixed-use tower BEM pipeline. Work in
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

## Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node
  (`speed-submit2`). ALWAYS `sbatch`.** Flagged three times; one more is account suspension.
  Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`. `tar`, `find`, `python` are
  **not** allowed there. The login shell is **tcsh** — no `for` loops, no `2>&1`, one short line.
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, even for one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
  explicit `N/A`. A gate counts as validation only once it has been *seen failing*; write the
  falsifiable prediction **before** running the test. **A miss is recorded, not repaired.**
- 🔴 **Vacuous tests are the recurring failure on this project — now NINE kinds.** Before recording
  any PASS, ask: *what result would have made this fail?* The newest one is the most general:
  - **#9 — the gate whose REFERENCE is derived from the same source it audits.** Fixing FINDING 9
    I wrote check **D8** (per-day-type volume ratio == `r(class)/R`). It passed. Re-creating the
    defect *in the reader* left D8 at **0 violations**, because the corrupted Saturday was
    simultaneously its reference and its target. Replaced by **D9**, which reads the **saved IDF**
    so neither side is a number the transform reported about itself. Ask of every gate: *could the
    thing being checked and the thing checking it be wrong together?*
  - Related method note: my first falsification patched the READER and both gates stayed silent —
    which nearly read as "the gates are useless" when the defect had actually lived in the WRITER.
    Perturb the layer the defect occupied; a falsification that misses tells you about your harness
    before it tells you about your gate.
- **A local `py_compile` is NOT a valid syntax check for cluster code.** Local Python is **3.13**
  (PEP 701), the cluster env is **3.10**. A multi-line f-string cost a full simulation round trip on
  2026-08-02. Compile inside the job, under `$PY`, and refuse to run if it fails.
- **Do not append to the Progress Log with PowerShell `Add-Content`.** PS 5.1 `Get-Content` reads a
  UTF-8 file as ANSI and double-encodes the whole insert. Append with bash `cat >>` / heredoc.
- **Verify every number you inherit.** Re-derive from the artefact's own columns.
- **Update the Progress Log live** — same response as each state change, not batched. The live doc
  is `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md` (**~4,700 lines**). Read the
  last ~600 before acting.
- **Leg-2 is closed and paper-ready — no file under `Leg2_2-split/` may be modified.** Reading its
  IDFs and `eplusout.sql` is fine.
- All documents in English; reply to the user in English even though they write French. Keep
  replies short and bulleted.
- Cheap models for mechanical work; minimum monitoring interval 30 min; never poll in a loop.

---

## 1. What changed on 2026-08-02 evening

Injector `eSim_bem_utils/commercial_integration.py`: md5 `56d6e324` → **`233932d7`** (2,970 lines).
Unit suite `eSim_tests/test_t9_13.py`: 40/40 → **58/58**.

### ✅ FINDING 8 — cache-key collision — FIXED AND CONFIRMED AT THE ENERGY LEVEL

`_t9_13_schedule_for` was keyed on `(channel, r_wd, r_we)`, and `r` is channel-wide, so **every**
`WaterUse:Equipment` object in a channel collapsed onto whichever prototype the loop reached first.
The source schedule is now in the key and in the generated name.

Smoke `Y2022__Tall__MTL` vs `Default_NECB__Tall__MTL` (job 1171438, scored 1171442):
- **the discriminating case passed** — all 8 `F31-F37 HOTEL_MID_*_GUESTRM` went ×1.136 → **×1.000**
  (worst deviation 0.0000); main `LAUNDRY` ×3.028 → **×1.000**.
- hotel channel 1 → **4** derived DHWv2 schedules; 33 distinct names (Hotel 4 / Office 1 /
  Residential 27 / Retail 1). Office and retail stay at 1 because each genuinely has one prototype.
- **measured, not assumed:** 27 residential objects, 27 distinct `(Space, prototype)` pairs → 1:1,
  that path was never colliding. Fixed anyway.
- new check **D7** reads the SAVED IDF (never `dhw_applied`, which records the cached name and would
  inherit the blindness). Seen failing on FINDING 8's exact signature.
- the arm-E provenance for the same cell has **zero** `t9_13_derived_name` lines and no D7 — which
  is exactly why the collision ran 112 cells undetected.

### ✅ FINDING 7 — 2030 retail built from the uncalibrated pool — FIXED (option B)

`build_retail_product_2030` now reads the calibrated `_C_v2` (md5 `5aa74f44…`). **21/21**
pre-registered checks PASS: QC weekday peak **11 h → 16 h**, Sat/weekday contrast 0.98 → 3.38, peak
multipliers bit-stable at 0.8550 / 0.9215 / 0.9975.
🔴 **The task prompt's PR coding was wrong** — `_C_v2` carries raw GSS province codes **24/48**, not
the 2022 stock's 2/4 remap. Measured with `value_counts`; 2/4 would have selected nothing.

### ✅ FINDING 9 — NEW, found by the FINDING 8 smoke — FIXED AND CONFIRMED (§2)

The FINDING 8 smoke left 7 objects off the no-op requirement. Attribution (job 1171443) showed
**3 of them were objects the fix provably never touched** (d = 1.0000), and a schedule-only
predictor (job 1171445) explained them from the schedules alone, matching the simulated energy to
three decimals:

> `_week_profiles` took the weekend profile as `sun or sat` and the writer stamped that single
> curve onto `For: Weekends Holidays AllOtherDays`. **Any prototype whose Saturday and Sunday differ
> lost volume — even at r = 1.000, where T9-13 is specified to be an exact no-op.**
> RetailStandalone **0.9234**, OfficeLarge **0.9524**, HotelLarge BLDG **0.9953**.
> Pre-existing in every DHW arm run to date (arms A–E all carry it).

Fixed by keeping all 8 day types distinct on the way in (`by_daytype`) and on the way out
(`_build_compact_fields_by_daytype`, one block per DISTINCT profile). `wd`/`we` keep their exact
former meaning, so nothing outside T9-13 moves. All three prototypes now predict **1.0000**, and the
simulation confirmed it (§2). New gate **D9** was seen failing on the real tower, on exactly the 6
pre-registered objects, before it was believed.

🔴 **Consequence for arms A–E: they all carry FINDING 9.** The correction is a level shift on DHW
wherever `--dhw-model volume_scaled` ran — retail **+7.7 %**, office **+4.8 %**, hotel
`BLDG_SWH_SCH` objects **+0.5 %**; guest rooms and laundries unaffected. Arm E's scorecard has NOT
been re-issued; that is a user decision (§4.4).

---

## 2. ✅ The FINDING 9 smoke landed — job **1171449**, **10 PASS / 0 FAIL**

`COMPLETED 00:41:48`, exit 0. Arm G `out_G_f9fix/campaign_233932d7` vs arm F
`out_F_f8fix/campaign_456301f5`, each over its own `Default_NECB`. Predictions were hard-coded in
`Step9_docs/3rdJ_09G_score_f9.py` and uploaded before the cells ran; none was altered.

| object | arm F | required | arm G |
|---|---|---|---|
| `F1`/`F2 RETAIL_*_BACKSPACE` | 0.923 | 1.000 | **1.000** |
| `F3-F11`/`F12-F20 OFFICE_RESTROOM` | 0.952 | 1.000 | **1.000** |
| `BOOSTER` | 0.995 | 1.000 | **1.000** |
| `F38 HOTEL_TOP_KITCHEN` | 0.995 | 1.000 | **1.000** |
| `F30 HOTEL_BOT_LAUNDRY` | 1.019 | **stays 1.019** | **1.019** |
| `LAUNDRY`, 12 guest rooms | 1.000 | 1.000 | 1.000 (worst dev 0.0000) |
| 27 residential | — | unchanged | worst \|G−F\| 0.0000 |
| any other object moving | — | none | 0 moved |

Audit `PASS`, 47 objects, `counts={D1..D6:0, D7:0, D8:0, D9:0}`, `d9_unchecked=0`, no
`t9_13_daytype_FALLBACK` line. Control cell still `N/A`.

**The discriminating prediction held.** `F30` was required to stay at 1.019 because its prototype
has Saturday == Sunday, so FINDING 9 never touched it — and it did, to three decimals. The FINDING 8
attribution of that 1.9 % therefore stands, and F30 remains a separate open item (§4.1).

**FINDING 9 is closed.** The next thing is the campaign decision, §3.

---

## 3. 🔴 THE ONE DECISION WAITING FOR THE USER — the campaign cell count

Nothing has been launched. The user has said this is their call and it is still open.

Context they need in order to decide:
- The full matrix is **56 cells** (2 buildings × 2 cities × 14 scenarios); two arms would be 112.
- The **2030-family office channel is stale** in 36 of 56 cells (the FINDING 6 re-issue,
  `office_presence_multiplier_2030.csv` md5 `575d17e5`), and the **2030 retail channel is stale in
  the same 36** after the FINDING 7 rewire. Y2022 and the three historical years are untouched.
- **FINDING 9 changes DHW in EVERY cell that runs `--dhw-model volume_scaled`**, not only the 2030
  family: retail DHW +7.7 %, office +4.8 %, hotel BLDG +0.5 % against arms A–E.
- So "re-run only the stale 2030 cells" is **no longer sufficient** if DHW is in scope. Either
  re-run all 56 with `volume_scaled`, or run without DHW and keep arm C as the DHW-free product.

Put those four bullets to the user and let them pick the scope. **Do not infer it, and launch
nothing until they answer** — this is the first action of the session.

---

## 4. Open items — flagged, not fixed

1. **`F30 HOTEL_BOT_LAUNDRY`, 1.9 %.** Peak-flow rescale **excluded by measurement** (job 1171446:
   commercial peaks differ only in the 6th significant figure, a float round-trip through eppy;
   residential peaks move ×0.711–1.574 by design). Remaining candidate: plant-loop coupling with the
   main `LAUNDRY` draw, which fell 67 % on the same service-water system. **Untested.**
2. **T9-12's `k = 0.60` needs re-checking** after the FINDING 7 retail rewire. It was calibrated
   against the *uncalibrated* pool's weekday mean; the shape source has changed underneath it.
   Flagged during the rewire, deliberately not re-tuned in the same change.
3. **The volume identity (0.9647) could not be re-verified.** `WATER USE EQUIPMENT TOTAL VOLUME` is
   not requested as an output variable, so every volume column reads `nan`. Add it to
   `_ensure_output_objects()` before the campaign if that identity is to be quoted.
4. **Arms A–E all carry FINDING 9.** Any DHW number already reported from them is off by the
   per-channel amounts above. Nothing has been retracted yet — decide with the user whether the
   arm-E scorecard needs re-issuing.
5. **The 3 Step-9 EUI FAILs** stay FAIL and stay explained-but-not-rescued (see the step9 memory).
6. Neither D8 nor D9 can catch a defect in `_schedule_daytype_profiles` itself, since both consult
   it. The independent guard is `Step9_docs/3rdJ_09F_daytype_loss.py` (its own IDF parser) — keep
   running it after any change to the schedule readers.

---

## 5. Files from this session

**Modified:** `eSim_bem_utils/commercial_integration.py` (md5 **`233932d7`**),
`eSim_tests/test_t9_13.py` (58 tests),
`Step7_docs/3rdJ_07_aug_to_bem_4split.py` (retail 2030 source + `D2030_RETAIL_PR`),
`Step8_docs/agg_armE.sh` (per-geometry `n_audited`, **§2c D7 and §2d D9 sweeps** — both treat an
ABSENT gate line as a finding, since a cell produced by an older injector would otherwise read as
passing),
`Step7_docs/outputs_step7/retail_presence_multiplier_2030_{cons,central,opt}.csv`
(predecessors kept as `_BAK_2026-08-02.csv`).

**New:** `Step7_docs/3rdJ_07R_regen_retail_2030.py`,
`Step9_docs/3rdJ_09F_retail_rewire_check.py`, `3rdJ_09F_smoke_f8fix.py`, `3rdJ_09F_smoke_delta.py`,
`3rdJ_09F_daytype_loss.py`, `3rdJ_09F_peakflow_check.py`, `3rdJ_09G_finding9_verify.py`,
`3rdJ_09G_score_f9.py`; `Step8_docs/smoke_f8fix.sh`, `rescore_f8fix.sh`, `delta_f8fix.sh`,
`daytype_f8fix.sh`, `smoke_f9fix.sh`.

**Cluster:** `/speed-scratch/o_iseri/step8_4split/campaign/` — `out_F_f8fix/campaign_456301f5`
(FINDING 8 smoke, 2 cells) and `out_G_f9fix/campaign_233932d7` (FINDING 9 smoke, 2 cells). Both
keep their `.sql`, so any further scoring is a 30-second job with **no re-simulation**.
Jobs this session: 1171438 (F8 smoke), 1171441/1171442 (rescore), 1171443 (attribution),
1171444/1171445 (day-type diagnosis), 1171446 (peak flow), 1171448 (**cancelled** — a late fix moved
the injector md5 and shipping a smoke whose INJ_HASH did not match the injector the campaign will
use was not worth saving the restart), **1171449 (F9 smoke, COMPLETED, 10 PASS / 0 FAIL)**.

Useful local command:
`py -3 3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09G_finding9_verify.py --falsify`
— injects both cells with the campaign driver's own call, runs the independent predictor, then
re-creates the pre-fix writer and requires D9 to catch it. Needs `EPLUS_IDD` set to
`C:/EnergyPlusV24-2-0/Energy+.idd`. Takes about 3 minutes and no cluster.
