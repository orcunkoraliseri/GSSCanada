# Manager prompt — 3J Leg-3 Step 9, **2026-08-03** (rewritten after the arm-H launch)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **Supersedes its own morning version, kept beside it as `3rdJ_L3_manager_prompt_2026-08-03_PRE-ARMH.md`.**
> That version's one open decision — the campaign cell count — has been answered by the user and
> executed. **The campaign is LAUNCHED.** Nothing in this file is waiting on a decision.

---

You are the manager on the 3J Leg-3 four-channel mixed-use tower BEM pipeline. Work in
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

## Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node
  (`speed-submit2`). ALWAYS `sbatch`.** Flagged three times; one more is account suspension.
  Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`. `tar`, `find`, `python`,
  **`md5sum`** are **not** allowed there — put hash checks inside the job, on the compute node
  (arm H does exactly this). The login shell is **tcsh** — no `for` loops, no `2>&1`, one short line.
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, even for one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
  explicit `N/A`. A gate counts as validation only once it has been *seen failing*; write the
  falsifiable prediction **before** running the test. **A miss is recorded, not repaired.**
- 🔴 **Vacuous tests are the recurring failure on this project — now TEN kinds.** Before recording
  any PASS, ask: *what result would have made this fail?*
  - **#9 — the gate whose REFERENCE is derived from the same source it audits.** Check `D8`
    (per-day-type volume ratio) passed while the defect was live, because the corrupted Saturday
    was simultaneously its reference and its target. Replaced by `D9`, which reads the **saved
    IDF**. Ask of every gate: *could the thing being checked and the thing checking it be wrong
    together?*
  - **#10 (new, 2026-08-03) — the gate that reads the WRONG PROCESS's exit code.**
    `smoke_f9fix.sh:47` ran the T9-13 unit suite as `$PY test_t9_13.py | tail -3` and then reported
    `$?` — which is **tail's** status, always 0. The line printed `unit suite exit=0` whatever the
    suite did. It is arguably a variant of "the explanation that cannot fail", but the mechanism is
    its own: the check is real, the *measurement of the check* is attached to the wrong thing.
    Corrected in `3rdJ_08D_campaign_speed_armH.sh` (status captured directly, job refuses on it).
    **Grep the other `.sh` files for `| tail` followed by `$?` — this pattern was copied around.**
  - Related method note: a falsification that patches the READER when the defect lived in the
    WRITER tells you about your harness before it tells you about your gate.
- **A local `py_compile` is NOT a valid syntax check for cluster code.** Local Python is **3.13**
  (PEP 701), the cluster env is **3.10.20**. Compile inside the job, under `$PY`, and refuse to run
  if it fails.
- **Do not append to the Progress Log with PowerShell `Add-Content`.** PS 5.1 `Get-Content` reads a
  UTF-8 file as ANSI and double-encodes the whole insert. Append with bash `cat >>` / heredoc.
- **Verify every number you inherit.** Re-derive from the artefact's own columns. **Including
  numbers from earlier in this same log** — the log is append-only, so an early section can be
  flatly contradicted by a later one. See §4: the arm-E scorecard is stated as 2P/3F/1U and then
  superseded by 3P/3F/0U about 330 lines later, and FINDING 8's stated mechanism is retracted
  outright ~180 lines after it is given. **The last statement wins; grep forward before quoting.**
- 🔴 **Never count lines with PowerShell.** `Get-Content file | Measure-Object -Line` **counts an
  empty line as zero lines** and silently undercounts by the number of blank lines — the step-9 log
  reads 3,684 in PowerShell and **4,837** under `wc -l` (1,153 blanks); the injector reads 2,748 vs
  **2,976** (228 blanks). On 2026-08-03 this made "read the last 600 lines" land ~1,000 lines short
  of the end, and two superseded claims were nearly carried into this prompt as current. Use
  `wc -l` via the Bash tool, always.
- **Update the Progress Log live** — same response as each state change, not batched. The live doc
  is `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md` (**4,869 lines**, `wc -l`, as of
  the end of 2026-08-03). Read the last ~600 **counted from the real total**.
- **Leg-2 is closed and paper-ready — no file under `Leg2_2-split/` may be modified.** Reading its
  IDFs and `eplusout.sql` is fine.
- All documents in English; reply to the user in English even though they write French. Keep
  replies short and bulleted.
- Cheap models for mechanical work; minimum monitoring interval 30 min; never poll in a loop.

---

## 1. 🔴 THE CAMPAIGN IS RUNNING — job `1171496`, arm H, 56 cells

User ruling, 2026-08-03: *"lance la campagne 56 cells avec volume_scaled"*. Launched the same
session. Arm E's scorecard is **re-issued after** this lands (also the user's ruling), not now.

| | |
|---|---|
| job | **`1171496`**, array `0-55%20`, `-t 7-00:00:00`, partition `ps` |
| submit script | `Step8_docs/3rdJ_08D_campaign_speed_armH.sh` (md5 `da7085b9`) |
| flags | `--lighting-model calibrated_v2 --dhw-model volume_scaled` (identical to arm E) |
| outroot | `/speed-scratch/o_iseri/step8_4split/campaign/out_H_allfix/campaign_233932d7` |
| at launch | tasks 0–7 RUNNING, 8–55 PENDING (`AssocGrpCpuLimit`) — normal throttling |

`H − E` isolates the four fixes and nothing else; everything that differs is upstream of the flags:

| fix | carrier | md5 |
|---|---|---|
| FINDING 6 — office 2030 on the matched stock frame | `office_presence_multiplier_2030.csv` | `575d17e5` |
| FINDING 7 — retail 2030 rewired to calibrated `_C_v2` | `retail_presence_multiplier_2030_{cons,central,opt}.csv` | `82b425b5` / `11414644` / `700398d0` |
| FINDING 8 — DHW cache-key collision | `commercial_integration.py` | `233932d7` |
| FINDING 9 — per-day-type Sat/Sun volume loss | same injector | `233932d7` |

**Why 56 and not the 36 stale 2030-family cells:** FINDING 9 changes DHW in *every* cell running
`volume_scaled`, not only the 2030 family. `Y2022` and the three historical years are in scope for
the DHW reason, not the product reason.

### Guards — all seven were OBSERVED firing on task 0, not assumed

```
[guard OK] injector (FINDING 8+9) = 233932d7
[guard OK] office 2030 product (FINDING 6) = 575d17e5
[guard OK] retail 2030 cons / central / opt (FINDING 7) = 82b425b5 / 11414644 / 700398d0
[guard OK] drivers compile under Python 3.10.20
[guard OK] T9-13 unit suite passed (exit 0)
```

The five product-md5 literals exist because `INPUTS_HASH` only protects a cell against a product
that changed *under an existing outdir*. A fresh outroot has no prior manifest, so it cannot tell a
correct product from a stale one — it would run all 56 cells on the pre-FINDING-6/7 CSVs and record
a self-consistent hash for them. Checked on **every** task, not task 0, because a partially
completed `scp` would otherwise pass task 0 and corrupt the rest.

`[T9-13 audit FAIL] 0 objects audited` on `Default_NECB__Tall__MTL` is **expected** — that is the
uninjected control cell, and "empty audit = FAIL" is the deliberate rule so a silently-skipped
audit cannot read as a pass. Four such cells exist (`{Tall,SuperTall}×{MTL,CLG}`); `agg_armE.sh`
classifies them separately. `INPUTS_HASH=d41d8cd9` on those cells is md5("") — correct for a cell
with no channels.

---

## 2. FIRST ACTIONS OF THE SESSION, in order

1. **`squeue -u o_iseri` / `sacct -j 1171496`.** Expect 56 COMPLETED. Any non-zero exit is a
   guard refusal or a real failure — read that task's log in
   `campaign/logs/armH_1171496_<task>.out` before doing anything else.
2. **🔴 Verify the new DHW volume series is real, in a cell that finished.** This is the one thing
   in arm H that has NOT been verified end-to-end (§3). The write half is confirmed — the
   `Output:Variable` is present in `Default_NECB__Tall__MTL/injected.idf` — but no finished cell
   had been read at launch. Check `dhw_volume_hourly.csv` exists, has 8760 rows, and is **not**
   all-zero/`nan`, and that `manifest.json` carries no `dhw_volume_hourly_exception`.
3. **Aggregate**: `Step8_docs/agg_armE.sh`, repointed at `out_H_allfix`. It already sweeps §2c `D7`
   and §2d `D9` and treats an **absent** gate line as a finding (a cell from an older injector must
   not read as passing).
4. **Then** the scoring work in §4.

---

## 3. What arm H changed beyond the four findings — open item 3, CLOSED

`Water Use Equipment Total Volume` was never requested as an output, so every volume column in arms
A–E reads `nan`. It is now requested (`DHW_VOLUME_VARIABLE` in `3rdJ_08P_probe_driver.py`) and
written per channel to `dhw_volume_hourly.csv`.

**The motive is anti-vacuity, not convenience.** The only existing statement of the T9-13 volume
identity (0.9647) comes from `3rdJ_09E_dhw_identity_probe.py`, which computes
`Σ Peak_Flow × (5·mean_wd + 2·mean_we)/7` **by parsing the IDF with our own reader**. Audited
quantity and auditing reference are both products of code we wrote — vacuous-gate kind #9 exactly,
sitting inside the one number quoted as proof that T9-13's arithmetic is correct. EnergyPlus
integrates the schedule it was actually handed, so its reported volume is a reference our parser
cannot corrupt.

- `_write_dhw_hourly_csv()` gained `variable`/`col_prefix` kwargs so the volume series reuses the
  **same** channel-resolution rules. Defaults reproduce prior behaviour exactly; the existing call
  site is untouched.
- The new extraction has its **own** `try/except`, like every sibling. A new reporting series must
  never take down a 56-cell campaign; if the variable is absent the cell still produces everything
  it produced before and the exception lands in the manifest. Downside bounded at the status quo —
  **which is also why step 2 of §2 matters: fail-soft means a silent `nan` looks like success.**
- `OUTPUT_SCHEMA_HASH` **`db4e729f` → `93dd5129`**, by design (it exists to stop a reporting-side
  change leaving old cells looking "done"). It is checked for *uniformity* across cells, not against
  a literal, so the Step-9 gate is unaffected. `INJ_HASH` does **not** move, so the campaign dir is
  `campaign_233932d7` — the same build the FINDING 9 smoke passed on.

---

## 4. Scoring work, once 56/56 land

**🔴 Arm E's FINAL scorecard is 3 PASS / 3 FAIL / 0 UNTESTABLE** (log §"P1 IS TESTABLE AFTER ALL").
An earlier section of the same log states **2 PASS / 3 FAIL / 1 UNTESTABLE** — that is the *first*
scoring run and it is **superseded**. `P1` was re-scored and **PASSED**: every cell already writes
`dhw_hourly.csv`, the "missing artefact" was a scoring error, and on `B_central__Tall__MTL`
residential the night 00–05 share went 0.0834 → **0.0828** with the peak draw hour unmoved at
**06:00** (against T9-11's 0.0834 → 0.3286 and 06:00 → 04:00). **Do not quote the earlier table.**

| | verdict | one line |
|---|---|---|
| P1 | **PASS** | shape preserved — the T9-11 failure does not recur |
| P5 | **PASS** | 0 of 616 material non-DHW end uses above 0.5 %; worst mover +0.207 % |
| P6 | **PASS** | 56/56 cells, max \|ΔArea\| = 0.0 m² over 392 pairs |
| P2 | **FAIL** | office DHW +21.7 / +8.4 / −3.7 % vs predicted +0.3 / −11.2 / −21.8 |
| P3 | **FAIL** | hotel +15.31 % vs +12.4 ± 2.0 |
| P4 | **FAIL** | residential +51.40 % vs +8…+18 % |

- **Re-issue arm E's scorecard** (the user's ruling). `P2` must be re-derived against the rebuilt
  office product — arm E ran on the pre-FINDING-6 one (weekend ratios ×2.49/×2.08/×1.73; corrected
  ×2.60/×2.12/×1.60). **`P2`, `P3`, `P4` failed as pre-registered and that stands in the record
  regardless of what the re-run says** — the re-run produces new numbers, it does not repair old
  verdicts. Note P3's consolation ("the magnitude missed but the mechanism worked") was **struck**:
  the motion was substitution, i.e. FINDING 8, not `r` modulation.
- **`P4` is the most important open physics item, and its first probe is already SPENT.** Job
  `1171408` tested *"`Peak_Flow_Rate` rose against hard-sized heaters, so the plant spends more time
  in recovery"* with both branches pre-registered. **REFUTED:** `Water Use Equipment Heating Energy`
  totals came in at **×1.389** — the draw energy itself moved, so the fault is not plant sizing.
  Do **not** re-run that probe as though it were open.
  - FINDING 8 then explained **~29 %** of P4: the big `LAUNDRY SERVICE WATER USE` object carries no
    zone prefix and is attributed to the **residential** channel by the aggregator; its rise was
    +1848 GJ against a residential channel rise of +6366 GJ. **~71 % remains unexplained**, and the
    27 apartment objects' own volume identity holds at 0.9647.
  - The live candidates are therefore **draw temperature** and **end-use attribution**, not plant
    sizing. Arm H's `dhw_volume_hourly.csv` gives the volume side independently of our parser for
    the first time — that is the new lever on this question.
- **The `Y2022` office channel (+28.6 % at `r ≈ 1.0`) is a separate open item**: the office restroom
  objects moved **×0.952**, i.e. *down*, while the office channel total rose. That is an
  **attribution** question, untouched by FINDINGS 8 and 9. FINDING 9 accounts for the ×0.952 itself
  (now ×1.000 in arm H), so re-measure this in arm H before theorising.

---

## 5. Open items — flagged, not fixed

1. **`F30 HOTEL_BOT_LAUNDRY`, 1.9 %.** Peak-flow rescale **excluded by measurement** (job 1171446).
   Remaining candidate: plant-loop coupling with the main `LAUNDRY` draw, which fell 67 % on the
   same service-water system. **Untested.** The FINDING 9 smoke's discriminating prediction held
   (F30 required to stay at 1.019 because its prototype has Sat == Sun, and it did), so the
   FINDING 8 attribution of that 1.9 % stands and F30 is a genuinely separate item.
2. **T9-12's `k = 0.60` needs re-checking** after the FINDING 7 retail rewire. It was calibrated
   against the *uncalibrated* pool's weekday mean; the shape source has changed underneath it.
   Deliberately not re-tuned in the same change. **Arm H runs with the un-retuned `k`** — so any
   arm-H retail lighting result is provisional until this is settled.
3. **Arms A–E all carry FINDING 9** (retail DHW +7.7 %, office +4.8 %, hotel `BLDG` +0.5 %). Nothing
   has been retracted; the re-issue in §4 is the remedy.
4. **The 3 Step-9 EUI FAILs** stay FAIL and stay explained-but-not-rescued.
5. **The hotel EUI band question is still open and still blocking** `S9-EUI-hotel`. R1 (amenity
   classification, dr_L3-03 §Caveats + §C.4) says `[240, 300]` → **0/56**. R2 (NECB 2017 /
   CanmetENERGY 2020, CZ-matched) says `[140,220]`/`[160,240]` → much better. They conflict, and the
   tie-breaker is one unanswered question: **is the CanmetENERGY NECB 2017 hotel archetype
   full-service or limited-service?** Requires the CanmetENERGY *Commercial Archetypes Performance
   Study* (2020), not in `deepResearch/`. Until it is read, adopting R2 would be choosing the band
   that rescues the gate over the band that condemns it, on no evidence. Currently implemented as
   three **INFO-only** gates; `S9-EUI-hotel` keeps `[180,300]` and keeps its FAIL.
6. **Decision 5 (Leg-2 office-EUI corrigendum) needs one bounded read-only job** before it can carry
   a number: run the corrected EUI query against **Leg-2's own** `eplusout.sql` files. The 1.706×
   factor was measured on a *Leg-3* run and `172.7 / 1.706 ≈ 101.2` is an indication of magnitude,
   **not a derived value**. Version A of the caveat (no number) is publishable today; version B
   needs that job. **Never claim the published band was affected — that was checked and refuted;
   `OFFICE_EUI_BAND` is hard-coded from literature, not simulation.**
7. Neither `D8` nor `D9` can catch a defect in `_schedule_daytype_profiles` itself, since both
   consult it. The independent guard is `Step9_docs/3rdJ_09F_daytype_loss.py` (its own IDF parser) —
   keep running it after any change to the schedule readers.

---

## 6. Files from the 2026-08-03 session

**Modified:** `Step8_docs/3rdJ_08P_probe_driver.py`, md5 **`b42dc4ba`** (this is the *post*-change
hash, verified on disk after the edits and confirmed live on the cluster — task 0 printed
`OUTPUT_SCHEMA_HASH = 93dd5129`, which only the edited file produces). Changes:
`DHW_VOLUME_VARIABLE`, parametrised `_write_dhw_hourly_csv(variable=, col_prefix=)`,
`dhw_volume_hourly.csv` in `_do_postprocess()`, `OUTPUT_SCHEMA_HASH` `db4e729f` → `93dd5129`.

**New:** `Step8_docs/3rdJ_08D_campaign_speed_armH.sh` (md5 `da7085b9`).

**Unchanged but re-uploaded to guarantee the cluster copy:** `eSim_bem_utils/commercial_integration.py`
(`233932d7`), `eSim_tests/test_t9_13.py` (`9fe462e6`, 58 tests),
`Step7_docs/3rdJ_07_aug_to_bem_4split.py` (`361ad354`), the four Step-7 2030 product CSVs,
`Step8_docs/3rdJ_08D_campaign_driver.py` (`8164c10b`), `3rdJ_08D_campaign_cells.py` (`dca23502`),
`agg_armE.sh` (`29dddd9b`), and three Step-9 scoring scripts.

**Cluster:** `campaign/out_H_allfix/campaign_233932d7` (arm H, running). Earlier smoke dirs
`out_F_f8fix/campaign_456301f5` and `out_G_f9fix/campaign_233932d7` both keep their `.sql`, so any
further scoring of those is a 30-second job with no re-simulation.

Jobs: **1171496 (arm H, 56 cells, LAUNCHED 2026-08-03)**. Previous session: 1171438, 1171441/1171442,
1171443, 1171444/1171445, 1171446, 1171448 (cancelled), 1171449 (F9 smoke, 10 PASS / 0 FAIL).

Useful local command:
`py -3 3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09G_finding9_verify.py --falsify`
— injects both cells with the campaign driver's own call, runs the independent predictor, then
re-creates the pre-fix writer and requires `D9` to catch it. Needs `EPLUS_IDD` set to
`C:/EnergyPlusV24-2-0/Energy+.idd`. About 3 minutes, no cluster.
