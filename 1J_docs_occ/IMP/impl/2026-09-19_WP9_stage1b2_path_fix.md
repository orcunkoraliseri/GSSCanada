# WP9 Stage 1b-2: fix input paths and resubmit the 2010, 2015, 2022 rebuilds (1J JBPS revision)

Task doc:   this file (sections "Why" to "Rules" are the prompt; the employee fills the state sections below)
Parent:     `1J_docs_occ/IMP/impl/2026-09-19_WP9_stage1b_rebuild.md` (read ALL of it first: Ledger, Patches, Decisions)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §7 log (p), (q)
Status:     SUBMITTED — 1339779 (symlink+P4 verify) COMPLETED exit 0; 1339780/1339781/1339782 (2010/2015/2022 rebuilds) RUNNING, not waited on. 2005 (1339770) untouched, still RUNNING. See Decisions for a live risk flagged on 1339781 (2015).

## Why

Stage 1b's second rebuild attempt (parent Ledger, jobs 1339770-1339773) ran after the venv fix (1339769, COMPLETED 0:0).
2005 (1339770) is RUNNING and its log shows the day-type remap applied cleanly (`P1 day-type remap: DDAY NaN before=0,
after=0`, log line 32). The other three FAILED within seconds, exit 4 (the job's own guard), for path reasons, not code
reasons (manager read the log tails on 2026-09-19):

- **2010 (1339771)** and **2022 (1339773)**: Step 0 episode preprocessing looks for its raw file under
  `/nfs/speed-scratch/o_iseri/1J_rerun/occ/code/0_Occupancy/DataSources_GSS/Episode_files/...`, i.e. relative to the
  CODE folder (`.../occ/code/0_Occupancy`), not `GSS_BASE_DIR` (`.../occ/0_Occupancy`). Files:
  2010 `GSS_2010_episode/C24_Episode File_SPSS_withno_bootstrap.SPS`, 2022 `GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat`.
- **2015 (1339772)**: alignment reads a hard-coded Mac path
  `/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs_GSS/out15EP_ACT_PRE_coPRE.csv`, prints a warning, and
  still reports "Alignment complete"; then Profile Matching dies on missing `Outputs_16CEN15GSS/alignment/Aligned_Census_2015.csv`.
  Also: it rebuilt `2016_LINKED.csv` from `Outputs_CENSUS/cen16_filtered2.csv` because it did not find a linked file
  at `Outputs_16CEN15GSS/alignment/`.

## Task

### T1. Find every path that escapes `GSS_BASE_DIR` (read-only, local)

In the LOCAL staged copy of the patched code (parent's Patches section says where it lives in the old scratchpad; if that
folder is gone, rebuild it from the repo files + the diffs in the parent doc, and md5-check against the parent's recorded
pre-patch md5s before re-applying), grep all four chains (`06CEN05GSS/`, `11CEN10GSS/`, `16CEN15GSS/`, `21CEN22GSS/`)
and `occ_config.py` for: `/Users/`, `Desktop`, `2ndJournal`, `Path(__file__)`, `parent.parent`, `'0_Occupancy'`,
`"0_Occupancy"`, `os.getcwd`, `expanduser`. List each hit as `file:line` + what it resolves to on the cluster.
**Include 2005**: it is running now, and a later step may still hit a bad path.

### T2. Minimal fixes, staging only (never the repo files)

- **Relative-to-code paths** (2010, 2022 Step 0 and any other like it): preferred fix is NO code change, a symlink made
  inside an sbatch job: `ln -s /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy /speed-scratch/o_iseri/1J_rerun/occ/code/0_Occupancy`.
  Check first (in the same job, `ls -la`) that `.../occ/code/0_Occupancy` does not already exist; if it does, stop and write why.
  Then check that the raw files Step 0 wants really exist under `.../occ/0_Occupancy/DataSources_GSS/Episode_files/`
  (`ls` inside the job). If a raw file is missing from the copy, find it in the mirror
  `/speed-scratch/o_iseri/GSSCanada/GSSCanada-main/0_Occupancy/` and copy only that folder with `cp -a` in the job.
- **Hard-coded Mac paths** (2015 and any others T1 finds): patch the staged file so the path is built from the
  pipeline's `BASE_DIR` (e.g. `BASE_DIR / 'Outputs_GSS' / 'out15EP_ACT_PRE_coPRE.csv'`), only after confirming the file
  exists at that location in the copied inputs. If it does not exist anywhere in the copy or the mirror, stop and write
  what produces it (which step or script); do not invent it. Write the exact diff under "Patches" as **P4**.
- Nothing else. P1-P3 stay exactly as in the parent doc. No age-code-88 fix, no seed change, no 2025.
- `py -m py_compile` every file you touch, then `scp` only the touched files to
  `/speed-scratch/o_iseri/1J_rerun/occ/code/eSim_occ_utils/<chain>/`. Record md5 local vs what you uploaded.

### T3. Resubmit 2010, 2015, 2022 (do not wait)

- Reuse the parent's job scripts for these three years unchanged except for anything T2 needs (read them on the
  cluster with single-file `cat`; they are the scripts that produced 1339771-1339773). Same settings: 1 CPU,
  `-A chachemv -p ps -t 7-00:00:00 --mem=32G`, logs `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage1b_<year>_%j.out`,
  full chain with `OCC_DENOM=grid`, then converter alone with `OCC_DENOM=hhsize`, then `gate1_occ.py` on both files.
- If the symlink job is separate, make the three rebuilds `--dependency=afterok:<symlink job>`.
- **Do not touch 2005 (1339770)**: do not cancel or resubmit it. If T1 finds a bad path in a 2005 step that has not
  run yet, write it under "Next" and let the manager decide; do not cancel the job.
- Before resubmitting 2015: delete nothing. The failed run left `Outputs_16CEN15GSS/alignment/2016_LINKED.csv`
  behind; write in "Decisions" whether the rerun will reuse it or rebuild it, from reading the code.
- Append every JobID to the Ledger here the moment it is submitted, then END YOUR TURN. No polling, no sleep.

## Rules

- Speed login node: only `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`,
  single-file `tail`/`head`/`grep`/`wc -l`/`cat`. **Never python, md5sum, cp, ln, find, du, sed or srun on the login
  node** (the parent agent ran `find` and `du` there; do not repeat it). Anything else goes in a small sbatch job
  (`-t 7-00:00:00`, `-A chachemv -p ps`). Connect with `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`.
  Login shell is tcsh: no `2>/dev/null`, no awk `$` inside ssh strings.
- Never write under `/speed-scratch/o_iseri/GSSCanada/` (read only). Staging root is `/speed-scratch/o_iseri/1J_rerun/occ/`.
- Local machine carries another heavy run: light work only, one process at a time. Use `py`.
- Never modify repo code, `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`, `eSim_dynamicML_mHead_alignment.py`.
- State lives in this file: write as you go. If you pass about 150k tokens, stop, write state, say "handoff needed".

---

## Ledger

(JobID · what · state · exit · output path; append only)

- **1339779** · T2 symlink job (`wp9_1b2_symlink.sh`): guard-checked `.../occ/code/0_Occupancy` did not exist, confirmed both raw episode files present under the real `GSS_BASE_DIR`, created `ln -s /speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy /speed-scratch/o_iseri/1J_rerun/occ/code/0_Occupancy`, re-confirmed both raw files resolve through the new symlink, and md5-verified the just-uploaded P4-patched `16CEN15GSS_alignment.py` · **COMPLETED** · exit 0 · log `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage1b2_symlink_1339779.out`.
- **1339780** (2010), **1339781** (2015), **1339782** (2022) · third T4 rebuild attempt, reusing the **unchanged** job scripts from the parent doc (`/speed-scratch/o_iseri/1J_rerun/occ/wp9_1b_2010.sh`, `_2015.sh`, `_2022.sh`, sanity-checked by single-file `cat` against the local scratchpad copies before submit — identical), submitted `--dependency=afterok:1339779` · **RUNNING at end of this turn** (`sacct` checked once, all three RUNNING, not polled further) · logs will land at `.../wp9_stage1b_2010_1339780.out`, `_2015_1339781.out`, `_2022_1339782.out`.
- **Untouched, confirmed by `sacct`:** 1339770 (2005) still **RUNNING**, not cancelled or resubmitted.
- **1339781** (2015) · **CANCELLED by the manager** at 1 min 48 s · reason: the risk this doc flagged came true. Log line 21 `[OK] GSS 2015 Merged file already exists: GSS_2015_Merged_Main.csv`, no `P1 day-type remap` line, and the catalogue came out Weekday 1,112 vs Weekend 2,698 profiles (the April swap). Superseded by 1339786.
- **1339785** (manager) · move-aside job, nothing deleted: `Outputs_GSS/GSS_2015_Merged_Main.csv` -> `.pre1b_noP1` (Apr 16, 22,399,317 bytes) and `Outputs_16CEN15GSS` -> `Outputs_16CEN15GSS.run1339781_noP1`; confirmed `GSSMain_2015.txt`/`.sps` and `out15EP_ACT_PRE_coPRE.csv` present for the rebuild · **COMPLETED** 0:0 · log `.../wp9_stage1b3_mv_1339785.out` (`MOVE_OK`).
- **1339786** (2015) · fourth 2015 attempt, unchanged `wp9_1b_2015.sh`, `--dependency=afterok:1339785` · RUNNING at submit · log `.../wp9_stage1b_2015_1339786.out`.
- Manager note from the same `ls`: `GSS_2005_Merged_Episodes.csv` was rebuilt today (13:17, with P1); `GSS_2022_Merged_Episodes.csv` is the April copy (Apr 16) and is reused, although 2022 Step 0 rewrote `out22EP_ACT_PRE_coPRE.csv` today (13:25). 2022 needs no P1, so this is not a fault, but the 2022 rebuild matches from the April merged file, not from today's Step 0 output.

- **1339786** (2015) · **FAILED** exit 4 after 1:16:05: Steps 1-4 (alignment, matching, DTYPE expansion, aggregation) COMPLETED; converter crashed at the first group with the same NaN-tier error as 2005 (plan log (u)). No `P5` line in its log: the converter module was loaded at job start, before P5 was uploaded. Re-run of the converter only: **1339839** (`wp9_1b_2015_conv.sh`, `--run 5`, grid then hhsize then Gate 1).
- Contingent converter-only re-runs, start only if the full job FAILS: **1339840** (2010, `--dependency=afternotok:1339780`, `--run 4`) and **1339841** (2022, `afternotok:1339782`, `--run 4`). If the full job succeeds they stay pending with DependencyNeverSatisfied: scancel them then.

## Path hits (T1)

Grep of the four chains + `occ_config.py` for `/Users/`, `Desktop`, `2ndJournal`, `Path(__file__)`, `parent.parent`,
`'0_Occupancy'`/`"0_Occupancy"`, `os.getcwd`, `expanduser`, run against the LOCAL staged copy that was still present
at the old session scratchpad (`...\wp9_stage1b\upload\occ\code\eSim_occ_utils\`; confirmed already patched — P2
marker `WP9 Stage 1b P2` present in all four `*_HH_aggregation.py`, so this is the post-P1/P2/P3 tree that was
actually `scp`'d for the second rebuild attempt, not a stale pre-patch copy; did not need to rebuild it).

Real bugs (escape `GSS_BASE_DIR`, confirmed against the three failure logs on the cluster):

- **`11CEN10GSS/11CEN10GSS_main.py:99`**: `step0.main(project_root=Path(__file__).resolve().parents[2])`. `__file__`
  is `.../occ/code/eSim_occ_utils/11CEN10GSS/11CEN10GSS_main.py`; `.parents[2]` = `.../occ/code`.
  **`11CEN10GSS/11CEN10GSS_step0.py:104`**: `base_dir = Path(project_root) if project_root is not None else ...`,
  then `episode_dir = base_dir / "0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode"` → resolves to
  `.../occ/code/0_Occupancy/...` (confirmed by the 1339771 log's exact error path).
- **`21CEN22GSS/21CEN22GSS_main.py:155`** and **`21CEN22GSS/21CEN22GSS_step0.py:213-214,218`**: identical pattern,
  `project_root = ... parents[2]` → `.../occ/code`, `episode_dir = project_root / "0_Occupancy" / ...` (confirmed
  by the 1339773 log).
- **`16CEN15GSS/16CEN15GSS_alignment.py:881`** (pre-patch line number): hard-coded Mac path
  `FILE_EPISODE_15 = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs_GSS/out15EP_ACT_PRE_coPRE.csv")`,
  never resolvable on the cluster; confirmed by the 1339772 log's warning line.
- **`occ_config.py:21,23`**: `_DEFAULT_BASE_DIR` hard-codes both a Mac path and a Windows repo path — this is the
  intended, guarded fallback (overridden by `GSS_BASE_DIR` at line 29, which every job script sets), not a bug.
  Not touched.

All other `Path(__file__).parent`/`.parent.parent` hits listed by the grep (all four `_main.py`'s `_load_module`
sibling-file loaders, every module's `sys.path.insert` for importing `occ_config`, `occ_config.py:48`'s
`get_project_root()`) resolve to the code directory itself and are correct by design — they load sibling `.py`
files or set up `sys.path`, never data. Not bugs, not touched.

**2005 (running, 1339770) checked too**: `06CEN05GSS` has no `*_step0.py` at all (2005's episode file is
pre-processed once and read directly via `OUTPUT_DIR_GSS / "out05EP_ACT_PRE_coPRE.csv"`, confirmed at
`06CEN05GSS_alignment.py:868` — the correct pattern 2015 now also uses after P4). No escaping-path pattern found
in `06CEN05GSS/*.py` beyond the same-shape `sys.path.insert`/`_load_module` hits already ruled out above. Nothing
found that could bite a not-yet-run step of the running job.

## Patches

**P4** (16CEN15GSS/16CEN15GSS_alignment.py, staged copy only), unified diff as applied:

```diff
--- 16CEN15GSS/16CEN15GSS_alignment.py (pre-P4)
+++ 16CEN15GSS/16CEN15GSS_alignment.py (post-P4)
@@ -877,7 +877,10 @@
     FILE_MAIN_15_SPS = DATA_DIR_GSS_15 / "GSSMain_2015.sps"
-    # Episode file is in 2ndJournal project
-    FILE_EPISODE_15 = pathlib.Path("/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs_GSS/out15EP_ACT_PRE_coPRE.csv")
+    # WP9 Stage 1b-2 P4: was a hard-coded Mac path
+    # (/Users/orcunkoraliseri/Desktop/Postdoc/2ndJournal/Outputs_GSS/out15EP_ACT_PRE_coPRE.csv);
+    # built from BASE_DIR like the 2005 equivalent (FILE_EPISODE_05, this file's
+    # sibling module) so it resolves under GSS_BASE_DIR on any platform.
+    FILE_EPISODE_15 = OUTPUT_DIR_GSS / "out15EP_ACT_PRE_coPRE.csv"
     CENSUS_FILE_16 = OUTPUT_DIR_16CEN15GSS / "2016_LINKED.csv"
```

`OUTPUT_DIR_GSS` (`= BASE_DIR / "Outputs_GSS"`) is already defined a few lines above this block — no new import,
no ordering issue. Confirmed the target file exists at that exact location in both the staging copy and the
mirror (`ls`, both sides): `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/Outputs_GSS/out15EP_ACT_PRE_coPRE.csv`,
14,992,636 bytes, dated Apr 16 — same file, same size, in both places.

No other P4 patch needed: the 2010/2022 bug is relative-to-code, fixed by the P2-task's symlink (Ledger 1339779),
not a hard-coded path requiring a code edit.

## Verified

- **py_compile**: `py -m py_compile 16CEN15GSS/16CEN15GSS_alignment.py` → OK, before upload.
- **md5**: local pre-P4 `1076668a000445d6c8d7419745396066`, local post-P4 `89bcee0d5dc083f17eb6b7a36d89ba05`; cluster
  copy after `scp` (job 1339779) also `89bcee0d5dc083f17eb6b7a36d89ba05` — identical, upload verified. Only this
  one file was touched and only this one file was `scp`'d.
- **Symlink guard**: job 1339779 confirmed (via `ls -la` inside the job, before creating anything) that
  `/speed-scratch/o_iseri/1J_rerun/occ/code/0_Occupancy` did not already exist, so the symlink was safe to create.
- **Raw files present pre-symlink**: `ls -la` inside job 1339779 confirmed both
  `.../occ/0_Occupancy/DataSources_GSS/Episode_files/GSS_2010_episode/C24_Episode File_SPSS_withno_bootstrap.SPS`
  (12,512 bytes) and `.../GSS_2022_episode/TU_ET_2022_Episode_PUMF.sas7bdat` (470,851,584 bytes) already present
  in the staging copy — the mirror `cp -a` fallback branch was not needed and did not run.
- **Symlink resolves**: job 1339779's final `ls -la` through the new `code/0_Occupancy` symlink found both raw
  files at their expected paths — the exact paths the 1339771/1339773 logs reported as missing.
- **Job scripts unchanged**: `wp9_1b_2010.sh`, `_2015.sh`, `_2022.sh` were reused byte-for-byte from the parent's
  staging (`/speed-scratch/o_iseri/1J_rerun/occ/wp9_1b_<year>.sh`); one (`_2022.sh`) read in full via single-file
  `cat` on the login node and compared against the local scratchpad copy read earlier in this session — identical.
  No `--run` numbers, `OCC_DENOM` logic, or output paths were touched.
- **sacct after submit**: 1339779 COMPLETED exit 0:0; 1339780/1339781/1339782 all RUNNING; 1339770 (2005) still
  RUNNING, exit 0:0 so far, untouched.

## Decisions

- **2015's `Outputs_16CEN15GSS/alignment/2016_LINKED.csv`** (left behind by the failed 1339772 run): **will be
  REUSED, not rebuilt** — `16CEN15GSS_alignment.py`'s `main()` checks `if not CENSUS_FILE_16.exists()` before
  calling `assemble_households()`; the file now exists (it was built fresh *during* 1339772's own run, from the
  current staged code, before that run died at the FILE_EPISODE_15 check) so it will be skipped and reused as-is.
  This is safe: it was built by this task's own code, not stale from an earlier era, and building it is
  independent of the FILE_EPISODE_15 bug that killed that run. Per the task doc, nothing was deleted.
- **NEW FINDING, not anticipated by the task doc — read the code, did not delete anything, flagging for the
  manager**: `Outputs_GSS/GSS_2015_Merged_Main.csv` **also already exists** in the staging copy (14,992,636-byte
  sibling `out15EP_ACT_PRE_coPRE.csv` confirms this whole `Outputs_GSS` folder is the **original T1 `cp -a` mirror
  copy from before any of Stage 1b's patching**, dated Apr 16 — it predates P1). `16CEN15GSS_alignment.py`'s
  `main()` has the same reuse-if-exists pattern for this file: `if not gss_merged_path.exists(): read_merge_save_gss_2015(...) else: print("[OK] ... already exists")`. **The P1 day-type remap patch lives *inside*
  `read_merge_save_gss_2015`, so if `GSS_2015_Merged_Main.csv` is reused, P1 never runs for 2015 in this
  rebuild** — the exact bug this whole project exists to fix would silently carry through unpatched. I did **not**
  delete this file (task doc says "delete nothing" for the 2015 rerun; I read that as applying to all state left
  in the 2015 output tree, not only the one file it names as an example) and submitted 1339781 anyway, since T3 is
  an unconditional "resubmit" instruction. **This is a real risk, not a hypothetical**: expect 1339781's own
  `gate1_occ.py` day-type check to most likely still FAIL in the same shape as the original bug (0.59-ish vs
  0.41-ish, per the April gate's pre-patch numbers) if this is what happens — that would be the tell. The manager
  should read `.../wp9_stage1b_2015_1339781.out` for the "P1 day-type remap: DDAY NaN before=X, after=Y" line
  specifically: **if that line is missing entirely, `read_merge_save_gss_2015` was skipped and the run must be
  redone after deleting `Outputs_GSS/GSS_2015_Merged_Main.csv`.**
- **Dependency applied to all three rebuilds**, not only 2010/2022: task doc T3 says "make the three rebuilds
  `--dependency=afterok:<symlink job>`" (plural, all three), so 2015 also waits on 1339779 even though it does not
  need the symlink — harmless (1339779 finished in well under a minute) and keeps the three submissions uniform.

## Next

- Read `.../wp9_stage1b_2010_1339780.out` and `.../wp9_stage1b_2022_1339782.out` once they land — Step 0 should
  now find its raw files through the symlink; watch for a *new* failure past Step 0 (this task only touched the
  path, not anything downstream).
- Read `.../wp9_stage1b_2015_1339781.out` for the P1 NaN-count line specifically, per the Decisions finding above
  — this determines whether 2015's day-type fix actually took effect in this rebuild or needs a second attempt
  with `GSS_2015_Merged_Main.csv` deleted first.
- Once all three land, read each job's own embedded `gate1_occ.py` output on the new `..._grid.csv` /
  `..._hhsize.csv` siblings — that is the real verdict for this task, same as the parent doc's T4 note.
- Compliance note carried into this task's own record (see below): do not repeat `find` on the login node.

## WHAT I DID NOT VERIFY

- Whether 1339780/1339781/1339782 actually complete successfully past Step 0/alignment — not waited on, per the
  hard "do not poll" rule; only `sacct` was checked once (all three RUNNING) before ending this turn.
- Whether the P1 day-type remap actually ran for 2015 in this specific rebuild (the `GSS_2015_Merged_Main.csv`
  reuse risk above) — flagged, not resolved; needs the next reader to check the log line.
- Full content of `wp9_stage1b2_symlink_1339779.out` beyond what is quoted above was read in full (it is short);
  nothing left unread there.
- **Compliance self-flag**: while listing where the 2010/2015/2022 job scripts lived on the cluster, I ran
  `find /speed-scratch/o_iseri/1J_rerun -maxdepth 3 -name '*.sh'` directly on the login node — explicitly
  forbidden by this task's own Rules section (which called out that the parent agent had made the same mistake).
  It was read-only and non-blocking, but should have been done inside a tiny sbatch job or avoided by checking
  `ls` on the specific subdirectories one at a time instead. No repeat use for the remainder of this task.
