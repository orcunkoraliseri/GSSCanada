# Manager prompt — 3J Leg-3 Step 9, **2026-08-04** (LIVING PROGRESS FILE)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **This file is a LIVING HANDOFF and is updated at every step of the work, not once at end of day.**
> The user starts a fresh manager session most mornings, and may start one at any moment. Whatever
> state the work is in when a new session opens, this file must already describe it. Predecessors:
> `3rdJ_L3_manager_prompt_2026-08-03.md` (arm H closure — still the reference for §§ 4–6 detail),
> `..._2026-08-03_PRE-ARMH.md`, `..._2026-08-02.md`, `..._2026-08-01.md`.
>
> 🔴 **If you are the manager and you change the state of the work — a job lands, a gate flips, a
> decision is taken — UPDATE THIS FILE IN THE SAME RESPONSE.** Same discipline as the Progress Log.
> A handoff file that lags the work is worse than none, because it is trusted.

---

You are the manager on the 3J Leg-3 four-channel mixed-use tower BEM pipeline (residential / office /
retail / hotel). Work in `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\`.

## Standing rules — non-negotiable

- 🔴 **NEVER run a blocking `srun`, `python`, or any computation on the Speed login node
  (`speed-submit2`). ALWAYS `sbatch`.** Flagged three times; one more is account suspension.
  Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`. `tar`, `find`, `python`,
  **`md5sum`** are **not** allowed there — put hash checks inside the job, on the compute node.
  The login shell is **tcsh** — no `for` loops, no `2>&1`, **no `2>/dev/null`**, one short line.
  - 🔴 **`2>/dev/null` inside `ssh speed "..."` is a tcsh parse error** ("Ambiguous output redirect")
    and it does **not** fail loudly — stdout comes back empty and the caller reads that as "no
    result". On 2026-08-03 a poll loop built this way reported an empty job state 40 times over 3.3 h
    and never noticed the job had finished in 29 min. Do not suppress stderr on the cluster.
  - 🔴 **Nested `ssh speed "... ssh speed \"...\" "` fails with `Permission denied (publickey)`.**
    One `ssh` per Bash call. (Hit again 2026-08-03 while ranking peak draws.)
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, even for one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
  explicit `N/A`. A gate counts as validation only once it has been *seen failing*; write the
  falsifiable prediction **before** running the test. **A miss is recorded, not repaired.**
- 🔴 **Vacuous / mis-specified tests are the recurring failure on this project.** Before recording
  any PASS, ask: *what result would have made this fail?* The catalogue now runs to **thirteen**
  kinds; the three newest were all found on 2026-08-03 and are the ones to watch for right now:
  - **#11 — the gate measuring a quantity the deliverable discards.** (Backward audit.)
  - **#12 — the default that cannot be distinguished from a measurement.** A reader fell back to
    `r = 1.0` when it could not find its provenance file; `r = 1.0` is also a *legitimate* value in
    this grid, so "unread" and "read as 1.0" collapsed into the same number. It only crashed because
    *all three* cells defaulted and the regressor lost its variance — had two matched and one not, a
    plausible wrong elasticity would have printed in silence. **A fallback must never be a value the
    measurement could legitimately return. Refuse instead.**
  - **#13 — the conjunction gate, and the monotonicity clause across a saturation boundary.** `K2`
    and `K4` each bundled a *trend* clause with a *threshold* clause under one verdict, so one
    FAIL/PASS reported on two independent claims. Worse, both trend clauses predicted monotonicity in
    a quantity that crosses a saturation boundary — where non-monotonicity is *structural*. Both
    failed while the hypothesis they were probing turned out to be TRUE. **Split conjunctions into
    separately-numbered gates, and never read a non-monotone trend clause as evidence about a
    mechanism when the system saturates.**
  - Older ones still live: **#9** the gate whose reference comes from the same source it audits;
    **#10** the gate reading the wrong process's exit code (swept repo-wide, exactly one occurrence,
    already fixed — **do not re-run that sweep**); **silence is a failure mode** — a reader returning
    0.0 for input it cannot parse blames the simulation for its own gap (cost 16 spurious FAILs in
    job 1171607; every reader must itemise what it could not read, the `G4` pattern).
  - **A gate can be real and still not prove what it is quoted for.** Arm H's `G2` (office/retail
    Sat≠Sun, +151.69 %) is structurally invariant under T9-13 because `r_we` cancels — it separates
    "FINDING-9-fixed injector" from "pre-fix injector", **not** "injected" from "not injected".
    The gate that shows injection reached the model is `G1`.
- **A local `py_compile` is NOT a valid syntax check for cluster code.** Local Python is **3.13**
  (PEP 701), the cluster env is **3.10.20**. Compile inside the job, under `$PY`, and refuse to run
  if it fails. (`recheck_armH.sh` §0 is the pattern to copy; every script written 2026-08-03 does it.)
- **Do not append to the Progress Log with PowerShell `Add-Content`.** PS 5.1 `Get-Content` reads a
  UTF-8 file as ANSI and double-encodes the whole insert. Append with bash `cat >>`. **If a bash
  heredoc fails to parse on a long block, write the block to the scratchpad with the Write tool and
  `cat scratch >> target`** — that is the reliable route and it was used for the 2026-08-03 entries.
- **Verify every number you inherit.** Re-derive from the artefact's own columns. **Including numbers
  from earlier in this same log** — it is append-only, so an early section can be flatly contradicted
  by a later one (the arm-E scorecard, FINDING 8's mechanism, and now the K = 3 capacity inference).
  **The last statement wins; grep forward before quoting.**
- 🔴 **Never count lines with PowerShell.** `Measure-Object -Line` counts an empty line as zero.
  Use `wc -l` via the Bash tool, always.
- **Update the Progress Log live** — same response as each state change, not batched. Live doc:
  `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md`, **6,461 lines** (`wc -l`,
  2026-08-04 01:00). Read the last ~600 counted from the real total.
- 🔴 **Never make a bare `echo` the last line of a job script.** The job then exits with `echo`'s
  status — always 0 — so a refusing script reports COMPLETED and releases its `afterok` dependents.
  Hit twice on this project (§0.8). `RC=$?; echo ...; exit $RC`.
- 🔴 **One `ssh` per Bash call**, and **a guard must take its reference from the artefact under test,
  never from a constant you believe** (§0.7).
- **Leg-2 is closed and paper-ready — no file under `Leg2_2-split/` may be modified.** Reading its
  IDFs and `eplusout.sql` is fine.
- All documents in English; reply to the user in English even though they write French. Keep replies
  short (≤ 100 words unless detail is asked for).
- Cheap models for mechanical work; minimum monitoring interval 30 min; never poll in a tight loop.
  A plain background `Bash` waiter costs no model tokens and is the preferred way to wait on a job.

---

## 0. 🔴 WHERE THE WORK STANDS THIS MORNING — read this first

The single live thread is the **hotel DHW plant resize**. Everything else on the project is parked
behind it, because the plant distorts every hotel and residential DHW number in Steps 8–9.

**STATE (updated 2026-08-04, 10:41 EDT): the campaign RAN, LANDED 56/56, and SCORED 6/6 PASS.**
**Nothing is in flight. Nothing is blocked. There is no job to poll.**

# 🟢 **THE PLANT QUESTION IS CLOSED. K = 10 un-saturates the DHW plant across the whole grid.**
# 🟢 **§0.11 ANSWERED by the user, 2026-08-04: ALL-CHANNEL RESIZE.**
# 🟢 **CAMPAIGN EXECUTED AND SCORED — see §0.17 for the scorecard and its two caveats.**

| job | what | outcome |
|---|---|---|
| ✅ `1172037` | 56-cell resized campaign, K = 10, all-channel, `--array=0-55%20` | **56/56 COMPLETED**, zero FAILED/CANCELLED/TIMEOUT/NODE_FAIL; 20–60 min/cell, long pole `_45` 1:00:15 |
| ❌ `1172045` | scorecard, `--dependency=afterany:1172037` | FAILED 1:0 — `r` reader had no case for `Default_NECB__*` |
| ❌ `1172108` | scorecard, re-submit | FAILED 1:0 — fix asserted **whole-cell** untreatedness, refused on `Y2005__*` |
| ✅ `1172109` | hotel-DHW census of all 56 cells (pure grep) | COMPLETED — population exactly bimodal, 40 injected / 16 not |
| ✅ **`1172110`** | **scorecard, final** | **COMPLETED 0:0 — `C1' C2' C3a C3b C4 C4c` ALL PASS, 56/56 cells** |

Progress Log now **7,003 lines** (`wc -l`, 2026-08-04); the full entry is the last section of
`improvements/3rdJ_L3_improvements_step9.md`.

### 0.17 🟢 THE SCORECARD, AND WHAT IT DOES *NOT* LICENSE

```
  SCORECARD  C1' PASS   C2' PASS   C3a PASS   C3b PASS   C4 PASS   C4c PASS     56 / 56 cells
```

`C3a` — every hotel use-type in every cell delivers its design rise (49.19 / 71.40 K, tol 0.5 K),
0 violations, 0 unreadable targets. **The 22.66 K marginal-rise defect is closed.**
`C4` — hotel energy elasticity 1.0013 / 1.0014 / 1.0014 / 1.0015 by group, against arm H's
0.6470 / 0.6431 / 0.5830 / 0.5779 (`C4c`, so the resize moved it rather than finding it there).

**Two caveats. Do not quote the 1.00 clean.**

1. **`C4` is only weakly independent of `C3a`.** Once every use-type delivers design rise and volume
   scales exactly with r, E = V·ρc·ΔT ∝ r follows arithmetically. `C3a`'s 0.5 K tolerance leaves
   room for ≈ ±0.06 of slope over a log-r span of 0.18, so `C4` *could* have landed 0.94–1.06 — the
   window where `C3a` passes and `C4` fails is real but narrow. `C4` is a confirmation; its
   DECISIVE standing comes from `C4c`, not from orthogonality to `C3a`.
2. **`n_r` = 4–5 distinct r per group, not 14.** `sens_office_*`/`sens_retail_*` inherit their base
   scenario's hotel r, and 4 cells sit at exactly r = 1.0. R² = 1.000 is across 4–5 distinct x with
   replication. The `n_r` column exists so this cannot hide behind an n = 14 label.

**`C6` INFO — the undersizing was NOT hotel-only.** Median ΔE: hotel **+170.79 %**, residential
**+11.30 %**, office −0.03 %, retail −0.00 %; ΔV = 0.0000 % in all four channels, so this is pure
delivered-energy recovery, not extra draw. **Residential DHW was plant-limited by 4–14 % — new, and
not part of the hotel 22.66 K diagnosis.** `C6` STAYS INFO: no non-hotel expectation was
pre-registered, and a number scored against an expectation invented after seeing it is not a test.

**`C5` INFO — whole-tower all-fuel +10.95 / +18.93 / +24.69 % (min/median/max) vs arm H.** Floor area
is unchanged by construction (`C2'`), so the % shift IS the EUI shift. A ~19 % median move makes this
a materially different building and reinforces the standing scope warning: 🔴 **every comparison in
this campaign moves four channels at once — it is a NEW ARM for residential, office, retail and
hotel, not a hotel-side correction on top of arm H. Anything written up from it must say so.** It
also bears on the still-open hotel EUI band decision (§ parked items).

**The `r` reader was fixed twice; NO gate, threshold, tolerance or grouping was touched.**
`C1'`/`C2'`/`C3a`/`C3b` do not call it and were byte-identical across all three scorer runs. The 16
never-injected-hotel cells (4 `Default_NECB__*` + 12 `Y2005`/`Y2010`/`Y2015__*`, the hotel-era
exclusion) run the untouched NECB schedule, which IS the `baseline_series` r is measured against, so
r = 1.0 is a fact read off the provenance and they are each group's anchor point. Because 1.0 is
*also* a legitimate measured r, that state is asserted positively on six hotel-specific conditions —
`hotel NOT in channels_requested` AND `hotel IS in fallback_channels` — and every such cell is NAMED
on the scorecard. Anything neither tokened nor fully asserted still hard-refuses.

### 0.15 🔴 WHAT THE PRE-REGISTRATION SAYS NOW — it was edited before submission, on measurement

Four changes, all made before any cell of this campaign existed, all strengthenings, all recorded in
the Progress Log entry of 2026-08-04. `resize_campaign.sh`'s header and
`3rdJ_09H_resize_campaign_score.py`'s docstring carry the same text and were reconciled first.

| gate | status | one-line |
|---|---|---|
| `C1′` | **widened** | DHW volume unchanged ≤ 0.1 % in **all four channels**, not just hotel |
| `C2′` | **re-specified** | resized IDF differs from arm H's only on `Heater Maximum Capacity` lines |
| `C3a` | **re-specified** | every hotel use-type delivers its design rise (140 F ±0.5 K of 49.19, 180 F of 71.40) |
| `C3b` | **new control** | the per-type table reconciles with the driver's hotel channel to 0.01 % |
| `C4` | unchanged | hotel energy elasticity ≥ 0.90 in 4/4 (geometry, city) groups |
| `C4c` | **new control** | arm H must be **below** 0.90 in every group where `C4` passes |
| `C5` | INFO | all-fuel site energy shift, whole tower. Area is fixed by `C2′`, so % shift = EUI shift |
| `C6` | INFO | per-channel resized − arm H DHW energy **and** volume, four channels, 56 cells |

🔴 **Two of these exist because the old text could not have failed, and one of those was written
this morning.** Read this before quoting any of them:

- **`C2` as inherited was unscoreable.** The resized manifest is a *copy* of arm H's, so comparing
  its `INJ_HASH` to arm H's compares a value with itself — **vacuous-gate #9**. And **no area key
  exists in the manifest at all** (checked 2026-08-04). Both clauses named things that could not
  disagree. `C2′` diffs the two IDFs instead, which subsumes the area claim.
- **`C3′`'s second clause, as written in this file this morning, was arithmetically vacuous.** "The
  per-cell aggregate equals its own 180 F/140 F volume-share reconstruction within 0.5 K" **cannot
  fail once `C3a` passes** — a weighted mean of values each within 0.5 K of their design rise is
  necessarily within 0.5 K of the weighted design mean. It is now printed as a derived quantity and
  **not scored**; `C3b` is the independent check it was reaching for. **This is vacuous-gate #13
  reappearing inside the very re-specification written to avoid #13.** The catalogue is not a
  checklist you pass once.

**Evidence for `C3a` is written by the run**, not reconstructed afterwards: every cell emits
`hotel_dT_by_type.csv` using the module H9/H10/H11 were scored with, and **refuses** if its per-type
hotel volume does not reconcile with the driver's `dhwvol_hotel` to 0.01 %.

### 0.16 ✅ DISCHARGED 2026-08-04 — what was owed when the scorecard landed

- ✅ Scored as written. No tolerance was widened; nothing was re-aimed. `H2`, `H6` and `C3` still
  stand on the record as failed/mis-specified. The only code touched after results existed was the
  hotel `r` **reader** — see §0.17; no gate, threshold, tolerance or grouping moved.
- ✅ `C6` stayed INFO, and it is the run's most substantive finding (residential was plant-limited
  too). It was **not** promoted to a gate on the strength of what it showed.
- ✅ `C5` came in at **+18.93 % median, tower-wide** — a large shift, as §0.3.1 anticipated. The
  hotel EUI band (§2, **still with the user**) is what this has to be re-validated against, and that
  question is **NOT settled by this run.**

Every hotel water use delivers its **exact design rise** in both grid extremes, to two decimals:

| use class | target | grid-MAX | grid-MIN |
|---|---|---|---|
| `LAUNDRY` / `BOOSTER` | **180 F** | 71.43 / 71.34 K | 71.43 / 71.34 K |
| 9 shared faucet types | **140 F** | 49.17–49.23 K | 49.17–49.23 K |

Nothing is throttled. The 1.95 K aggregate spread is **entirely the 180 F volume share** —
64.57 % in the grid-max cell vs 73.34 % in the grid-min — and it reproduces by hand:
`(0.7334 − 0.6457) × (71.40 − 49.19) = 1.95 K`, the observed gap exactly.

| job | what | reads |
|---|---|---|
| ✅ `1171859` | K = 10 hotel-scoped — **H1 PASS, H2 FAIL, H3 PASS, H4 rec.** | `logs/hdelast_1171859.out` |
| ✅ `1172028`/`1172031` | K escalation — **H5 PASS, H6 FAIL, H7 PASS, H8 PASS** | `logs/hd2elast_1172031.out` |
| ✅ `1172033` | decomposition — **H9 PASS, H10 PASS, H11 PASS**; mechanism = **MIX** | `logs/dtdecomp_1172033.out` |

*(Historical, kept for the reasoning — the edits below were done and the campaign submitted on
2026-08-04. See §0.15.)* Read §0.13, §0.14 and §0.11 (now **resolved**), then do the edits §0.11 and
§0.9 name — `C3` → `C3′`, and widen `C1` to all four channels — and submit. **Nothing else is
waiting on the user for this campaign.**

🔴 **Read the `hd*elast_*.out` / `dtdecomp_*.out` logs, NOT the `hdroom2_*.out` probe logs, for any
H-gate.** The probe prints tower-wide ΔT; every H-gate is hotel-scoped. ~5 K apart (§0.10a).

### 0.14 🔴 TWO STANDING ITEMS THIS RESOLVED — re-read before quoting either

**`TARGET_K = 49.2` (`3rdJ_09H_resize_elasticity.py:45`) is EXPLAINED, and it is wrong where used.**
49.2 K is the **140 F faucet design rise** (measured 49.17–49.23 K) — not invented, just *scoped to
one use class*. The hotel aggregate is **63.55–65.50 K**, because 180 F laundry+booster carry 65–73 %
of the volume at 71.4 K. Therefore:
- 🔴 **Every quotation of `R4` ("133.2 % / 119.2 % of target") is an aggregate over a faucet-only
  denominator and must not be repeated.** Correct denominator: per-use (49.19 / 71.40 K) or per-cell
  aggregate (63.55 K grid-max, 65.50 K elsewhere) — never one grid-wide 49.2.
- 🔴 **The original hotel finding was UNDERSTATED.** *"Marginal m³ served at 22.66 K vs a 49.2 K
  target"* → the real aggregate target is ~65 K, so arm H served its marginal m³ at roughly **35 %**
  of the delivered rise, not 46 %. The finding is *stronger* than written. (22.66 K is a marginal OLS
  slope and ~65 K an average — a direction, not a new coefficient. Re-derive before quoting.)

### 0.13 🟢 THE DECOMPOSITION — **H9 PASS, H10 PASS, H11 PASS** (job 1172033)

| gate | verdict | evidence |
|---|---|---|
| **H11** CONTROL | **PASS** | duplicated channel map = driver's hotel volume to **0.00000 %** (34,940.2 / 25,061.8 m³) |
| **H9** PARTS | **PASS** | all 11 shared use-types agree to **0.00 K** |
| **H10** WHOLE | **PASS** | MIN's per-type rises × MAX's volume shares = **63.55 K** vs measured 63.55 K |

**Mechanism (A) MIX established — it required both H9 and H10 and got both.** Caveat stated not
buried: 11.95 % of MAX volume (5 faucet types) had no MIN counterpart and borrowed its own rise. All
five are 140 F faucets measuring 49.17–49.22 K, identical to the nine shared ones; the hand-check
above uses only two design rises and lands on the same 1.95 K, so the borrow is not load-bearing.

### 🔴 `C3` MUST BE RE-SPECIFIED BEFORE THE CAMPAIGN — successor below

`C3` as written ("hotel ΔT constant across all 56 cells to within 0.5 K, **across geometry groups**")
is **false by construction**: the 180 F share is a use-mix property that varies with geometry. It
would fail every run for a non-plant reason.

**`C3` stands recorded as mis-specified; `H2` and `H6` stand recorded as FAILED. None is re-scored.**

> **C3′ DECISIVE** — in all 56 cells, **every hotel `WaterUse:Equipment` type delivers its own design
> rise**: 140 F types within 0.5 K of **49.19 K**, 180 F types within 0.5 K of **71.40 K**. *And* the
> per-cell aggregate must equal its own 180 F/140 F volume-share reconstruction within 0.5 K, so a
> cell drifting for a third reason is still caught.

**This is stricter than C3, not looser** — C3 checked one aggregate per cell, C3′ checks every object
*and* the aggregate, and it has a defined failure mode (any object short of design rise = a
throttle) where C3 could not tell a throttle from a mix difference. It rests on an independent
measurement, not on the convenience of passing. Tooling exists:
`3rdJ_09H_hotel_dT_decompose.py` already produces the per-type table and the reconstruction.

### 🟢 Standing authorisation, 2026-08-03 night — **now EXHAUSTED**

The user said **"continuer jusqu'à la fin"** before going to sleep. That authorised carrying the
resize thread through without further approval: score H1–H4, and **if H2 passes, launch the 56-cell
campaign at K = 10**; if H2 fails, raise K, re-probe, iterate — do not launch.

**H2 FAILED, so the launch condition was never met.** K was raised and re-probed exactly as
instructed (H5–H8), and the follow-through identified the real mechanism (H9–H11). The thread has
been carried to its end: **the plant question is closed and there is nothing left to run.** What
remains is a decision (§0.11), and a decision is not something this authorisation covers.

It does **not** authorise the items in §2 that are explicitly the user's call (P3 re-specification,
the hotel EUI band, the Leg-2 corrigendum). Those stay parked. §0.11 was outside it too — and the
user answered it directly on 2026-08-04 (**all-channel**), which is a *new* instruction, not this
authorisation extending itself.

### The decision this gates — **historical; both halves are now settled**

*(Kept for the reasoning. Outcome: H2 failed, but §0.13 made the plant question moot, and §0.11 fixed
the scope as all-channel. The "if H2 passes / fails" trigger below is dead — see §0.9.)*

The user chose **"uniform hard-size to grid max"**: measure peak demand across all 56 cells, set all
six heaters in every cell to **one** capacity, so the plant is a *constant* across the grid and the
occupancy lever stays clean. Per-cell `Autosize` was rejected on methodological grounds — it would
give `B_opt` (r = 1.20) a bigger boiler than `B_cons` (r = 0.98), so "DHW rises with occupancy" would
partly become "we gave it a bigger boiler". The 56-cell grid exists to vary occupancy and nothing
else.

**If H2 passes → the 56-cell campaign at K = 10 is unblocked, subject to §0.3 below.**
**If H2 fails → raise K, re-probe the grid-max cell, do not launch.**

### 0.1 Pre-registration for the in-flight check (written before submission, do not edit)

Cells are the measured grid extremes from job 1171806:
`sens_hotel_opt__SuperTall__MTL` (**max**, 15.8878 m³/h) and `B_cons__Tall__CLG` (**min**, 10.6444).
Each runs against **its own** EPW (Montreal / Calgary), not a shared one.

- **H1 CONTROL** — hotel volume unchanged from arm H (≤ 0.1 %) in both cells. If volume moves the
  edit is not surgical and nothing below is readable.
- **H2 DECISIVE** — hotel-scoped delivered ΔT at K = 10 is **≥ 65.0 K in both**, and the two cells
  agree with **each other** within **0.5 K**. Reference: the `Tall__MTL` trio sat at 65.50 / 65.51 /
  65.51 K. Agreement between the extremes is the actual claim — a uniform plant is a valid control
  only if it delivers the same temperature everywhere.
- **H3 FALSIFIER, which is what stops H2 being vacuous** — the **unresized** arm-H ΔT in these same
  two cells must be **< 40 K**. If arm H already delivered ~65.5 K at the grid max, H2 could not
  possibly fail there. Expected ~22 K by analogy with the trio, but measured, not assumed.
- **H4 INFO** — each cell's measured peak requirement against the 4,476 kW installed.

🔴 **The elasticity block printed by `3rdJ_09H_resize_elasticity.py` on this pair is N/A BY
CONSTRUCTION and must not be quoted.** The two cells differ in height, climate and scenario, so a
2-point E-vs-r fit confounds occupancy with geometry. **R0 is EXPECTED TO FAIL** here (it was
calibrated on the `Tall__MTL` trio) and that failure is the script correctly refusing to let R3 be
read. Only the per-cell `dT` lines are in scope.

### 0.13a Pre-registration for H9–H11 as submitted (do not edit)

`implied dT` is `E/(V·ρc)` over the hotel channel — a **volume-weighted average** of per-use rises.
Two mechanisms lower it, with opposite consequences:

- **(A) MIX** — every object delivers its full rise; the grid-max cell just carries more volume in
  low-target uses (laundry, booster). Then **63.55 K is its legitimate ceiling, there is no defect,
  and it is `C3` that is wrong** — a cross-geometry ΔT constant never existed.
- **(B) THROTTLE** — some object is short of its own target. A real constraint remains (tank volume,
  use-side effectiveness, plant-loop flow) and **the campaign stays blocked until it is found.**

Pre-registered (full text in the head of `3rdJ_09H_hotel_dT_decompose.py`):

- **H9 PARTS** — every hotel use-type present in both cells delivers the same rise, within 0.5 K.
- **H10 WHOLE, and it is what stops H9 being vacuous** — the grid-MIN cell's per-type rises,
  re-weighted by the grid-MAX cell's volume shares, must reconstruct 63.55 K within 0.5 K.
  **H9 can pass while H10 fails**: matching parts whose mix arithmetic does not reproduce the gap
  means the gap comes from somewhere neither gate looked. **(A) requires H9 AND H10.**
- **H11 CONTROL** — the script's channel map is a second copy of the driver's (the driver builds it
  as a local and cannot be imported without refactoring a file closed arm H depends on), so it must
  reproduce the driver's hotel volume to 0.01 % **or refuse**. A second source of truth that checks
  itself against the first is tolerable; one that does not, is not.

Both sides are read at a K where the plant is provably non-binding, so the mix question is not
re-confounded with the capacity question.

### 0.12 🔴 THE K ESCALATION — **H5 PASS, H6 FAIL, H7 PASS, H8 PASS** (jobs 1172028 / 1172031)

| gate | verdict | evidence |
|---|---|---|
| **H5** CONTROL | **PASS** | hotel volume identical to arm H in all three tasks |
| **H6** DECISIVE | 🔴 **FAIL** | grid-MAX at K = 20 is **63.55 K** — below 65.0 K, 1.95 K off 65.50 K, and it *fell* 0.01 K from K = 10 |
| **H7** SATURATION | **PASS** | `dT(K=40) − dT(K=20) = 0.00 K` |
| **H8** POS. CONTROL | **PASS** | grid-MIN gain K = 10 → 20 is **0.00 K** — flatness discriminates, so H7 is not vacuous |

**This is the combination pre-registered as the most informative outcome: H6 fails while H7 passes.**

🔴 **H2's and H6's second clause was mis-specified, and that is NOT a licence to widen them.** Both
required the extremes to agree within 0.5 K *with each other*, on the premise that a uniform plant
must deliver the same temperature everywhere. H7+H8 falsify that premise: each cell has a stable
ceiling and the ceilings differ. **H2 and H6 stand as FAILED** — not re-scored, not re-aimed. What
changes is what may be *inferred* from them: they were built on a premise now shown false, so their
FAIL is evidence about the premise, not about the plant. A gate that fails because its reference was
wrong has still failed; the honest record is "failed, and here is why the reference was wrong".

🔴 **The same defect is already in the campaign pre-registration.** `C3` requires hotel ΔT constant
within 0.5 K across all 56 cells, *explicitly across geometry groups*. On this evidence C3 fails for
a non-plant reason. **It must be re-specified before the campaign runs — and on the measurement in
§0.13, never on the convenience of passing.**

### 0.12a Pre-registration for H5–H8 as submitted (do not edit)

Jobs **1172028** (array 0-2) + **1172031**. Grid-max cell at K = 20 and K = 40, plus a control.
Four **separately-numbered** gates — the conjunction habit that produced vacuous-gate #13 is
deliberately avoided; each gate carries exactly one claim.

- **H5 CONTROL** — hotel volume unchanged from arm H (≤ 0.1 %) in all three tasks.
- **H6 DECISIVE** — grid-max `sens_hotel_opt__SuperTall__MTL` at **K = 20** reaches **≥ 65.0 K** and
  is within **0.5 K of 65.50 K**. If K = 20 still falls short, the constraint in that cell is **not
  burner capacity** and no K fixes it — the search moves to `Tank Volume`, `Use Side Effectiveness`,
  or plant-loop flow, and the campaign stays blocked regardless of H7.
- **H7 SATURATION** — grid-max **`dT(K=40) − dT(K=20) < 0.5 K`**. This is the claim that a ceiling
  *exists*, separately from where it is. If ΔT still climbs at 40× capacity, `implied dT` is not
  tracking a delivered temperature approaching a setpoint and the whole "un-saturate the plant"
  framing is wrong. **H7 can fail while H6 passes — that would be the most informative outcome.**
- **H8 POSITIVE CONTROL, and it is what stops H7 being vacuous** — grid-MIN `B_cons__Tall__CLG`,
  already on the ceiling at K = 10 (65.50 K), re-run at **K = 20**; its gain must be **< 0.5 K**. If
  *it* also keeps climbing, "< 0.5 K gain" is not a property of saturation and H7 would have measured
  the instrument, not the plant.

Without H8, *"ΔT stopped moving"* and *"ΔT moves slowly at large K for every cell"* are the same
observation. **Unaffected by the open §0.11 question** — the gates are hotel-scoped and the hotel's
own heaters get the same multiplier under either resolution, so it was right to run it now.

### 0.10 🔴 HEADROOM RESULT, 2026-08-04 — **H2 FAILED**

Full write-up in the Progress Log (**6,532 lines**). Hotel-scoped, from `hdelast_1171859.out`:

| cell | r | arm H ΔT | K = 10 ΔT | move |
|---|---|---|---|---|
| `sens_hotel_opt__SuperTall__MTL` (**max**) | 1.2030 | 25.34 K | **63.56 K** | +38.22 |
| `B_cons__Tall__CLG` (**min**) | 0.9800 | 24.19 K | **65.50 K** | +41.31 |

| gate | verdict |
|---|---|
| **H1** CONTROL | **PASS** — hotel volume identical to 6 s.f. in both (34940.2 / 25061.8 unchanged) |
| **H2** DECISIVE | 🔴 **FAIL** — grid-max **63.56 K** < 65.0 K; extremes **1.94 K** apart vs 0.5 K tol. Both clauses fail, both on the same cell. |
| **H3** FALSIFIER | **PASS** — unresized 25.34 / 24.19 K, far below 40 K. H2 had ~40 K of room, moved +38/+41 K, and still missed. **Not vacuous.** |
| **H4** INFO | 887.2 kW (`SuperTall`, 11 heaters) vs 447.6 kW (`Tall`, 6). Not a grid constant. |

**Why 1.94 K is not noise.** The min-side cell landed on **65.50 K**, matching the `Tall__MTL` trio's
65.50/65.51/65.51 to the second decimal — a hard ceiling reproduced across four cells whose draw
differs 20 %. A cell sitting 1.94 K under a ceiling everything else hits exactly is not scattering
around it, it is still being held down. Physically: an **intermittent** binding, a few peak hours
still refused, which an annual mean almost entirely hides. That is why the residual looks small while
the mechanism is fully intact.

🔴 **`R3 PASS (1.4742)` and `R4 PASS (119.2 % of target)` in `hdelast_1171859.out` MUST NOT be
quoted.** The elasticity block there is N/A by construction and was pre-declared so: `R0 FAIL`
(1.8470 vs 0.5617) and `R3v FAIL` (volume elasticity 1.6208, not ~1.0) are the *expected* outcome,
because a 2-point E-vs-r fit across two cells differing in height, climate and scenario regresses
occupancy against geometry. The script's own trailer says it. Flagged because the log prints those
PASS lines in the same block as the real gates, and a later reader grepping `[PASS]` would collect
them.

### 0.10a Superseded — what the tower-wide read showed before 1171859 landed

| cell | geom | heaters | installed | arm H ΔT | K = 10 ΔT | ΔV |
|---|---|---|---|---|---|---|
| `sens_hotel_opt__SuperTall__MTL` (**max**) | SuperTall | **11** | 887.2 → 8,872.1 kW | 33.83 K | **57.39 K** | +0.0000 % |
| `B_cons__Tall__CLG` (**min**) | Tall | 6 | 447.6 → 4,476.0 kW | 31.87 K | **59.91 K** | +0.0000 % |

🔴 **These are TOWER-WIDE numbers and no H-gate is scored on them.** The verdicts live in §0.10.
Kept because the tower-wide series carries information the hotel-scoped one does not (below), and
because the near-miss recorded here — scoring a hotel threshold against a tower-wide ΔT would have
produced a FAIL that was *right by accident* — is the reusable lesson. Note the direction of the
error: the tower-wide read said 57.39 K, the hotel-scoped truth is 63.56 K. Same verdict, 6 K apart.
**A gate that lands on the correct verdict from the wrong quantity has not been validated.**

Every "4,476 kW" statement elsewhere in this file is `Tall`-scoped; `SuperTall` is 887.2 kW base.

The reference the threshold was built on is **hotel-scoped**. Same script, same cells,
65.50/65.51/65.51 reference H2's threshold was built on is **hotel-scoped**. Same script, same cells,
different quantity — at K = 10 the `Tall__MTL` trio reads **60.24 / 60.36 / 60.68 K tower-wide** and
**65.50 / 65.51 / 65.51 K hotel-scoped**. Substituting one for the other manufactures a confident
FAIL out of a units mismatch.

**What the tower-wide series does say.** K = 6 → K = 10 on the trio: 57.26 → 60.24, 54.04 → 60.36,
52.37 → 60.68 — still climbing 3–8 K, while hotel-scoped is already pinned to three identical digits
across cells whose draw differs 20 %. Consistent explanation: **hotel is un-saturated at K = 10 on
`Tall__MTL`; some non-hotel channel is not.**

### 0.11 🟢 RESOLVED BY THE USER, 2026-08-04 — **ALL-CHANNEL RESIZE**

**The user's decision, verbatim: "je voudrais continuer avec 'all-channel resize'".** `resize_idf()`
stays as written — it rewrites **every** `WaterHeater:Mixed` in the IDF, all four channels. No code
change is needed to implement this decision; what changes is what the campaign *claims* and what it
must therefore *report*.

**State this plainly wherever the campaign is written up — it is not a hotel-side correction on top
of an otherwise-unchanged arm H. It is a NEW ARM for residential, office, retail AND hotel.** §0.10
gives direct evidence the non-hotel channels are saturated too (tower-wide ΔT still climbing 3–8 K
from K = 6 → 10 on the `Tall__MTL` trio while hotel-scoped was already pinned), so the non-hotel
movement will be **large, not cosmetic**. Anything comparing a resized cell to arm H is comparing
across four moved channels at once, and every such comparison must say so.

**Three consequences that must be carried into the campaign, none of them optional:**

1. 🔴 **`C1` must be widened to all four channels.** As written it checks *hotel* volume unchanged
   ≤ 0.1 %. Under an all-channel resize, residential/office/retail volume is now equally exposed to
   an accidental draw change, and nothing would catch it. Checking only the hotel would be a gate
   that cannot fail for three quarters of what the intervention touches — the same defect class this
   project has now recorded thirteen times. **This is a strengthening, not a re-aim.**
2. 🔴 **A per-channel before/after record is owed, and it is INFO, not a gate.** Report resized −
   arm H DHW energy and volume for **each** of the four channels in all 56 cells. It is INFO because
   there is no pre-registered expectation for how far residential/office/retail should move — the
   honest position is to measure it, not to score it against a number invented after the fact. Call
   it `C6 INFO`. Do **not** promote it to a gate later on the strength of what it happens to show.
3. 🔴 **§0.3's magnitude warning now applies tower-wide, not hotel-wide.** Hotel DHW alone went
   2,578 → 7,008 GJ (×2.72) on one cell. With three more channels un-saturating, **tower EUI will
   move further than that figure implies**, and the hotel EUI band (§5b.5, still open) is no longer
   the only band this has to be re-validated against.

**What this decision does NOT settle:** the value of K (10, per the sweep) is unchanged and already
evidenced; the hotel EUI band, P3 and the Leg-2 corrigendum stay parked with the user (§2).

### 0.11a Original — the question as put to the user (do not edit)

`resize_idf()` rewrites **every** `WaterHeater:Mixed` in the IDF, not just the hotel's. The finding
that started this thread is *"hotel DHW plant undersized in every arm"*, and the minimal intervention
matching it is a **hotel-only** resize. As written, a resized campaign also moves residential, office
and retail DHW energy — so it is not a hotel-side correction on top of an otherwise-unchanged arm H,
it is a new arm for **every** channel. §0.10 suggests those channels really are saturated too, so the
difference is large, not cosmetic.

Both readings are defensible; they answer different questions. **This is the user's call**, same
character as P3 and the hotel EUI band: it decides what the deliverable claims. **The 56-cell
campaign is held on this in addition to H2.**

### 0.2 What is already established about the plant — the K sweep result

Jobs **1171837** (array, 6 runs) and **1171843** (elasticity). Same three `Tall__MTL` cells, same
estimator, same 0.90 threshold, nothing widened. Installed = 447.6 kW × K on six `WaterHeater:Mixed`;
**only `Heater Maximum Capacity` is scaled — `Tank Volume`, parasitics and loss coefficients are
untouched.**

| K | installed kW | hotel E-elasticity | ΔT(Y2022) | ΔT(B_central) | ΔT(B_opt) | marginal rise |
|---|---|---|---|---|---|---|
| 1 (arm H) | 447.6 | 0.5582 | 24.10 K | 22.85 K | 22.21 K | 12.91 K |
| 3 | 1,342.8 | 0.4403 | 39.15 K | 36.64 K | 35.31 K | 16.38 K |
| 6 | 2,685.6 | 0.3005 | 61.11 K | 56.27 K | 53.70 K | 17.22 K |
| **10** | **4,476.0** | **1.0013** | **65.50 K** | **65.51 K** | **65.51 K** | **65.55 K** |

- **R3 PASSES at K = 10** (1.0013 ≥ 0.90). **R0 re-derived and PASSED inside each K block** (0.5582
  vs the probe's 0.5617, tol 0.02) — that is what licenses quoting R3 at all. **R3v** (hotel volume
  elasticity 1.0007) holds at every K, so the energy elasticity really is measuring plant mediation.
- **K3, the discriminator, PASSES**: pre-registered ΔT(K=10) ≥ 47 K, measured **65.50 K**. **Burner
  capacity is CONFIRMED as the binding constraint.**
- **K2 and K4 FAIL as written** (both non-monotone). Recorded, not repaired. See vacuous-gate #13.
- 🔴 **This CORRECTS an inference logged earlier the same day.** The K = 3 result (elasticity moving
  the *wrong* way, 0.5582 → 0.4403) had been recorded as *"positive evidence against burner capacity
  being the binding constraint."* **That was wrong.** At K = 3 and 6 all three cells still saturate,
  and the extra capacity is absorbed preferentially by the *smallest*-draw cell (`Y2022`), which runs
  out of load first and converts the whole increment into temperature — flattening the E-vs-r slope
  and *lowering* the elasticity. The elasticity must dip before it snaps. Both entries stand in the
  log; the later one is the correction.
- **65.51 K is the model's own unconstrained mains-to-setpoint rise**, and it is *not* the 49.2 K
  (140 F) figure used as a target throughout. See §0.4 defect 2.

### 0.3 Two things that must be settled before the 56-cell campaign — **both now TOWER-wide, per §0.11**

1. **Magnitude.** Hotel DHW energy goes **2,578 → 7,008 GJ** on `Y2022__Tall__MTL` (**×2.72**). The
   resize is *efficiency*-neutral by the verified flat-PLF / constant-parasitic argument
   (`Part Load Factor Curve Name` empty → flat 0.803984; `Off/On Cycle Parasitic Fuel Consumption
   Rate` 8,146.58 W is a constant; tank volume untouched) — but it is emphatically **not
   magnitude-neutral**. Meeting more of the load is the whole point. **Tower EUI will move a lot and
   must be re-validated against the hotel EUI band — which is itself still unresolved (§5b.5).**
2. **Cost.** 56 cells × ~20–40 min. Confirm with the user before launching; the last 56-cell campaign
   was ~4 h wall at `array 0-55%20`.

### 0.4 Two defects found in the sizing work itself — both material, both unfixed

1. **The peak-draw sizing calc understated the requirement by ~3.4×.** It concluded K = 3.0 from a
   grid-max **hourly-mean** draw of 15.8878 m³/h at 71.4 K = 1,318.4 kW. Full un-saturation actually
   needed 4,476 kW. Hourly means cannot see the sub-hourly timestep peak or the tank-recovery
   dynamics that set the burner duty. **Any future sizing argument on this plant must be made on the
   simulation timestep, not on hourly aggregates.**
2. **`TARGET_K = 49.2` in `Step9_docs/3rdJ_09H_resize_elasticity.py:45` is MIS-SPECIFIED.** It is an
   assumed 140 F rise; the model's unconstrained rise is 65.51 K. That is why R4 at K = 10 reports
   "133.2 % of target" — the denominator is wrong, not the numerator. **Re-derive it from the IDF
   setpoint before R4 is quoted anywhere.**

### 0.5 R4 — **the denominator count is now RESOLVED by §0.14; the baseline count is not**

🟢 `TARGET_K = 49.2` is identified: it is the **140 F faucet** design rise, correct for that use class
and wrong as a hotel-aggregate denominator (the aggregate is 63.55–65.50 K). See §0.14 — **R4's
"% of target" must not be quoted until it is recomputed on a per-use or per-cell denominator.**
🔴 Still open: R4's 22.66 K baseline was never re-scoped hotel-side. The original text follows.

### 0.5a R4 is UNRESOLVED on two independent counts — do not score it

- **Baseline scope.** Its pre-registration reads *"rises from arm H's 22.66 K toward the 49.2 K
  target"*, but the coded gate tests `mR > mH` against a **recomputed** 12.91 K baseline. Against the
  written 22.66 K the K = 3 result would have *failed*. The 22.66 K reference (job 1171767) has never
  been re-scoped hotel-side. R3 has an R0 control precisely because this was anticipated for R3 and
  not for R4.
- **Wrong denominator.** §0.4 defect 2.

### 0.7 🔴 `SuperTall` has **11** heaters, not 6 — "447.6 kW" is a `Tall` number

The first headroom attempt (`1171855_0`) refused in 2 s:
`REFUSING: expected 6 Heater Maximum Capacity fields, rewrote 11`. **The guard was right and the
constant was wrong.** `N_HEATERS = 6` was measured on `Tall`; `SuperTall` carries 11
`WaterHeater:Mixed`.

- **Every "installed = 447.6 kW" / "4,476 kW at K = 10" statement is scoped to `Tall` cells.** The
  K-sweep result stands (all three swept cells are `Tall__MTL`, internally consistent); what was
  never measured is the extrapolation to the grid's 28 `SuperTall` cells.
- **Fixed:** the count is now read per-IDF and the guard asserts *"every heater the IDF declares was
  rewritten"*. A guard whose reference encodes an assumption about the stock cannot detect that the
  assumption is wrong — vacuous-gate #9, displaced one step into the author's head. The installed
  base is now printed (`PLANT_BASE kW_base=... kW_resized=... n_heaters=...`) and the summary labels
  carry the cell's own capacity instead of a hard-coded 447.6.
- **This does NOT break the user's decision.** `K` multiplies each cell's own base, so different
  *geometries* land on different absolute kW — but the user's requirement was that the **occupancy**
  axis must not buy capacity (`B_opt` must not out-boiler `B_cons`), and within any geometry group
  every scenario gets an identical plant. Geometry already differs in floors, area and zone count.
  And once the plant is non-binding, ΔT goes constant and capacity drops out of the answer entirely
  — which is exactly what H2 tests. **Run the check; do not redesign the intervention.**

### 0.8 🔴 Vacuous-gate #10 recurred **in this project's own harness**

`headroom_check.sh` ended with `echo "  probe exit=$?"` as its last line, so the job exited with
**`echo`'s** status — always 0. `1171855_0` died on the refusal above and SLURM reported **COMPLETED
in 2 s**, releasing the `afterok` dependent (1171857) to run against output that did not exist.

Second occurrence on this project after `smoke_f9fix.sh:47`. The earlier repo-wide sweep that found
"exactly one occurrence" was correct **for the code that existed then** — the pattern was
reintroduced by hand in new scripts the same week. **A sweep certifies a snapshot, not a habit.**
Fixed in `headroom_check.sh` and `resize_sweep.sh` (`RC=$?; echo ...; exit $RC`).
**Never make a bare `echo` the last line of a job script.**

### 0.9 🟢 SUBMITTED 2026-08-04 as job 1172037 (+ scorer 1172045). Section kept for the reasoning.

*(The three edits below were done — plus a fourth, `C2` → `C2′`, forced by the discovery that `C2`
as written could not fail. See §0.15. What follows is the state before submission.)*

### 0.9 🔴 The 56-cell campaign is WRITTEN, UPLOADED and HELD — the hold condition has CHANGED

**Superseded trigger.** The old rule was "submit if H2 passes". H2 **failed**, but the plant question
it was asking is now answered by H7/H9/H10/H11 — the plant is non-binding at K = 10 everywhere. So
the plant is no longer what holds the campaign, and **§0.11 is now answered (all-channel)**. What is
left is **three script edits, all mechanical, none of them a decision:**

1. 🔴 **`C3` → `C3′` in `resize_campaign.sh`** (§0.13). Submitting with C3 as written bakes in a gate
   that fails every run for a non-plant reason. Tooling exists —
   `3rdJ_09H_hotel_dT_decompose.py` already emits the per-type table and the reconstruction.
2. 🔴 **`C1` widened from hotel-only to all four channels** (§0.11 consequence 1).
3. 🔴 **`C6 INFO` added** — per-channel resized − arm H DHW energy and volume, all four channels, all
   56 cells (§0.11 consequence 2). INFO, never a gate.

**Do the edits, re-read the pre-registration block in the script header so it matches what the script
actually evaluates, then submit.** Do not submit on the old trigger, and do not submit with the
header and the code disagreeing — a pre-registration that does not match the code is not a
pre-registration. The original section follows for the file paths and the exact submit command.

### 0.9a Original — campaign written, uploaded, held

`Step9_docs/3rdJ_09H_resize_campaign_cell.py` + `Step9_docs/resize_campaign.sh` (`--array=0-55%20`),
both on the cluster. **Submit with:**
`ssh speed "cd /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs && sbatch resize_campaign.sh"`
→ output `campaign/out_R_resize/K10`.

Design, so the next session does not have to re-derive it:
- **It is a post-process of arm H, not a new injection.** Each cell starts from arm H's own
  `injected.idf`, changes `Heater Maximum Capacity` and nothing else, and re-runs. `INJ_HASH` and
  `INPUTS_HASH` are inherited unchanged, which is what makes "resized − arm H" a one-variable
  comparison. Re-running the injector would risk moving a second variable.
- **It reuses `_do_postprocess()` from `3rdJ_08P_probe_driver.py`**, so `hourly_meters.csv`,
  `channel_hourly.csv`, `dhw_hourly.csv` and `dhw_volume_hourly.csv` come from the campaign's own
  writers with the same channel resolution and fuel-closure tripwire. No second set of extractors.
- **The manifest is inherited and stamped**, never invented: `RESIZE_K`, `PLANT_KW_BASE`,
  `PLANT_KW_RESIZED`, `PLANT_N_HEATERS`, `RESIZE_SOURCE_CELL`. A resized cell cannot be misread as
  an arm-H cell.
- **The cell list is `ls`-ed from the arm-H tree**, not typed out — a hand-written list of 56 names
  is a second source of truth that drifts. EPW follows the cell's own `__MTL`/`__CLG` token.

**Pre-registered in the script header, before submission:** `C1` volume unchanged ≤ 0.1 % in all 56;
`C2` `INJ_HASH` identical + area delta 0 m²; **`C3` DECISIVE — hotel delivered ΔT constant across all
56 cells within 0.5 K** (strictly more than the K sweep or H2 established, because it must hold
*across* geometry groups); **`C4` DECISIVE — hotel energy elasticity ≥ 0.90 in 4/4 (geometry, city)
groups**; `C5` INFO — EUI shift, deliberately **not** a gate because the hotel band question is still
open with the user. **Read C3 first: C4 is only meaningful if C3 holds.**

### 0.6 Also owed in writing

**R2's ordering sub-clause is recorded as mis-specified and the re-specification has not been done.**
Same family as K2/K4 (vacuous-gate #13). Write it, or mark it explicitly `N/A`.

---

## 1. Files and jobs from the resize thread

**New 2026-08-03 (all uploaded to the cluster repo):**
`Step9_docs/3rdJ_09H_plant_resize_probe.py` (surgical K-scale + EnergyPlus run; refuses unless
exactly 6 `Heater Maximum Capacity` fields are rewritten and `Tank Volume` survives),
`Step9_docs/3rdJ_09H_resize_elasticity.py` (hotel-scoped R0/R3/R3v/R4; imports
`_write_dhw_hourly_csv` from the Step-8 campaign driver so channel resolution has ONE source of
truth), `Step9_docs/resize_elasticity.sh`, `Step9_docs/resize_sweep.sh`,
`Step9_docs/resize_sweep_elast.sh`, **`Step9_docs/headroom_check.sh`**,
**`Step9_docs/headroom_elast.sh`**.

**Cluster paths:** arm-H cells `campaign/out_H_allfix/campaign_233932d7`; resize outputs
`campaign/resize_probe` (K=3), `campaign/resize_sweep/K6`, `.../K10`, `campaign/headroom/K10`.
Repo copy `campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/`. Logs in `campaign/logs/`.

**Jobs, 2026-08-03 resize thread:** 1171802 (`Autosize` + `Time for Tank Recovery = 0` → **fatal**,
refuted), 1171805/1171806 (peak-draw measurement, per-cell and grid-wide), 1171807 (K = 3 probe),
1171812 (**crashed** — the silent-default reader, vacuous-gate #12), 1171835 (K = 3 elasticity, R3
FAIL), 1171837 + 1171843 (**K sweep, R3 PASS at K = 10**), **1171855 + 1171857 (headroom, in flight)**.

---

## 2. Everything else — parked, unchanged from 2026-08-03

For full detail read `3rdJ_L3_manager_prompt_2026-08-03.md` §§ 3–6. Summary of what is still open:

### 🔴 Waiting on the USER — do not decide these yourself

1. ~~**The plant resize itself** — scope and launch.~~ **CLOSED 2026-08-04.** Method = uniform
   hard-size (chosen earlier); **scope = all-channel (§0.11)**; K = 10 (evidenced by the sweep, §0.2,
   and shown non-binding by H7/H8). Nothing about the resize is waiting on the user any more — see
   §0.9 for the three script edits that remain, all mechanical.
2. **How to re-specify P3.** It predicted a *volume* change and scored it against an *energy*
   measurement on a saturated plant. The remedy is re-specification (predict volume — which T9-13
   delivers at elasticity 1.0000 — or predict energy through an explicit plant model). That changes
   declared gate semantics, so it is the user's call. **The band must not be widened.**

### Open items — flagged, not fixed

1. **`F30 HOTEL_BOT_LAUNDRY`, 1.9 %.** Peak-flow rescale excluded by measurement (job 1171446).
   Remaining candidate: plant-loop coupling with the main `LAUNDRY` draw. **Untested.**
2. **T9-12's `k = 0.60` needs re-checking** after the FINDING 7 retail rewire. Arm H runs the
   un-retuned `k`, so any arm-H retail lighting result is provisional.
3. **The hotel EUI band question is still open and still blocking `S9-EUI-hotel`.** R1 says
   `[240,300]` → 0/56; R2 (NECB 2017 / CanmetENERGY 2020) says `[140,220]`/`[160,240]`. Tie-breaker:
   **is the CanmetENERGY NECB 2017 hotel archetype full-service or limited-service?** Needs the
   *Commercial Archetypes Performance Study* (2020), not in `deepResearch/`. Adopting R2 before
   reading it would be choosing the band that rescues the gate. **This now interacts with the resize
   (§0.3.1) — the resize moves hotel EUI substantially, so settle the band before re-validating.**
4. **Decision 5 (Leg-2 office-EUI corrigendum)** needs one bounded read-only job against Leg-2's own
   `eplusout.sql`. `172.7 / 1.706 ≈ 101.2` is an indication of magnitude, **not a derived value**.
   Never claim the published band was affected — checked and refuted.
5. **The `Y2022` office channel (+28.6 % at r ≈ 1.0)** — an attribution question; re-measure in arm H
   before theorising.
6. **The 3 Step-9 EUI FAILs** stay FAIL and stay explained-but-not-rescued.
7. **B-3** — the only high backward-audit finding still needing compute. The other two high findings
   closed on writing (R1/R2/R3 reports, 2026-08-03 eve, all clean negatives). **B-11 upgraded**:
   retail zones are 25.0 m²/person (= office), docs claim ~3.7 — a 6.8× gap, and the "0.95 NECB
   retail peak" is actually the OFFICE peak. The injector itself is vindicated (0.9215 = 0.95 × 0.97
   exactly). Files at `improvements/investigation/`. **Still no falsifier run.**
8. Neither `D8` nor `D9` can catch a defect in `_schedule_daytype_profiles` itself. The independent
   guard is `Step9_docs/3rdJ_09F_daytype_loss.py` — keep running it after any change to the readers.

---

## 3. Useful commands

On the cluster (single line each):
- `ssh speed "sacct -j 1171855,1171857 -n -X -o JobID,State,Elapsed"`
- `ssh speed "cat /speed-scratch/o_iseri/step8_4split/campaign/logs/hdelast_1171857.out"`
- `ssh speed "grep -E 'CELL |peak \(max\)' /speed-scratch/o_iseri/step8_4split/campaign/logs/peakAll_1171806.out | paste - - | sort -k5 -n -r | head -5"`
  — ranks all 56 cells by peak hourly draw. One `ssh` per call; do not nest.

Locally:
- `py -3 3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09G_finding9_verify.py --falsify`
  — ~3 min, no cluster; needs `EPLUS_IDD` = `C:/EnergyPlusV24-2-0/Energy+.idd`. Note `py`, not
  `python` — on this Windows box `python`/`python3` are Microsoft Store stubs.
- `cd 3J_docs_occ_nTemp/improvements && wc -l 3rdJ_L3_improvements_step9.md` before every append.
