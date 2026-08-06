# Manager prompt — 3J Leg-3 Step 9, **2026-08-05** (LIVING PROGRESS FILE)

Paste this whole file as the first message of a fresh session. It is self-contained.

> **This file is a LIVING HANDOFF and is updated at every step of the work, not once at end of day.**
> The user starts a fresh manager session most mornings, and may start one at any moment. Whatever
> state the work is in when a new session opens, this file must already describe it. Predecessors:
> `3rdJ_L3_manager_prompt_2026-08-04_progress.md` (the whole resize thread — still the reference for
> §§0.1–0.17 detail, the K sweep, the H1–H11 gates and why `H2`/`H6`/`C3` stand failed),
> `..._2026-08-03.md` (arm H closure, §§4–6), `..._2026-08-03_PRE-ARMH.md`, `..._2026-08-02.md`,
> `..._2026-08-01.md`.
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
  **A loop of greps over 56 files is not a single-file peek — put it in a job** (that is what
  `resize_hotel_r_census.sh` is, and it cost 2 seconds of compute).
  The login shell is **tcsh** — no `for` loops, no `2>&1`, **no `2>/dev/null`**, one short line.
  - 🔴 **`2>/dev/null` inside `ssh speed "..."` is a tcsh parse error** ("Ambiguous output redirect")
    and it does **not** fail loudly — stdout comes back empty and the caller reads that as "no
    result". On 2026-08-03 a poll loop built this way reported an empty job state 40 times over 3.3 h
    and never noticed the job had finished in 29 min. Do not suppress stderr on the cluster.
  - 🔴 **Nested `ssh speed "... ssh speed \"...\" "` fails with `Permission denied (publickey)`.**
    One `ssh` per Bash call.
- **Every job requests `-t 7-00:00:00` minimum.** No exceptions, even for one-minute probes.
- Cluster commands single-line, each labelled "locally" or "on the cluster".
- **Never widen a band or relax a gate to erase a FAIL.** The remedy is re-specification or an
  explicit `N/A`. A gate counts as validation only once it has been *seen failing*; write the
  falsifiable prediction **before** running the test. **A miss is recorded, not repaired.**
- 🔴 **Vacuous / mis-specified tests are the recurring failure on this project.** Before recording
  any PASS, ask: *what result would have made this fail?* The catalogue runs to **thirteen** kinds.
  - **#12 — the default that cannot be distinguished from a measurement.** *This one came up again on
    2026-08-04 and was designed around rather than fallen into — the pattern to copy.* The hotel `r`
    reader needed a value for 16 cells whose hotel channel was never injected, and the correct value
    is exactly `1.0` — which is **also** a perfectly legitimate measured `r`. A silent fallback would
    have been indistinguishable from a real reading. The fix: assert the state **positively** on six
    hotel-specific conditions, **name every cell that took that path on the scorecard**, and
    hard-refuse anything that is neither tokened nor fully asserted. See §1.3.
  - **#11** the gate measuring a quantity the deliverable discards · **#13** the conjunction gate, and
    the monotonicity clause across a saturation boundary · **#9** the gate whose reference comes from
    the same source it audits · **#10** the gate reading the wrong process's exit code (swept
    repo-wide, one occurrence, fixed — **do not re-run that sweep**) · **silence is a failure mode**,
    a reader returning 0.0 for input it cannot parse blames the simulation for its own gap (cost 16
    spurious FAILs in job 1171607; every reader must itemise what it could not read, the `G4` pattern).
  - **A gate can be real and still not prove what it is quoted for.** Arm H's `G2` is structurally
    invariant under T9-13 because `r_we` cancels — it separates "FINDING-9-fixed injector" from
    "pre-fix injector", **not** "injected" from "not injected". `G1` is the one that shows injection
    reached the model.
- **A local `py_compile` is NOT a valid syntax check for cluster code.** Local Python is **3.13**,
  the cluster env is **3.10.20**. Compile inside the job, under `$PY`, and refuse to run if it fails.
- **Do not append to the Progress Log with PowerShell `Add-Content`.** PS 5.1 `Get-Content` reads a
  UTF-8 file as ANSI and double-encodes the insert. Append with bash `cat >>`. **If a heredoc fails
  to parse on a long block, write it to the scratchpad with Write and `cat scratch >> target`.**
- **Verify every number you inherit.** Re-derive from the artefact's own columns. **Including numbers
  from earlier in this same log** — it is append-only, so an early section can be flatly contradicted
  by a later one. **The last statement wins; grep forward before quoting.**
- 🔴 **Never count lines with PowerShell.** `Measure-Object -Line` counts an empty line as zero.
  Use `wc -l` via the Bash tool, always.
- **Update the Progress Log live.** `3J_docs_occ_nTemp/improvements/3rdJ_L3_improvements_step9.md`,
  **7,003 lines** (`wc -l`, 2026-08-04 10:45). Read the last ~400 counted from the real total.
- 🔴 **Never make a bare `echo` the last line of a job script.** `RC=$?; echo ...; exit $RC`.
- **Leg-2 is closed and paper-ready — no file under `Leg2_2-split/` may be modified.** Reading its
  IDFs and `eplusout.sql` is fine.
- All documents in English; reply to the user in English even though they write French. Keep replies
  short (≤ 100 words unless detail is asked for).
- Cheap models for mechanical work; minimum monitoring interval 30 min; never poll in a tight loop.
  A plain background `Bash` waiter costs no model tokens and is the preferred way to wait on a job.

---

## 0. 🔴 WHERE THE WORK STANDS — read this first

**STATE (2026-08-04, 11:15 EDT): the resized DHW campaign RAN, LANDED 56/56, and SCORED 6/6 PASS.**
**Four user decisions were taken the same day (§2.1). §8E aggregation of the resized arm is IN
FLIGHT as job `1172148` — poll it first.**

# 🟢 **THE PLANT QUESTION IS CLOSED.** K = 10 un-saturates the DHW plant across the whole grid.
# 🔴 **FIRST TASK OF THE NEXT SESSION: write the Step-9 re-score predictions BEFORE running it.**
The re-score scores gates, so its falsifiable predictions go into the Progress Log **first**. The
aggregation (`1172148`) is mechanical and carries no gate, which is why it could be launched without
them.

| job | what | outcome |
|---|---|---|
| ✅ `1172037` | 56-cell resized campaign, K = 10, all-channel, `--array=0-55%20` | **56/56 COMPLETED**, zero FAILED/CANCELLED/TIMEOUT/NODE_FAIL; 20–60 min/cell |
| ❌ `1172045` | scorecard, `--dependency=afterany:1172037` | FAILED 1:0 — `r` reader had no case for `Default_NECB__*` |
| ❌ `1172108` | scorecard, re-submit | FAILED 1:0 — fix asserted **whole-cell** untreatedness, refused on `Y2005__*` |
| ✅ `1172109` | hotel-DHW census of all 56 cells (pure grep, 2 s) | COMPLETED — population exactly bimodal, 40 / 16 |
| ✅ **`1172110`** | **scorecard, final** | **COMPLETED 0:0 — all six gates PASS, 56/56 cells** |

### 0.1 🟢 THE SCORECARD

```
  SCORECARD  C1' PASS   C2' PASS   C3a PASS   C3b PASS   C4 PASS   C4c PASS     56 / 56 cells
```

- **`C3a` DECISIVE — the 22.66 K marginal-rise defect is CLOSED.** Every hotel use-type in every cell
  delivers its design rise (49.19 K at 140 F, 71.40 K at 180 F, tol 0.5 K). 0 type violations,
  0 unreadable design targets. Derived and **not** scored: worst |aggregate − mix reconstruction|
  **0.0324 K** on `B_opt__Tall__MTL`.
- **`C4` DECISIVE** — hotel DHW energy elasticity by (geometry, city) group:

  | group | n | n_r | arm H e | resized e | R² |
  |---|---|---|---|---|---|
  | `SuperTall__CLG` | 14 | 5 | 0.6470 | **1.0013** | 1.000 |
  | `SuperTall__MTL` | 14 | 4 | 0.6431 | **1.0014** | 1.000 |
  | `Tall__CLG` | 14 | 5 | 0.5830 | **1.0014** | 1.000 |
  | `Tall__MTL` | 14 | 4 | 0.5779 | **1.0015** | 1.000 |

- `C4c` CONTROL PASS — no group was already ≥ 0.90 in arm H, so `C4` discriminates.
- `C1'` CONTROL PASS — DHW **volume** unchanged ≤ 0.1 % in all four channels, 0 violations, 0 unreadable.
- `C2'` CONTROL PASS — resized IDF differs from arm H's **only** on `Heater Maximum Capacity` lines.
  **Burner capacity only; tank volume was NOT resized.**

### 0.2 🔴 TWO CAVEATS — DO NOT QUOTE THE 1.00 CLEAN

1. **`C4` is only WEAKLY independent of `C3a`.** Once every use-type delivers its design rise and
   volume scales exactly with `r` (which `C1'` shows, and which is structural — the draw is
   schedule-driven and cannot see the burner), then `E = V·ρc·ΔT_design ∝ r` follows arithmetically.
   `C3a`'s 0.5 K tolerance is ~1 % of 49.19 K, which over a log-`r` span of ~0.18 leaves ≈ ±0.06 of
   slope — so `C4` *could* have landed 0.94–1.06 with `C3a` still passing. The window where `C3a`
   passes and `C4` fails is real but **narrow**. **`C4` is a confirmation, not a second independent
   measurement**; its DECISIVE standing comes from `C4c`. Same family as the `C3'` second clause
   already demoted to derived-not-scored.
2. **`n_r` = 4–5 distinct `r` per group, not 14.** `sens_office_*` and `sens_retail_*` vary
   office/retail and inherit their base scenario's hotel `r`; 4 cells sit at exactly `r = 1.0`. So
   R² = 1.000 is across 4–5 distinct x with replication, not 14 free points. The `n_r` column was
   added precisely so this cannot hide behind an `n = 14` label.

### 0.3 🔴 THE SUBSTANTIVE FINDING — THE UNDERSIZING WAS **NOT HOTEL-ONLY**

`C6` INFO, resized − arm H, 56 cells:

| channel | ΔE min % | ΔE median % | ΔE max % | ΔV max % |
|---|---|---|---|---|
| hotel | +134.70 | **+170.79** | +194.99 | 0.0000 |
| residential | +4.39 | **+11.30** | +13.91 | 0.0000 |
| office | −0.04 | −0.03 | −0.01 | 0.0000 |
| retail | −0.04 | −0.00 | −0.00 | 0.0000 |

Full table → `out_R_resize/K10/C6_per_channel_delta.csv`. **Volume is flat to 4 dp in every channel**,
so all of this is delivered-energy recovery, not extra draw.

**Residential DHW was plant-limited by 4–14 %. That was NOT part of the hotel 22.66 K diagnosis and
was not predicted by anyone.** Office and retail never bound (the −0.03 % is cycling noise, not a
real reduction). 🔴 **`C6` STAYS INFO** — no expectation for the non-hotel channels was
pre-registered, and a number scored against an expectation invented after seeing it is not a test.
Do not promote it on the strength of what it shows.

`C5` INFO — whole-tower all-fuel site energy vs arm H: **+10.95 % min** (`Default_NECB__SuperTall__MTL`)
/ **+18.93 % median** / **+24.69 % max** (`B_opt__Tall__CLG`). Floor area is unchanged by construction
(`C2'`), so the % shift **is** the EUI shift.

🔴 **This makes the resized arm a materially different building. Every comparison in this campaign
moves four channels at once — it is a NEW ARM for residential, office, retail and hotel, not a
hotel-side correction on top of arm H. Anything written up from it must say so.**

---

## 1. What was built, and the one thing that went wrong

### 1.1 Files changed / created 2026-08-04

- `Leg3_4-split/Step9_docs/3rdJ_09H_resize_elasticity.py` — new `hotel_r_with_source()`; `hotel_r()`
  is now a thin float-only wrapper.
- `Leg3_4-split/Step9_docs/3rdJ_09H_resize_campaign_score.py` — `C4` names every non-token `r`
  source, new `n_r` column, header note recording the reader fix.
- `Leg3_4-split/Step9_docs/resize_hotel_r_census.sh` — **new**, pure grep, no python.
- `Leg3_4-split/Step9_docs/resize_campaign.sh`, `resize_campaign_score.sh`,
  `3rdJ_09H_resize_campaign_cell.py` — as submitted, unchanged since.

### 1.2 Where the outputs are

- resized cells → `/speed-scratch/o_iseri/step8_4split/campaign/out_R_resize/K10/`
- arm H cells → `.../out_H_allfix/campaign_233932d7/`
- scorecard log → `.../logs/resizescore_1172110.out`; census → `.../logs/hotelrcensus_1172109.out`

🔴 **There is NO `agg_R_*` directory.** Verified by `ls` on 2026-08-04: every other arm has one
(`agg_A_t99`, `agg_B_lm3`, `agg_C_lm3v2`, `agg_D_full`, `agg_E_dhwvol`, `agg_H_allfix`) and the
resized arm does not. **The resized arm has never been through §8E aggregation, so NO Step-9 gate has
been scored on it** — not `S9-EUI-*`, not `G8o/G8r/G8h`, not `S9-LONG-*`, none. The scorer read cells
directly. **This is the prerequisite for anything downstream** and it is one job
(`3rdJ_08E_aggregate_4split.py`, pattern = `agg_armE.sh`).

### 1.3 The reader fix — **no gate was touched**, and why it took three jobs

`C1'/C2'/C3a/C3b` do not call the `r` reader and were **byte-identical across all three scorer runs**.
No gate, threshold, tolerance or grouping was modified at any point.

- `1172045` refused on `Default_NECB__*` — never DHW-injected at all, so no
  `MXU_Hotel_DHWv2_..._r####w####` token to read.
- `1172108` asserted **whole-cell** untreatedness and then refused on `Y2005__*` — hotel absent from
  `channels_requested` but `n_dhw_applied=47` for the other three channels. **A cell that injected 47
  DHW schedules is plainly not untreated. The scope was wrong, not the strictness.**
- `1172109` censused all 56 cells instead of guessing again. Population **exactly bimodal**,
  `n_dhw_unresolved=0` throughout, no third state:

  ```
  40  hotel injected        4 MXU schedules + one `t9_13 hotel` line -> r from the token
  16  hotel never injected  hotel absent from channels_requested, present in fallback_channels
      = 4  Default_NECB__*        (nothing injected at all, n_dhw_applied=0)
      + 12 Y2005/Y2010/Y2015__*  (hotel-era exclusion, QC hotel truth starts 2019;
                                  other three channels injected, n_dhw_applied=47 or 31)
  ```

Those 16 run the untouched NECB hotel schedule, which **is** the `baseline_series` that every other
cell's `r` is measured against — identical `reference_occ_mean` hotel `wd=0.357275 we=0.368193` in
the treated and untreated provenances alike. So `r = 1.0` is a fact read off the file, and they are
each group's **anchor point** (4 per group), not cells to drop.

**Lesson worth keeping: when a reader refuses, census the population before patching it.** Two jobs
were spent guessing from one sample; the census cost 2 seconds and settled it.

---

## 2. USER DECISIONS — **four answered 2026-08-04, one still open**

### 2.1 ✅ ANSWERED 2026-08-04 — act on these, do not re-ask

1. **Which arm is the deliverable → DECIDE AFTER SEEING R's STEP-9 GATES.** Deliberately deferred.
   Arm H is what all Step-8/9 analysis rests on and has a *known physical defect*; arm R fixes it but
   is a new arm for four channels and moves the tower ~19 %. The user will not choose between them on
   the resize scorecard alone — the choice waits on R's own `S9-EUI-*` / `G8*` / `S9-LONG-*` results.
   🔴 **Do not write either arm up as primary until this is settled.**
2. **What runs next → §8E AGGREGATION + STEP-9 RE-SCORE ON R.** Aggregation **LAUNCHED as job
   `1172148`** on 2026-08-04 (see §2.3). The Step-9 re-score is **NOT** launched, on purpose: it
   scores gates, so its falsifiable predictions must be written into the Progress Log **before** it
   runs. That is the first task of the next session.
3. **Hotel EUI band → FIND AND READ THE CANMETENERGY STUDY FIRST.** Do not adopt R2's
   `[140,220]`/`[160,240]` until the *Commercial Archetypes Performance Study* (2020) settles whether
   the NECB 2017 hotel archetype is **full-service or limited-service**. It is not in `deepResearch/`.
   🔴 **Adopting R2 without it is choosing the band that rescues the gate.** Until then
   `S9-EUI-hotel` stays scored against R1 `[240,300]` and stays FAIL.
4. **P3 re-specification → PREDICT VOLUME.** Score what T9-13 actually delivers — volume, at
   elasticity 1.0000 — instead of energy through a saturated plant. **The band must not be widened**,
   and the re-specification must be written down before it is scored.

### 2.2 🔴 STILL OPEN — waiting on the user

5. **Decision 5 — the Leg-2 office-EUI corrigendum.** Needs one bounded read-only job against Leg-2's
   own `eplusout.sql`. `172.7 / 1.706 ≈ 101.2` is an indication of magnitude, **not a derived value**.
   Never claim the published band was affected — checked and refuted. Leg-2 stays read-only.

### 2.3 🟡 QUEUED — job `1172151`, §8E aggregation of the resized arm

`Step9_docs/agg_armR.sh` → `campaign/agg_R_resize`. **First action of the next session:**
`ssh speed "sacct -j 1172151 -n -X -o JobID,State,ExitCode,Elapsed"`, then
`tail /speed-scratch/o_iseri/step8_4split/campaign/logs/aggR_1172151.out`.

🔴 **The account is CPU-starved by work that is not this project's.** `sacctmgr` gives
`cpu=32`, and an unrelated 32-task array named **`qc1983nu` (jobs `1172111` / `1172112`, 1 CPU each,
7-day walltime)** is holding all 32 with more tasks queued behind. Submitted around the same time as
the scorer (their IDs sit between `1172110` and `1172148`) but **not by this project's work — do not
cancel them without asking the user.** First submission `1172148` asked for 4 CPUs and would have had
to wait for four simultaneous free slots; **cancelled and resubmitted as `1172151` at 1 CPU** (user's
instruction), which backfills as soon as a single `qc1983nu` task ends. 8E walks the 56 cells
sequentially, so the extra CPUs bought nothing.

**Local fallback, if Speed stays blocked** (the user raised it): it needs the cell data, which lives
on `/speed-scratch`. Measured on `B_opt__Tall__MTL`: `run/eplusout.sql` **161.7 MB** +
`hourly_meters.csv` 2.1 MB per cell → **≈ 9.2 GB over scp for all 56**, since 8E opens each cell's
SQL (`parse_channel_areas`, `read_calendar`). Viable but slow, and the local box cannot be rebooted
remotely — prefer waiting for the 1-CPU backfill unless the block lasts hours.

Three things about it that differ from every previous arm, all deliberate and documented in the
script header:

- **No `campaign_<hash>/` level.** The resized tree is `out_R_resize/K10/<cell>/` directly, because
  each cell is a post-process of arm H rather than a fresh injection. Arm E's hash guard cannot
  apply; §1 of the job asserts the arm-H tree the cells were built *from* instead.
- **No T9-13 audit sweep.** Every `injected.idf.provenance.txt` in the resized tree is **copied from
  arm H** — the resize does not re-inject. Re-running the P1 shape sweep here would re-measure arm H
  and report it as a property of arm R: **vacuous-gate #9**, the gate whose reference comes from the
  source it audits. Arm H's sweep already passed and stands.
- **`3rdJ_08E_aggregate_4split.py` gained `--idf-name`** (default `injected.idf`, so all six earlier
  arms are byte-identical). The resized cells write `injected_resized.idf` and `injected.idf` does
  not exist there. 🔴 **Deliberately not solved with a symlink named `injected.idf`** — in every
  other arm that name means "arm H's injected IDF", and a later reader diffing `injected.idf` across
  arms would silently compare a resized IDF against an unresized one and read the burner-capacity
  change as an injection difference. A flag says what is happening; a same-named symlink hides it.

---

## 3. Open items — flagged, not fixed

1. **`F30 HOTEL_BOT_LAUNDRY`, 1.9 %.** Peak-flow rescale excluded by measurement (job 1171446).
   Remaining candidate: plant-loop coupling with the main `LAUNDRY` draw. **Untested.**
2. **T9-12's `k = 0.60` needs re-checking** after the FINDING 7 retail rewire. Arm H runs the
   un-retuned `k`, so any arm-H retail lighting result is provisional — **and so is the resized
   arm's, since it inherits arm H's schedules unchanged.**
3. **B-3** — the only high backward-audit finding still needing compute. The other two closed on
   writing (R1/R2/R3, 2026-08-03 eve, all clean negatives). **B-11 upgraded**: retail zones are
   25.0 m²/person (= office), docs claim ~3.7 — a 6.8× gap, and the "0.95 NECB retail peak" is
   actually the OFFICE peak. The injector itself is vindicated (0.9215 = 0.95 × 0.97 exactly).
   Files at `improvements/investigation/`. **Still no falsifier run.**
4. **`R4`'s 22.66 K baseline was never re-scoped hotel-side.** Now moot for the resized arm (`C3a`
   supersedes it) but **still open for arm H**, which matters if arm H stays the deliverable.
5. **`R2`'s ordering sub-clause** is still owed in writing or an explicit `N/A`.
6. **The `Y2022` office channel (+28.6 % at r ≈ 1.0)** — an attribution question; re-measure in arm H
   before theorising.
7. **The 3 Step-9 EUI FAILs** stay FAIL and stay explained-but-not-rescued.
8. **`H2`, `H6` and `C3` stand on the record as FAILED / mis-specified.** None was re-aimed, none was
   re-scored. A gate failing because its reference was wrong has still failed.
9. Neither `D8` nor `D9` can catch a defect in `_schedule_daytype_profiles` itself. The independent
   guard is `Step9_docs/3rdJ_09F_daytype_loss.py` — keep running it after any change to the readers.

---

## 4. Useful commands

On the cluster (single line each, one `ssh` per call, never nested):
- `ssh speed "sacct -j <ids> -n -X -o JobID,State,ExitCode,Elapsed"`
- `ssh speed "cat /speed-scratch/o_iseri/step8_4split/campaign/logs/resizescore_1172110.out"`
- `ssh speed "ls /speed-scratch/o_iseri/step8_4split/campaign/"` — arm directories and aggregations
- Submit: `ssh speed "cd /speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs && sbatch <script>.sh"`
- Upload: `scp <files> speed:/speed-scratch/o_iseri/step8_4split/campaign/repo/3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/`

Locally:
- `cd 3J_docs_occ_nTemp/improvements && wc -l 3rdJ_L3_improvements_step9.md` before every append.
- `py -3 3J_docs_occ_nTemp/Leg3_4-split/Step9_docs/3rdJ_09G_finding9_verify.py --falsify`
  — ~3 min, no cluster; needs `EPLUS_IDD` = `C:/EnergyPlusV24-2-0/Energy+.idd`. Note `py`, not
  `python` — on this Windows box `python`/`python3` are Microsoft Store stubs.

Waiting on a job costs nothing: a background `Bash` waiter
(`sleep 1800; ssh speed "sacct ..."`, `run_in_background: true`) uses **zero model tokens**, unlike a
monitoring subagent. Never poll tighter than 30 min.
