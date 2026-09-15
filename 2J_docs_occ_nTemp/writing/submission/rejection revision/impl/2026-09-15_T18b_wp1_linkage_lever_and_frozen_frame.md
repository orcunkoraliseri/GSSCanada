# T18b — WP1: one extra matching lever (drop CMA) and the frozen household frame — implementation state

Task doc:   this file. Parent: `2026-09-15_T18_wp1_rebuild_2022_build.md` (read Design, Ledger, Verified, Decisions in
full). Spec: `2026-09-15_WP1_step2_retargeting_spec.md` §5b rule 5. Plan log (u).
Status:     BLOCKED — job 1328333 array 0-1, both tasks FAILED exit 3, frame assert fired (Manager addendum 1
            trigger confirmed). Not a code bug. Choice rule not applied. Next = fresh employee runs Frame v2.

## Why (read from the T18 collector pass, T18 doc Verified)
- The 2022-only rebuild (Arm N) ran cleanly, but the strict match share fell from 44.94 % to 29.75 %, a drop of 15.19
  points. That is more than the 10-point limit, so spec §5b rule 5 fires: test one more lever and record both builds.
- Most of the lost strict matches landed in Tier 2 (`2_Core` 62,646 → 103,403). Tier 2 drops MARSTH, HHSIZE and
  CMA. Tier 3 barely moved (95,113 → 97,878), so people lost household size as a match key, not age or sex.
- Arm N's schedule file has 144,629 households against the published 144,465 (+164), and the Step-7 validator
  fails 6 checks on that one cause. It also fails check 3.5: stock at-home 75.00 % vs the Step-2 weighted GSS-2022
  anchor of 72.3 % (Δ2.70 pp, band ≤ 2 pp; `07_bemIntegrationGSS_val.py:76-80,350-357`). Arm C passes both.

## Design (manager, fixed before any T18b data is seen)
**Lever = drop CMA from the Tier-1 key set, globally.** Tier 1 becomes `AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR` +
`DDAY_STRATA`; Tiers 2–4 unchanged. CMA is the least informative key because it is nested inside PR, which stays.
Dropping it keeps household size and marital status in the strictest tier. No source edit. The wrapper replaces
`run_slot_match` on the imported module with a thin function that removes `"CMA"` from `match_keys` and calls
the original (`05_census_linkage.py:111-213`, tiers built locally at `:144-147`). `_POOL_EXCLUDE` (`:93`) is
computed at import and still excludes CMA from the pass-through columns. The employee confirms the call site passes
`MATCH_KEYS` as `match_keys` and records the line.

**Frozen household frame (applies to every 2022 build used downstream).** The paper's design is "freeze the
stock, evolve occupancy", and the Step-8/9 pairing needs the published households. So every downstream stock is
restricted to the published 144,465 `HH_ID`s. This happens **at the stock level**: filter
`21CEN22GSS_aug_Full_Aggregated_excl.csv` to the published HH set, then rerun `07_aug_to_bem.py --year 2022` and the
validator on it. That way T20's 2030 build reads the same frozen stock.
- Assert: every published HH_ID is present in the arm's excl stock. If any is missing, the job still writes the
  unfiltered outputs plus `missing_hh.csv`, exits non-zero, and the manager re-designs. Nothing is filled in.
- Record why the 164 differ. Read `run_exclusion()` (`05_census_linkage.py:639-697`) and name the rule that drops
  them in Arm C but not in Arm N. Report counts both directions (in N not published, in published not N).

**Builds (both recorded, spec rule 5):**
- **N-f** = existing Arm N excl stock → frame filter → `07_aug_to_bem.py --year 2022` → validator. No relink.
- **Nb-f** = full T18 chain on the 2022-only diaries with the CMA lever → frame filter → `07_aug_to_bem.py` →
  validator.
- Published HH list comes from `T18/reference/BEM_Schedules_2022.csv` (`SIM_HH_ID`, the collector job 1328328 reads
  it too; do not depend on that job).

**Choice rule (fixed now).**
- Primary 2022 stock = **Nb-f** if its Tier-1 share (6 keys) is within 10 points of Arm C's 44.94 %, i.e. ≥ 34.94 %.
- Otherwise primary = **N-f**. The tier drop becomes a stated limitation. No further lever is tried (the spec
  allows one).
- The build not chosen is kept as a sensitivity. Report its weekday household at-home difference from the primary.

**Reported, not banded:**
- Tier shares for N-f and Nb-f.
- The 7-key-equivalent share of Nb-f: Tier-1 agents whose donor CMA equals their census CMA, which is comparable with
  Arm C's 44.94 %.
- Donor reuse: max and 99th percentile.
- Household weekday and weekend at-home, national and per archetype.
- Validator pass/warn/fail counts. After the frame filter, the household-count checks must pass.
- Check 3.5 stays as it is: the band is never moved. For the paper, report the stock at-home split by donor type
  (real vs synthetic diary) and, if `augmented_diaries.csv` carries a survey weight column, the weighted real-2022
  at-home. This tells us whether the 2.7 pp gap to the weighted anchor comes from the synthetic diaries or from
  weighting. If no weight column exists, write NOT AVAILABLE.

## Acceptance (collector)
- B1 both jobs exit 0 and every chain step prints OK (read the logs, not only `sacct`).
- B2 frame: household set of each filtered `BEM_Schedules_2022.csv` equals the published set (count both
  directions = 0); rows 6,934,320; validator household-count checks PASS.
- B3 lever took effect: Nb-f `Matched_Keys.csv` Tier-1 count differs from Arm N's 85,256, and the wrapper log
  prints the 6-key list.
- B4 tier and at-home numbers above filled; choice rule applied and written under Decisions with the numbers.
- B5 no leakage: md5 of `T18/reference/*` and Arm C/Arm N outputs unchanged (Arm N excl stock is read, never
  written).

## Brief (employee, Sonnet)
Rules: identical to T18 (login node = `sbatch squeue sacct scancel scontrol cd ls scp module load`, single-file
`tail head grep wc -l cat` only; never python, `find`, `du`, `md5sum`, `cp` there. T18 recorded one `find` slip, so
do not repeat it. Every job `-p ps -t 7-00:00:00`; ssh `-o BatchMode=yes -o ConnectTimeout=60`; tcsh, no `2>&1`.
Python `/speed-scratch/o_iseri/envs/step4/bin/python`. Write only under `/speed-scratch/o_iseri/2J_revision/T18b/`;
read T18 files, never write them. No edits to repo files; local `py -3 -m py_compile` only.
**Submit and end your turn — never wait.**
1. Read the T18 doc, `T18_scripts/t18_pipeline.py`, `T18_scripts/collector/t18_collector_verify.py` (it fixes two
   bugs in `t18_metrics.py`; reuse it, do not reuse the broken lines), `05_census_linkage.py:111-213,639-697` and
   the `run_linkage_full` call site of `run_slot_match`. Record under Decisions: the exclusion rule, the call-site
   line, and all paths.
2. Write `impl/T18b_scripts/`: `t18b_pipeline.py` (imports `t18_pipeline.py`'s path patching; adds `--lever cma`
   and `--frame-filter <published_hh_list>`), `t18b_job.sh` (array 0-1: 0 = N-f, 1 = Nb-f; `-c 8 --mem=64G`),
   `t18b_metrics.py` (reported items + B2/B3/B5, written as CSV/JSON under `T18b/out/<build>/`). Compile locally.
3. Stage by `scp -r`, submit the array (no dependency; T18 outputs already exist). Ledger: JobID. Status SUBMITTED.
   End turn.

## Ledger
- **Local staging** (scratchpad `T18b_stage/T18b/`, built with local `cp`, not on the login node):
  `T18b_scripts/` (`t18b_pipeline.py` 16,732 B, `t18b_job.sh` 1,522 B, `t18b_metrics.py` 10,220 B);
  `nf/repo/scripts/` (`07_aug_to_bem.py` 13,246 B, `activity_loads.py` 11,530 B,
  `07_bemIntegrationGSS_val.py` 53,721 B); `nbf/repo/scripts/` (those 3 plus `05_census_linkage.py`
  44,158 B and `05_postlink_rake.py` 44,456 B). Sources: `2J_docs_occ_nTemp/*.py` for the 07-scripts,
  rake and activity_loads; `eSim/eSim_occ_utils/25CEN22GSS_classification/05_census_linkage.py` for
  linkage (same source T18 used).
- **Remote dirs created** (`ssh ... mkdir -p`, login node, allowed): `T18b/logs`, `T18b/out/nf`,
  `T18b/out/nbf`. **`scp -r`** of the local staging folder to
  `/speed-scratch/o_iseri/2J_revision/T18b/` — exit 0. Remote `ls -la` on all three script dirs
  confirmed every byte size matches the local staging folder exactly (see sizes above) — no
  truncation/corruption in transfer.
- **JobID 1328333** — `t18b` array (`--array=0-1`), submitted `sbatch -p ps -t 7-00:00:00
  T18b_scripts/t18b_job.sh` from `/speed-scratch/o_iseri/2J_revision/T18b/` (the script's own
  `#SBATCH` lines set `-c 8 --mem=64G`, matching T18's precedent). Task 0 = N-f, task 1 = Nb-f. No
  `--dependency` (T18 outputs already exist on disk, per design). State immediately after submission
  (`squeue -u o_iseri`): **`1328333_0` RUNNING on `speed-33`, `1328333_1` RUNNING on `speed-34`** — both
  started immediately, no queueing. Other jobs at submission time: `1328310_5`/`_4` (T22, RUNNING,
  small), `1328286_2` (T17 array, RUNNING, 8 CPUs), everything else PENDING on dependencies (T20/T26/T21
  chain, and `1328290` T17-compare) — none of ours touched, none cancelled. Output:
  `T18b/logs/slurm_t18b_1328333_0.out`, `slurm_t18b_1328333_1.out`; `T18b/out/{nf,nbf}/t18b_metrics_*.{json,csv}`.

- **Collector pass (2026-09-15).** `1328333_0` (build nf, on speed-33) FAILED exit 3, elapsed 2:02 (log runs
  to timestamp 121.5s). `1328333_1` (build nbf, on speed-34) FAILED exit 3, elapsed 17:48 (log runs to
  timestamp 1067.3s). Logs read in full: `T18b/logs/slurm_t18b_1328333_0.out` (1,196 B),
  `slurm_t18b_1328333_1.out` (8,703 B). No `.err` files exist for either task (`ls T18b/logs/` lists only
  the two `.out` files).

## Verified
- `py -3 -m py_compile t18b_pipeline.py t18b_metrics.py` — clean, locally, no big-file execution.
- `bash -n t18b_job.sh` — clean. (Written as `#!/bin/bash`, not tcsh — see Decisions: T18's own
  `t18_chain.sh` is `#!/bin/bash` too; tcsh is only the login-node ssh session shell, not the sbatch
  script's shebang. An earlier `bash -n` attempt on a tcsh-flavoured draft failed with a syntax error at
  EOF — that draft was discarded before staging, never scp'd, so no `find`/forbidden-tool slip and no
  stray file left on Speed.)
- Remote byte sizes for all 11 staged files match the local staging folder exactly (Ledger).
- `squeue -u o_iseri` immediately post-submit confirmed both `1328333` array tasks RUNNING, not queued;
  no dependency chain, no CPU-cap violation (total running CPUs well under the project's 32-CPU
  convention: 2 small T22 tasks + 8 CPUs T17 + 16 CPUs this array).
- Confirmed via `Read` of `2J_docs_occ_nTemp/07_aug_to_bem.py:94`
  (`df = df.rename(columns={"HH_ID":"SIM_HH_ID"}).copy()`) that `HH_ID` (the key column in
  `21CEN22GSS_aug_Full_Aggregated_excl.csv`) and `SIM_HH_ID` (the key column in the published
  `BEM_Schedules_2022.csv`) share one value space — the frame filter's join key is valid without any
  translation table.
- Confirmed via `Grep` on `05_census_linkage.py` that `run_slot_match` is called exactly once inside
  `run_linkage_full`, at line 381, as a bare global name — the precondition for the wrapper-replacement
  lever to work (Decisions).

- **Collector pass (2026-09-15) — cause of exit 3, both builds: the frame assert, exactly as the manager's
  pre-registered expectation (addendum 1) said. Not a code bug.** N-f exact quote
  (`slurm_t18b_1328333_0.out`): `[FRAME-FILTER FAIL] 849 published HH_IDs missing from this build's stock.
  Wrote unfiltered stock -> .../T18b/nf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl_UNFILTERED.csv
  and missing HH list -> .../missing_hh.csv. Nothing filled in. Exiting non-zero.` then
  `T18B_STEP_FAILED: t18b_pipeline.py (build=nf) exit=3`. Nb-f exact quote (`slurm_t18b_1328333_1.out`):
  `[FRAME-FILTER FAIL] 869 published HH_IDs missing from this build's stock. Wrote unfiltered stock ->
  .../T18b/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl_framefiltered_UNFILTERED.csv
  and missing HH list -> .../missing_hh.csv. Nothing filled in. Exiting non-zero.` then
  `T18B_STEP_FAILED: t18b_pipeline.py (build=nbf) exit=3`.
- `frame_filter_result.json` read for both: N-f (`T18b/nf/repo/outputs/aug_pipeline/frame_filter_result.json`)
  — published_n=144,465, arm_n=144,629, missing_n=849, extra_n=1,013, status FAIL_MISSING_HH. Nb-f
  (`T18b/nbf/repo/outputs/aug_pipeline/frame_filter_result.json`) — published_n=144,465, arm_n=144,627,
  missing_n=869, extra_n=1,031, status FAIL_MISSING_HH. `wc -l` on `missing_hh.csv` cross-checks both
  exactly: N-f 850 lines (849 + header), Nb-f 870 lines (869 + header).
- Nb-f reached the full relink chain before failing: `linkage.run_linkage_full` → `rake.main_joint` →
  `linkage.run_aggregate` → `linkage.run_bem` → `linkage.run_exclusion` all printed `STEP OK` (log), exclusion
  dropped 980 HHs (0.34% of 286,537) leaving 285,557 rows / 144,627 unique HH_ID in
  `21CEN22GSS_aug_Full_Aggregated_excl.csv` — only the frame_filter step on THAT file failed. N-f never
  relinked (design) and ran frame_filter directly on Arm N's own stock (285,553 rows, 144,629 unique HH_ID).
- CMA lever confirmed active in the log independent of the frame failure (B3): `[lever=cma] Tier-1 match_keys:
  ['AGEGRP', 'SEX', 'MARSTH', 'HHSIZE', 'LFTAG', 'PR', 'CMA'] -> ['AGEGRP', 'SEX', 'MARSTH', 'HHSIZE', 'LFTAG',
  'PR']`; Tier distribution 1_Perfect 120,270 (41.97%), well above Arm N's 85,256.
- `T18b/out/nbf/tier1_7key_equivalent.json` read (Nb-f only; job still failed before this would matter for
  nf, which has no such file — N-f does not relink): n_tier1=120,270, n_donor_cma_eq_census_cma=57,549,
  n_all_agents=286,537, pct_of_tier1=47.850%, **pct_of_all_agents=20.084%** — the file's own note names this
  last figure as the one comparable with Arm C's 44.94% Tier-1 share.
- No `validator_result.json` exists under either build's `aug_pipeline/` dir (`ls` of both dirs confirmed) —
  both jobs failed before the validator step ran; there is no validator result to report.

## Decisions
- **Exclusion rule (task doc step 1, required).** `run_exclusion()` (`05_census_linkage.py:639-698`,
  Sub-step 5H) drops every PP_ID whose PER-HOUSEHOLD mean AT_HOME across the 48 `HH_hom30_*` slots is
  `< 0.30` (`:650-658`, `hh_means = agg[hh_hom_cols].mean(axis=1); fail_ppids = ... hh_means < 0.30`),
  then applies that same PP_ID exclusion set identically to `Full_Schedules_excl`,
  `Full_Aggregated_excl` and `BEM_Schedules_excl` (`:660-680`). **This code and the 0.30 threshold are
  byte-for-byte identical between Arm C and Arm N — there is no second rule.** What differs is which
  diary each household's members get matched to upstream, in `run_slot_match` (donor pool is 2022-only
  in Arm N, and additionally drops CMA from Tier-1 in Nb-f); a different matched diary gives a different
  per-household 48-slot at-home mean, so a different set of households lands on each side of the fixed
  0.30 line. The "164 extra households" the T18 doc records for Arm N is this same mechanism, not a
  distinct defect. `t18b_pipeline.py`'s `frame_filter()` reports both directions per build
  (`missing_n` = published HH_IDs absent from the build's own stock; `extra_n` = the build's HH_IDs not
  in the published set) — written to `frame_filter_result.json` under each build's `aug_pipeline/`
  output dir, not yet read back in this turn (job still running).
- **Call-site line (task doc step 1, required):** `05_census_linkage.py:381` —
  `df_matched = run_slot_match(df_census_dday, df_pool, MATCH_KEYS, DDAY_COL, region_tier=region_tier)`,
  inside `run_linkage_full()` (`:364-410`). `MATCH_KEYS` (module constant, `:75`,
  `["AGEGRP","SEX","MARSTH","HHSIZE","LFTAG","PR","CMA"]`) is passed positionally as `match_keys`,
  confirming the design's own description exactly.
- **CMA lever implemented as a `run_slot_match` replacement on the loaded module, not as a
  `MATCH_KEYS` monkeypatch**, per the design's explicit wrapper text. Reason (read from the source,
  recorded because the design's rationale line ("`_POOL_EXCLUDE` is computed at import and still
  excludes CMA from the pass-through columns") only makes sense once this is spelled out): `t1_keys =
  match_keys + [dday_col]` (`:144`) is the ONLY place `match_keys` feeds Tier construction — Tiers 2-4
  are hardcoded to `AGEGRP,SEX,LFTAG,{REGION|PR},dday` / `AGEGRP,SEX,dday` / `dday` (`:145-147`),
  confirming "Tiers 2-4 unchanged" is automatic, not something the wrapper has to preserve by hand. But
  `MATCH_KEYS` (the same global) is ALSO read by `_POOL_EXCLUDE = set(MATCH_KEYS) | {...}` (`:93`,
  computed once at module import) and by `expand_slot_schedules()`'s `cen_demog = [k for k in
  MATCH_KEYS if k in df_census.columns]` (`:258`), both of which decide whether CMA keeps arriving as a
  CENSUS-side demographic passthrough column in the output. If the wrapper patched the module-level
  `MATCH_KEYS` global instead of intercepting `run_slot_match`, CMA would silently stop being excluded
  from the pool passthrough AND stop being pulled from Census, changing the output schema as a side
  effect of the matching lever — not what "Tiers 2-4 unchanged" means. `t18b_pipeline.py`'s
  `apply_cma_lever()` (script, this turn) therefore does `linkage_mod.run_slot_match = wrapper`, where
  `wrapper(df_census, df_pool, match_keys, ...)` computes `new_keys = [k for k in match_keys if k !=
  "CMA"]` and calls the ORIGINAL `run_slot_match` with `new_keys` — `MATCH_KEYS` itself is never
  touched. This works because `run_linkage_full` resolves the bare name `run_slot_match` against the
  module's globals dict at call time (confirmed via `Grep`, single call site), so reassigning the
  attribute on the loaded module object redirects that call without editing any function body — no
  source edit, matching the design and the "no pipeline source edits" rule.
- **7-key-equivalent capture point.** The design's "Tier-1 agents whose donor CMA equals their census
  CMA" number needs the donor's raw CMA, which only exists on `_pool_idx` before
  `run_linkage_full` drops that column at `:389-391` when writing `Matched_Keys.csv` — it is not
  recoverable from any written output file without re-matching. Computed it INSIDE the CMA-lever
  wrapper itself (the one point in the chain where `_pool_idx` is still on `df_matched` and the wrapper
  already has `df_pool`/`df_census` in scope), written to
  `T18b/out/nbf/tier1_7key_equivalent.json`; not yet read back in this turn (job still running).
- **Build N-f reuses Arm N's own `Matched_Keys.csv` from T18 (read-only) for its tier-share and
  donor-reuse numbers**, rather than re-deriving them from any T18b-written file — N-f does not relink
  (design, fixed), so its Tier-1/2/3/4 shares over the 286,537-agent Census frame ARE Arm N's already-
  measured shares (Tier-1 29.754 %, per the T18 doc). Frame filtering only removes ~164 households
  downstream in the BEM step; it cannot change a person-level match tier. `t18b_metrics.py`'s
  `matched_keys_path()` branches on `--build` for exactly this reason.
- **Staged fresh local copies of the 5 pipeline scripts for `nbf` and the 3 post-filter scripts for
  `nf`, rather than remote-copying T18's already-staged `arm_N/repo/scripts/`.** A remote-to-remote copy
  would need `cp` or a compute-node relay on the login node's forbidden list for a simple file copy;
  staging fresh from the same local repo originals T18 itself staged from is simpler and equally
  faithful (byte sizes cross-checked against the live repo, see Ledger), and keeps every T18b write
  strictly under `T18b/`, never touching `T18/arm_N/repo/scripts/`.
- **`t18b_job.sh` written as `#!/bin/bash`, not tcsh**, matching T18's own `t18_chain.sh` precedent
  (`T18_scripts/t18_chain.sh:1`) exactly. The task doc's "tcsh, no `2>&1`" line describes the
  login-node ssh session's shell for the commands this employee types over ssh, not the sbatch script's
  own shebang — sbatch runs a script under whatever interpreter its `#!` line names, independent of the
  submitting shell. Recording this explicitly since a first tcsh-flavoured draft of the script failed a
  local syntax check and was rewritten before ever being staged.
- **Validator counts captured in-process inside `t18b_pipeline.py`, not parsed from the HTML report or
  slurm log afterwards.** Read `07_bemIntegrationGSS_val.py:175` (`self.results: dict[str, list[str]] =
  {"pass": [], "fail": [], "warn": []}`) and confirmed `run_all()` only prints a summary line and writes
  an HTML report (`:955-985`) — it never dumps `self.results` to a machine-readable file on its own. So
  `run_a2b_and_validator()` (script, this turn) keeps the live `validator` object after `run_all()`
  returns and writes `validator.results` straight to `validator_result.json` under each build's
  `aug_pipeline/` dir itself, rather than re-deriving pass/warn/fail counts from text later
  (feedback_verify_progress_log_claims.md — read the artifact, don't re-parse a log for something the
  code already has in memory).
- **Region-tier kept at `True` for the Nb-f relink**, same as both T18 arms, per the parent T18 doc's
  own Decision (current on-disk build used `--region-tier`; default `False` reproduces pre-fix
  behaviour bit-for-bit) — the design does not mention changing it, and changing it alongside the CMA
  lever would confound which change moved the Tier-1 share.

## Manager addendum 1 (2026-09-15, written BEFORE any 1328333 output was read)
Trigger: the T18 collector pass 2 (T18 doc, addendum) read that Arm N's excl stock lacks **849 published
households** (1,013 extra; 143,616 common). The frame assert above will therefore fire on N-f and very likely on Nb-f.
That is the designed stop, not a bug. The re-design is fixed now so no result can steer it:
- **Frame v2.** The frozen frame is taken from the build's **pre-exclusion** aggregated stock
  (`21CEN22GSS_aug_Full_Aggregated.csv`, the input of `run_exclusion()`), filtered to the published 144,465 HH_IDs,
  then `07_aug_to_bem.py --year 2022` → validator. Reason: the published exclusion already fixed the stock; "freeze
  the stock" means the 0.30 at-home cut is not re-applied to a stock that is frozen by design. Re-applying it
  would change which dwellings exist between the published and revised 2022 runs and break the Step-8/9 pairing.
- **Reported (limitation, not banded):** number and share of published households whose new-diary household at-home
  mean is < 0.30 (they would have been excluded under a fresh build), per archetype; and check 3.5 on the full
  frame and on the frame minus those households.
- Assert v2: every published HH_ID is present in the pre-exclusion stock. If any is still missing, stop again and
  write `missing_hh.csv`; the linkage does not drop census households before exclusion, so this is not expected.
- Choice rule, B1–B5 and every band unchanged. B2 applies to the v2 frame.
- **Design W note.** `Equip_Design_W`/`Light_Design_W` are computed per household from its own diary activities
  (`07_aug_to_bem.py:77-87`, `activity_loads.calibrate_schedules`), so they are expected to change when the donor
  diaries change. That is not a stock change. T22 and the Step-9 activity arm read the revised file's own values.
  The historic 2005/2010/2015 files compute their own design W from their own diaries, so the T24 verdict stands.

## Next
Employee: steps 1-3. Collector (fresh, after the array leaves the queue): B1–B5, apply the choice rule. If the frame
assert fired, the collector records `missing_n`/`extra_n` per build and stops; a fresh employee then runs Frame v2
(addendum 1) for both builds, reusing the Nb-f relinked stock (no second relink).

**Collector pass (2026-09-15) result: the frame assert fired in BOTH builds (missing_n/extra_n recorded above
under Decisions and Ledger). Per this section's own rule, the collector stops here — B1–B5 and the choice rule
are NOT applied (the frame did not pass in either build, so the choice rule's precondition fails by design).
Next = fresh employee runs Frame v2 (Manager addendum 1) for both builds, reusing the Nb-f relinked stock
already on disk under `T18b/nbf/repo/outputs/aug_pipeline/` (no second relink needed).**
Manager: re-point T20 (2030 build), T26 (scenarios) and T21 (reruns) to the chosen frozen stock. The jobs now waiting
on the failed T18 array (T20 1328311, T26 1328326/1328327, and any T21 phase-A jobs depending on 1328311) can never
start. A fresh employee cancels them and resubmits them against the primary build's paths.
Manager note (T21 phase-A employee returned): the T21 phase-A jobs to cancel are **1328329** (baseline extract,
afterok:1328311) and **1328330** (smoke, afterok:1328329). `run_paired_mc.py` has no `--code-root` flag
(`Step8_docs/run_paired_mc.py:35-47`); the T21 scripts call the staged copy by its own path instead. The
resubmitting employee keeps that workaround.

## Manager addendum 2 (2026-09-15, after the collector pass; no rule changed)
- Frame v2 is launched for both builds by a fresh employee (task `impl/2026-09-15_T18c_wp1_frame_v2.md`).
- **The rule reads the 6-key Tier-1 share** (Design, choice rule). Nb-f 6-key Tier-1 = 120,270 / 286,537 = **41.97 %**
  ≥ 34.94 %, so the lever meets the bar as written. The choice is NOT final until Frame v2 passes B1–B5 for Nb-f; if
  Nb-f fails B2 after Frame v2 and N-f passes, N-f is primary.
- **Reported as a limitation, never used to re-decide:** the 7-key-equivalent share (donor CMA equals census CMA) is
  **20.08 %** of all agents in Nb-f, against Arm C 44.94 % and Arm N 29.75 %. Dropping CMA from Tier 1 raises the
  strict-tier share but lowers city agreement between person and donor. The paper states both numbers. The choice
  rule is not re-opened on this number: it was written before any output, and it named the 6-key share.

## WHAT I DID NOT VERIFY
- Did not run any chain step or read any job output — submitted and ended the turn per the no-parking
  rule. No evidence yet that `run_linkage_full` (with the CMA-lever wrapper active), `run_bem`,
  `run_exclusion`, `frame_filter()`, `07_aug_to_bem.py`'s `main()`, or the Step-7 validator actually
  succeed end to end on the Nb-f path, or that the N-f frame-filter+a2b+validator path succeeds reading
  Arm N's excl stock. Reasoned through the code (every function is either T18's own, unmodified, or a
  thin wrapper/filter written this turn) but this is reasoning, not a measurement.
- Did not verify the CMA-lever wrapper's redirection empirically (e.g. no smoke run confirming
  `linkage.run_slot_match = wrapper` actually intercepts the call inside `run_linkage_full` at runtime)
  — confirmed only by reading the bytecode-resolution argument (LOAD_GLOBAL at call time) and the single
  call site via `Grep`, not by executing it.
- Did not verify `frame_filter()`'s `missing`/`extra` split against real numbers — the "164" figure in
  the Why section is from the T18 doc (Arm N's household count vs published, pre-CMA-lever, pre-frame-
  filter); T18b's own `missing_n`/`extra_n` for N-f and Nb-f are unmeasured until the job's
  `frame_filter_result.json` files are read.
- Did not verify `t18b_metrics.py`'s `donor_type_split()` weighted-real-2022 branch against a known
  answer — logic (filter `IS_SYNTHETIC==0 & CYCLE_YEAR==2022`, weight by `WGHT_PER` if present and
  non-null) was reasoned through, not exercised on real data; whether `augmented_diaries.csv`'s
  downstream `Full_Aggregated_excl.csv` actually carries a usable `WGHT_PER` column for real-2022 rows
  is unconfirmed (T18's own doc used `WGHT_PER` in its N4.d method, so the column is expected to exist,
  but its non-null coverage on real-2022 rows specifically was not checked here).
- Did not check Speed disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T18b/` — Nb-f's
  own fresh chain writes several-hundred-MB-scale files similar to T18's arms, on top of whatever T18/
  T17/T20/T22/T26 already occupy.
- Did not confirm the array will run to completion inside its 7-day walltime, or that both tasks running
  concurrently (16 CPUs, ~600 MB-scale CSVs each) does not exceed node memory (`--mem=64G` per task,
  matching T18's sizing precedent, not independently re-derived for T18b's slightly larger frame-filter
  step).
- **Collector pass (2026-09-15) additions.** Did not read `missing_hh.csv` row contents (the actual HH_IDs)
  beyond `wc -l` counts — did not check overlap/difference between the nf and nbf missing-ID lists. Did not
  check disk usage/quota impact of the large `*_UNFILTERED.csv` files now on disk (nf: 608,922,179 B; nbf:
  608,996,441 B) — Frame v2 needs the pre-exclusion `Full_Aggregated.csv` (nbf has one, 611,086,069 B,
  already on disk from the relink that ran before the frame filter; nf has none, since N-f never relinked and
  only read Arm N's already-excluded stock). Did not independently recompute any of Nb-f's log-reported
  numbers (rake flip counts, coherence Δ, per-LFTAG paid-work gaps, the 7-key-equivalent JSON's own
  arithmetic) — read as printed/written, not re-derived. Did not apply the choice rule or B1–B5 (correct per
  this doc's own rule: the frame did not pass in either build). Did not start, stage, or submit any Frame v2
  work.
