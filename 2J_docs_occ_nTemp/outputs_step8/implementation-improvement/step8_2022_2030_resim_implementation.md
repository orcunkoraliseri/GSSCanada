# Step-8 targeted LOCAL re-simulation (2022 & 2030 only) — implementation doc

**Scope:** Task 1 of the handoff prompt at
`2J_docs_occ_nTemp/outputs_step7/prompt/step8_9_targeted_resim_LOCAL_prompt.md` (background reading,
not modified). Task 0 (act30 "un-calibrated" wording fix) is a separate, already-complete task —
noted here only as prior context. Tasks 2–4 are out of scope for this doc; see "Remaining tasks" below.

---

## Aim

Re-run the Step-8 EnergyPlus paired Monte-Carlo campaign (24 cells = 4 archetypes × 6 cities,
N=50 households/cell) for **2022 and 2030 only**, on the local Windows box, because the 2026-07-09
Steps 4–7 refresh (region-tier relink + `05_postlink_rake.py --joint` activity raking) materially
changed the 2022/2030 BEM schedules (1.2% household-ID churn vs. the old 144,507-HH frame; act30 now
joint-raked/calibrated where it used to be un-raked). This makes the existing Step-8 campaign (run
2026-06-08, cluster job 953111, 24/24 PASS) **stale for 2022 and 2030**. Historical years 2005/2010/2015
are untouched by the refresh and are kept as-is (targeted scope, user-approved) — they do not need
re-simulation.

## Why local, not cluster

The Speed HPC cluster is busy for ~2 weeks. Rather than wait, this re-sim runs directly on
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main` using the locally installed EnergyPlus
(`C:\EnergyPlusV24-2-0\energyplus.exe`, auto-detected by `eSim_bem_utils_2J/config.py:8-14`). Speed
login-node rules do not apply to local runs.

## Prior context — Task 0 (DONE, separate task)

The stale "act30 un-calibrated" wording was fixed in `2J_docs_occ_nTemp/07_bemIntegrationGSS.md`
(~L47, ~L226) and `2J_docs_occ_nTemp/07_bemIntegrationGSS_val.py` (§4.4 ~L438-442, deviations panel
~L792-797 and ~L823-831), reworded to "joint-raked (calibrated)". Predecessor archived to
`2J_docs_occ_nTemp/archive/07_bemIntegrationGSS_val.20260710_pre_actcalib.py` — **verified present**
(53,575 bytes, timestamped 2026-07-10 15:56). Both Step-7 reports were regenerated —
`outputs_step7/step7_validation_report_2022_v2.html` and `step7_validation_report_2030_v2.html` —
**verified present, both dated 2026-07-10 15:57**, results 2022 34/0/0 PASS and 2030 33/0/0 PASS
(0 FAIL both years). This task is complete; it is not the subject of this doc.

---

## Task 1 decision — paired-sampling gotcha (P1 chosen)

Restricting Step-8 to `--years 2022,2030` builds the household sampling pool from the 2022∩2030
intersection (144,465 HH) — a different pool than the original 5-year (144,507 HH) intersection —
so the same seed (42) draws a **different** random 50 households per cell than the existing
`sample_XXX_HHnnnn` dirs already on disk for 2005/2010/2015.

Two options were identified:
- **P1 (pragmatic):** fresh `--n 50 --seed 42 --years 2022,2030` sampling, treating 2022-vs-2030 as
  internally paired (this is the paper's forward-looking WFH/2030 delta). Historical years
  2005/2010/2015 become non-paired trend context. No code change required.
- **P2 (rigorous):** re-sim the same 50 HH per cell as the existing campaign, requiring a new
  fixed-HH-list mode in `run_paired_mc.py` plus handling for the ~0.6% of manifest HH now absent
  from the 144,465 frame.

**User chose P1.** This is the option in flight.

---

## Three bugs found (two before launch, one diagnosed from the first launch attempt)

### Bug 1 — manifest-clobbering risk (fix status: MITIGATION PENDING, see open action item)

`eSim_bem_utils_2J/main.py` — actual path
`2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/main.py`, function `run_step8_paired_mc()` — writes
`cell_manifest.csv` fresh on every invocation:

```python
# main.py:2073-2078
# Write manifest up front so provenance survives even if E+ crashes mid-run.
man_path = os.path.join(output_dir, "cell_manifest.csv")
with open(man_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["sample", "sim_hh_id", "hhsize", "dtype", "pr"])
    w.writeheader()
    w.writerows(manifest_rows)
```

Because the fresh 2022/2030-only sample draws different households than the original 5-year
campaign, it creates NEW `sample_XXX_HH<id>` folders alongside the OLD ones under the same cell
dir — but overwrites the SHARED `cell_manifest.csv`. `08_simulation_plots.py`'s `discover_runs()` /
`load_cell_manifest()` resolves each `sample_NNN_HH<id>` folder's true household ID by **manifest
index first, directory-name-embedded ID only as fallback**. Once the manifest reflects the NEW
(2022/2030) sample mapping, every OLD 2005/2010/2015 folder at the same sample-index number would
be mislabeled with whichever household the NEW run assigned to that index — silently wrong
`sim_hh_id` on retained historical-year aggregate rows.

**Fix (planned, not yet executed):** after the Step-8 2022/2030 campaign finishes successfully,
archive (rename, do not delete) the freshly-overwritten `cell_manifest.csv` for all 24 cells (e.g.
append a `.new_2022_2030` or dated suffix) **before** running Task-3 re-aggregation. With no
manifest present, `load_cell_manifest()` returns `{}` and `discover_runs()` falls back 100% to
parsing the household ID embedded in the directory name — correct for both old and new rows.
Confirmed cost: the `hhsize` column in the aggregate `annual` table goes blank for all rows (old
and new) since it only ever came from the manifest; grepped and confirmed this column is not read
by `08_simulation_val.py` or any `plot_figNN()` function — cosmetic/unused, not a validation gate.

**Verified as of this writing:** the manifest has **not yet been overwritten**. Checked two cells
directly —
`BEM_Setup/SimResults_Step8/campaign_N50/MidRise__Calgary_6B/cell_manifest.csv` (still dated
2026-06-05 09:08) and
`BEM_Setup/SimResults_Step8/campaign_N50/SingleD__Toronto_5A/cell_manifest.csv` (still dated
2026-06-03 05:48). This is consistent with the run being killed (see Status below) before it
reached the manifest-write step in `run_step8_paired_mc()` for any cell. **This means the bug has
not yet manifested, and the archival mitigation is still a required step before/after any
successful completion of this campaign — flagged as an open action item below, not yet done.**

### Bug 2 — resume-skip false-positive (fix status: DONE, code change applied)

`Step8_docs/run_campaign_local.py` originally had no `--years` flag. Its resume-skip check counts
existing `hourly_meters.csv` files per cell against an "expected" count (`args.n * len(COMPARATIVE_YEARS)`
= 250 for the old 5-year campaign). If a naive `--years` restriction were bolted on without
recomputing "expected", it would drop to 100 (50 HH × 2 years) — which the pre-existing 250 files
already exceed — so every cell would be misdetected as "already done" and a new run would silently
do nothing.

**Fix applied:** added a `--years` CLI passthrough (comma-separated, forwarded to
`run_paired_mc.py --years`); `nyr`/`expected` are now computed from `len(years)` when `--years` is
passed (confirmed in the current file at lines 165-170, 183-185, 226). Predecessor archived to
`2J_docs_occ_nTemp/archive/run_campaign_local.20260710_pre_years.py` — **verified present**
(11,785 bytes, timestamped 2026-07-10 16:04). **This run was launched with `--no-resume` explicitly**
regardless, to sidestep the false-skip risk entirely for this one-off targeted re-run (the `--years`
help text itself flags this: "pass --no-resume alongside this for a targeted subset re-run").

### Bug 3 — concurrent-cell schedule-loading memory blowup (fix status: DONE, relaunched)

The first launch attempt (see "Launch attempt 1" below) used the default `--workers 18` (cores-2 on
this box). Each of the 18 concurrently-running cells loads its own full schedule set (~3.7 GB) into
RAM independently, so 18 cells in flight at once means **18 × 3.7 GB** of schedule data resident
simultaneously — this blew past the 80% committed-memory watchdog ceiling in ~3 minutes, before any
individual EnergyPlus subprocess had even finished starting. This is a `--workers` (cells-in-parallel)
problem, not an `--ep-workers` (E+ processes-per-cell) problem, and the script's own design comment
near the watchdog/argparse section documents the intended flip for exactly this scenario: run **one
cell's schedules in RAM at a time** (`--workers 1`) and get the parallelism instead from **K
EnergyPlus processes running concurrently within that one cell** (`--ep-workers K`). System has
63.5 GB total RAM (~32 GB free alongside other running apps), so `--ep-workers 18` (18 concurrent E+
processes within a single cell) was chosen as the flip.

**Fix applied:** relaunched with `--workers 1 --ep-workers 18` instead of the default `--workers 18
--ep-workers 1`. No code change was needed — the flip is an existing, documented CLI option. See
"Launch attempt 2" below for the relaunch command and current state.

---

## Launch attempt 1 (aborted)

Run from `2J_docs_occ_nTemp/Step8_docs/`:

```
py run_campaign_local.py --n 50 --seed 42 --years 2022,2030 --no-resume
```

Console redirected to
`C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\BEM_Setup\SimResults_Step8\campaign_N50\_step8_2022_2030_resim_console.log`.
No explicit `--workers` / `--ep-workers` were passed, so both used their defaults, confirmed by the
console log header: `workers=18  ep-workers=1  mem-abort=80.0%  mode=standard` (18 = cores-2 on this
box; 80% is the committed-memory watchdog ceiling). Scope as planned: 24 cells × 50 HH × 2 years
= 2,400 EnergyPlus runs, writing into the same `BEM_Setup\SimResults_Step8\campaign_N50\<arch>__<city>\`
cell dirs as the existing untouched 2005/2010/2015 data (new `sample_XXX_HHnnnn` folders coexist
alongside the old ones, containing only `2022/` and `2030/` subfolders). A dry-run before launch had
confirmed 24/24 cells resolved, 2,400 total runs planned, 0 unresolved.

**Outcome — VERIFIED (2026-07-10, ~16:08): the campaign aborted.** Independent verification (log
contents, `campaign_status.csv`, live-process check) showed it stopped shortly after launch:

- `tasklist` showed **zero** `python.exe` or `energyplus.exe` processes running — nothing was
  executing at that point.
- The console log (last modified 2026-07-10 16:08) recorded:
  > `!!! WATCHDOG: committed memory 80.4% >= 80.0% -> KILLING all cells and aborting (peak 80.4%).`
  > `=== Campaign finished in 0.05 h ===`
  > `cells ok: 0/24  (newly run: 0, resume-skip: 0)`
  > `!!! ABORTED BY WATCHDOG -- committed-memory ceiling hit. No freeze; run was killed.`
  > `Lower --ep-workers and re-launch (resume skips completed cells).`
- All 24 cells showed `ABORTED` in `campaign_status.csv` (also written 2026-07-10 16:08): 1 cell
  (`SingleD__Toronto_5A`) at `exit=1, 2.9 min`, 16 more mid-flight cells at `exit=1, 2.9–3.0 min`,
  and 6 `HighRise__*` cells at `exit=-1, 0.0 min` (never got to start before the pool-wide kill —
  consistent with 18 workers running concurrently against 24 queued cells). The whole attempt ran
  for **0.05 h (~3 minutes)** before the memory watchdog tripped and killed every cell. **0 of 24
  cells completed.**
- Partial output existed on disk: 763 new `sample_XXX_HHnnnn` directories were created under
  `campaign_N50\<cell>\` before the kill (checked directly, e.g. 20 new dirs under
  `MidRise__Calgary_6B\`), but **zero** `hourly_meters.csv` files were produced by this run — i.e.
  no EnergyPlus output actually landed; only directory scaffolding existed.
- `cell_manifest.csv` in the two cells checked was **unchanged** from its pre-campaign timestamp (see
  Bug 1 above) — the manifest-clobbering risk had not materialized from this attempt.

**Root cause diagnosed (by the coordinator, confirmed against the script's own design comment):** see
Bug 3 above — 18 concurrent cells × ~3.7 GB of schedule data each blew past the 80% memory ceiling
before any E+ subprocess finished starting. This is a `--workers` problem, fixed by flipping to
`--workers 1 --ep-workers K`.

## Launch attempt 2 (relaunched — current live state)

Relaunched from the same directory with the `--workers`/`--ep-workers` flip applied:

```
py run_campaign_local.py --n 50 --seed 42 --years 2022,2030 --no-resume --workers 1 --ep-workers 18
```

Same console log path as attempt 1. Launched ~2026-07-10 16:09.

**Verified running stably as of ~2026-07-10 16:12 (this documentation pass):**
- `tasklist` shows 2 live `python.exe` processes (one orchestrator-sized, ~176 MB; one main process,
  ~1.46 GB) and 2 live `energyplus.exe` processes (~257 MB each) — the campaign is actively executing.
- Per-cell logs under `_logs/` show exactly **one** cell actively growing —
  `SingleD__Toronto_5A.log` at 99,515 bytes, last written 16:12:11 — while every other cell's log is
  frozen at its attempt-1 timestamp (16:07–16:08). This confirms **sequential, one-cell-at-a-time**
  processing, consistent with `--workers 1`.
- The coordinator additionally reports free memory holding steady around 31–32 GB (of 63.5 GB total)
  since relaunch, with no further watchdog trips.

**This documentation pass does NOT assert a completion state.** The campaign was still in progress
(on its first or an early cell) at the time of writing, with pass/fail counts and total runtime not
yet known. Do not treat any earlier "0/24" or "aborted" figures above as the current outcome — those
describe attempt 1 only. Task 3 (re-aggregation) still cannot start until this attempt finishes AND
the Bug-1 manifest-archival mitigation is carried out.

---

## Remaining tasks (status as of 2026-07-10 ~23:25 — see Progress Log update 4 for detail; Task 1
now 12/24 cells done — all SingleD + OtherDwelling, 0 failures — MidRise in progress, HighRise not
started)

- **Task 2 — Step-9 local re-sim. Status: driver BUILT + smoke-tested; full campaign NOT YET
  LAUNCHED.** The thin local wrapper now exists —
  `2J_docs_occ_nTemp/Step9_docs/run_step9_local.py` (330 lines) — reusing the `eSim_bem_utils_2J`
  engine and mirroring Step-8's `run_campaign_local.py` memory-watchdog pattern (own code comment at
  L66: "identical pattern to Step 8's run_campaign_local.py"; same `--workers`/`--ep-workers`/
  `--mem-abort` flags, `build_manifest()` at L148). A 1-cell/n=1/both-treatments smoke test PASSED
  (see Progress Log below). Full re-sim scope remains 4,800 runs (24 cells × 50 × 2 yr × 2 arms —
  baseline vs. activity-driven), pointed at the 17-col activity schedules
  (`BEM_Schedules_{2022,2030}.csv`) and the 13-col baseline schedules
  (`BEM_Schedules_{2022,2030}_baseline.csv`). **Launch is deliberately held** until the Step-8
  campaign finishes — see Progress Log. Step-8 ETA has widened (see update 4) so this hold likely
  extends well past the original ~4-5h estimate.
- **Task 3 — re-aggregate + re-validate. Status: NOT STARTED.** `Step8_docs/08_simulation_plots.py
  --rebuild-agg --figs all` then `08_simulation_val.py` for Step-8; the Step-9 equivalents
  (`step9_validate_full.py`, `step9_loadshape_aggregate.py`, `09_activityDrivenLoads_val.py`) for
  Step-9. **Must happen only after** the Bug-1 manifest archival step above, and only after Step-8
  actually completes (12/24 cells done as of update 4 — see Progress Log for detail).
- **Task 4 — propagate the 144,507 → 144,465 household-frame fix. Status: NOT STARTED.** Across
  remaining downstream docs: `08_simulation.md`, `09_activityDrivenLoads.md`, the `00_*` overview
  docs, a stale code comment in `eSim_bem_utils_2J/main.py` (~L66-72, "share the SAME 144,507
  SIM_HH_IDs"), and the manuscript's explicit "144,507 households" line
  (`writing/2nd_Occ_Journal_Skeleton.md:358`). Deferred until after the re-simmed numbers land, so
  the paper's frame matches its results.

---

## Progress Log

**2026-07-10** — Documented the Step-8 2022/2030 targeted local re-sim (Task 1 of the LOCAL
resim handoff prompt). Recorded the P1 paired-sampling decision (fresh 2022/2030 sample, treated as
internally paired; historical years become non-paired context), the manifest-clobbering bug found
in `run_step8_paired_mc()` (mitigation: archive `cell_manifest.csv` per cell before Task-3
aggregation — not yet done, no manifests overwritten yet) and the resume-skip false-positive bug in
`run_campaign_local.py` (fixed: `--years` passthrough added, predecessor archived). Verified firsthand
that both archived predecessors (`07_bemIntegrationGSS_val.20260710_pre_actcalib.py`,
`run_campaign_local.20260710_pre_years.py`) and both Step-7 v2 reports exist with today's date.
Independently checked live status rather than trusting the handoff's "still running" assumption:
found the campaign had already been **killed by its own memory watchdog** after ~3 minutes
(committed memory hit 80.4%, ceiling 80%), with **0 of 24 cells completed** and no
`python.exe`/`energyplus.exe` processes currently alive. 763 partial sample directories exist on
disk with zero `hourly_meters.csv` outputs; `cell_manifest.csv` files are unchanged in the two cells
sampled. Flagged the re-launch (with reduced `--workers` to stay under the memory ceiling) as the
immediate next action, and Tasks 2–4 as outlined but not started.

**2026-07-10 (update)** — Coordinator diagnosed the watchdog abort's root cause: the default
`--workers 18` ran 18 cells concurrently, each loading its own ~3.7 GB schedule set into RAM at once,
blowing past the 80% committed-memory ceiling in ~3 minutes before any EnergyPlus subprocess finished
starting — a `--workers` (cells-in-parallel) problem, not an `--ep-workers` problem. Relaunched with
the flip documented in the script's own design comment: `--workers 1 --ep-workers 18` (one cell's
schedules in RAM at a time, 18 concurrent E+ processes within that cell; box has 63.5 GB total RAM,
~32 GB free). Documented this as Bug 3. Independently re-verified (not just transcribed) the relaunch
state before updating this doc: confirmed 2 live `python.exe` + 2 live `energyplus.exe` processes,
confirmed only `SingleD__Toronto_5A.log` actively growing (99,515 bytes @ 16:12:11) while all other
cell logs sit frozen at their attempt-1 timestamps — consistent with sequential one-cell-at-a-time
processing under `--workers 1`. Restructured the doc into "Launch attempt 1 (aborted)" / "Launch
attempt 2 (current)" sections; explicitly did not assert any completion or final pass/fail counts for
attempt 2, since it was still in progress at the time of writing.

**2026-07-10 (update 2, ~16:30) — Task 1 campaign confirmed healthy and progressing; first cell
complete.** Independently re-verified attempt 2's live state rather than trusting the prior "still in
progress" note at face value: read the tail of
`BEM_Setup/SimResults_Step8/campaign_N50/_logs/SingleD__Toronto_5A.log` directly and confirmed it
recorded `Total time: 719.6 seconds (12.0 minutes)`, `Successful: 100/100`, `Failed: 0/100`, and
`DONE cell=SingleD__Toronto_5A: status=ok | E+ 100/100 ok | 100/100 hourly parsed` — cell 1 of 24
(100 runs = 50 HH × 2 yr) completed cleanly, file last modified 2026-07-10 16:23:33. Confirmed the
campaign is actively moving to the next cell, not stalled: `SingleD__Kelowna_5B.log` exists and was
last modified 16:26:08 (24 s before this check at 16:26:32), with its tail showing only
`Running 100 EnergyPlus jobs (50 HH x 2 yr)... Starting 100 simulations with 18 parallel workers ...
[SIM] Running... [0/100 complete] Elapsed: 01:00` — i.e. cell 2 has just started, consistent with
`--workers 1` sequential processing and roughly a ~12 min/cell pace (→ rough ETA ~4-5 h for the
remaining cells if that pace holds across archetypes). **Caveat verified and flagged explicitly:**
`campaign_N50/campaign_status.csv` is still the STALE file from launch attempt 1 — last modified
2026-07-10 16:08:03, all 24 cells still listed `ABORTED` (most at `exit=1, 2.9-3.0 min`, the 6
`HighRise__*` cells at `exit=-1, 0.0 min`). This file is only written once at full-campaign
completion/exit, so it will keep showing attempt-1's all-ABORTED snapshot for the entire duration of
attempt 2's run — **do not read `campaign_status.csv` as current status while attempt 2 is still
executing; trust the per-cell `_logs/*.log` tails instead.** Task 1 status: IN PROGRESS, healthy,
1/24 cells done, 0 failures so far.

**2026-07-10 (update 3, ~16:30) — Task 2 (Step-9 local driver) built and smoke-tested; Task 2 full
launch deliberately deferred.** Built
`2J_docs_occ_nTemp/Step9_docs/run_step9_local.py` (330 lines — verified by direct line count; this is
somewhat longer than the ~280-line estimate carried into this session, no functional discrepancy
found), mirroring Step-8's `run_campaign_local.py` memory-watchdog design (own in-file comment at L66:
"Memory watchdog: identical pattern to Step 8's run_campaign_local.py"; same `--workers`/
`--ep-workers`/`--mem-abort` CLI surface, `build_manifest()` at L148). Ran a smoke test: 1 cell
(`SingleD__Toronto_5A`), `--n 1`, both treatments (baseline + activity), `--workers 1 --ep-workers 2
--no-resume`. **Verified directly, not taken on faith:**
- `BEM_Setup/SimResults_Step9/campaign_N50_2022_2030/step9_manifest.csv` (written 16:20:53) contains
  exactly 4 rows — `(baseline,2022)`, `(baseline,2030)`, `(activity,2022)`, `(activity,2030)` — **all
  four with `hh_id=33188`**. This empirically confirms the paired-sampling design (shared seed +
  shared household pool, no extra bookkeeping) actually pairs the two treatment arms onto the same
  household in practice, not just in theory.
- All 4 expected `hourly_meters.csv` outputs exist on disk under
  `BEM_Setup/SimResults_Step9/campaign_N50_2022_2030/idfs/SingleD__Toronto_5A/{baseline,activity}/
  sample_001_HH33188/{2022,2030}/hourly_meters.csv` (sizes ~1.18-1.39 MB each, all written
  16:20:52-16:20:53) — smoke test PASSED end-to-end, EnergyPlus output actually landed (not just
  manifest scaffolding).
Manifest schema (`idx,cell,treatment,hh_id,year,idf_path,epw_path`) matches expectations, IDF/EPW
paths resolve correctly (e.g. `CAN_ON_Toronto.City-Univ.of.Toronto.715080_TMYx_5A.epw`).

**Decision (open, not a finalized instruction from the project owner):** the full Step-9 campaign
(24 cells × 2 treatments × 50 HH × 2 yr = 4,800 EnergyPlus runs) has **not** been launched. The
executor is deliberately holding it until the Step-8 campaign (2,400 runs, currently 1/24 cells done,
rough ETA ~4-5 h at the observed ~12 min/cell pace) finishes, to avoid two large unattended
EnergyPlus campaigns competing for memory/CPU simultaneously on a box that cannot be remotely
rebooted if it locks up. This is a judgment call by the executor, flagged here for the project owner
to override if a different sequencing is preferred.

Tasks 3 (re-aggregate + re-validate Step-8 and Step-9) and Task 4 (propagate the 144,507→144,465
frame-size fix across remaining downstream docs/manuscript) remain **NOT STARTED** — unchanged from
the outline above.

**2026-07-10 (update 4, ~23:25) — Task 1 campaign: SingleD + OtherDwelling archetypes complete
(12/24 cells), 0 failures across 1,200 E+ runs; MidRise in progress; timing estimate revised
upward.** Independently re-verified the live state from scratch (did not take the ~12 min/cell
extrapolation in update 2 on faith) by listing `_logs/*.log` sorted by `LastWriteTime` and tailing
each cell's "SIMULATION SUMMARY" block directly:

- **All 6 SingleD cells done, 0 failures:** Toronto (16:23:33), Kelowna (16:37:26), Vancouver
  (16:51:06), Montreal (17:04:45), Calgary (17:18:49), Winnipeg (17:32:45) — each log confirms
  `Successful: 100/100`, `Failed: 0/100`. E+-phase "Total time" values: 719.6s, 717.6s, 715.2s,
  706.5s, 725.8s, 701.7s → **mean 714.4s = 11.9 min/cell**, matching the ~12.0 min figure. Gaps
  between consecutive cells' `LastWriteTime` (wall time, includes schedule-load/startup overhead):
  13m53s–14m04s → **mean ~13.8 min/cell**, matching the ~13.8 min figure.
- **All 6 OtherDwelling cells done, 0 failures:** Toronto (18:30:09), Kelowna (19:26:53), Vancouver
  (20:23:50), Montreal (21:20:57), Calgary (22:17:27), Winnipeg (23:14:24) — each log confirms
  `Successful: 100/100`, `Failed: 0/100`. E+-phase "Total time" values: 3214.4s, 3174.8s, 3181.7s,
  3202.0s, 3163.5s, 3194.4s → **mean 3188.5s = 53.1 min/cell**, matching the ~53 min figure (~4.4×
  SingleD's E+ phase). Gaps between consecutive cells: 56m30s–57m24s → **mean ~56.8 min/cell wall**,
  matching the ~57 min figure. **Combined SingleD+OtherDwelling total: 1,200/1,200 E+ runs
  successful, 0 failed.**
- **MidRise in progress, no completion data yet.** `MidRise__Toronto_5A.log` started ~23:14:24
  (immediately after OtherDwelling Winnipeg finished) and is actively growing (`LastWriteTime`
  23:21:31, checked again at 23:22:06 — still mid-run, tail showing `[SIM] Running... [0/100
  complete] Elapsed: 04:30`, i.e. no individual E+ run has finished within this cell yet). The log's
  zone-discovery `FLAG` line confirms the building geometry directly: **27 People zones** (not the
  ~26 estimated pre-check) — G floor (1 corridor + 7 apartments = 8 zones), M floor (1 corridor + 8
  apartments = 9 zones), 1 Office zone, T floor (1 corridor + 8 apartments = 9 zones) — a genuine
  multi-floor apartment building, materially more zones than SingleD or (apparently) OtherDwelling.
  Given OtherDwelling's ~4.4× slowdown over SingleD tracked with its own higher zone count, MidRise's
  per-cell time may match or exceed OtherDwelling's ~57 min — not yet confirmed since no MidRise cell
  has completed. MidRise's other 5 cell logs (Kelowna/Winnipeg/Montreal/Calgary/Vancouver) are still
  frozen at 16:07:52–16:08:01, leftover from launch-attempt-1's abort — attempt 2 has not reached them
  yet, confirming strict sequential order under `--workers 1`.
- **HighRise (6 cells) not started.** All 6 `HighRise__*.log` files are unchanged since 2026-06-02
  14:41–14:45 (`campaign_console.log` likewise stale at 2026-06-02 15:07) — confirmed these predate
  this re-sim entirely (leftover from the old prior campaign) and attempt 2 has not touched them.
- **Memory healthy:** `Get-CimInstance Win32_OperatingSystem` at 2026-07-10 23:22:06 reports
  **26.54 GB free of 63.46 GB total** — no signs of the committed-memory pressure that tripped the
  80% watchdog and killed launch attempt 1.
- **Revised completion estimate — widened, not just extended.** 12/24 cells done, 12 remain (6
  MidRise + 6 HighRise). At OtherDwelling's observed ~57 min/cell pace, the remaining 12 cells would
  take **~11.4 h**; but MidRise's larger zone count (27, vs. an unconfirmed but apparently smaller
  OtherDwelling count) and HighRise's completely uncharacterized geometry/timing mean the true pace
  could run longer per cell than OtherDwelling's, not shorter. Presenting this honestly as a wide
  range — **roughly 11–20+ h remaining, genuinely uncertain until at least one MidRise cell and one
  HighRise cell complete** — rather than false precision. **This explicitly revises update 2's
  ~4–5 h ETA upward**: that earlier figure was extrapolated from SingleD's ~12 min/cell pace alone,
  before any OtherDwelling data existed to reveal the ~4× archetype-to-archetype slowdown now
  confirmed twice (SingleD→OtherDwelling, and suspected again OtherDwelling→MidRise/HighRise).
  Task 1 status: IN PROGRESS, healthy, 12/24 cells done, 0 failures so far.
