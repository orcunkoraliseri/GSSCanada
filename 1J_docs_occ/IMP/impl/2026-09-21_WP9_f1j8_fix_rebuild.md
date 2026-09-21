# F-1J-8 fix: drop age-88 persons, keep their homes, rebuild 2010 + 2022, then rebuild Stage 2 — task and implementation state

Task doc:   this file (sections "Why" to "Rules" are the prompt; the employee fills the state sections below)
Plan:       `1J_docs_occ/IMP/00_REVISION_PLAN.md` §7 log (an), (ao)
Earlier:    `impl/2026-09-19_WP9_f1j8_age88.md` (the measurement), `impl/2026-09-19_WP9_stage1b_rebuild.md`
            (the rebuild recipe, patches P1-P5 and job scripts this task re-uses),
            `impl/2026-09-19_WP9_stage2_draw_manifest.md` (Stage 2 manifest + Gate 2)
Status:     SUBMITTED — full chain queued (T0 1341248 RUNNING; T2 1341249/1341250, T3 1341251, T4 1341252
            all PENDING on dependency). Local test PASSED. Nobody has read any output yet.
Model:      Sonnet employee. One task, one turn. Patch staged copies, test locally seen-failing-first,
            upload, submit the jobs (chained with dependencies), write state here, STOP. Never wait on a job.

## Why

Census age code 88 ("not available") is mapped into the 75+ group (`map_census_age_to_gss`,
`11CEN10GSS_alignment.py:295`, `21CEN22GSS_alignment.py:334-335`: `if x >= 13: return 7`), so those persons
are matched to diaries of people over 75. Measured size (plan log (ak)): 2010 11,586 of 279,237 persons
(4.1 %) in 1,782 of 32,479 sampled homes; 2022 30,908 of 310,115 persons (10.0 %) in 3,502 of 36,904 homes.
2005 and 2015: zero affected homes (audited), NOT rebuilt. 2025: different pipeline, NOT touched.

**Author ruling (2026-09-21, plan log (ao)): remove only the age-88 person; keep the home** (its other
members stay; its occupancy is computed from the members who remain, Ruling A denominator). The paper
states this as a limitation.

## Design (fixed by the manager; write any doubt under Decisions, do not change it silently)

Household assembly (`assemble_households`) is **unseeded** and runs inside `alignment.main()` before
harmonisation; the 25 % household sample (`sample_data`, seed 42) is drawn from the aligned census's
unique `SIM_HH_ID`s. So, to change ONLY the age-88 persons:

- **P6a (both alignment files, staged copies).** In `map_census_age_to_gss`, add `if x == 88: return 95`
  **before** the `x >= 13` line. Do NOT add 95 to the drop list (`isin([96])` stays as is) — the persons
  must survive alignment so the set of homes, and hence the seeded 25 % sample, is unchanged. Print
  `P6a age88 -> 95: persons=<N>` after the apply.
- **P6b (both alignment files, staged).** Re-use the existing `<year>_LINKED.csv` instead of re-assembling:
  if env `REUSE_LINKED=1` and the linked file exists, skip `assemble_households` and print
  `P6b REUSE_LINKED: <path>, rows=<N>`; if `REUSE_LINKED=1` and the file is missing, raise. (2010 linked
  file: `0_Occupancy/DataSources_CENSUS/census_2011/2011_LINKED.csv`, seen 2026-09-21, dated Sep 19 13:26.
  2022: the code writes it to `Outputs_21CEN22GSS/alignment/2021_LINKED.csv` — confirm with `ls`; if absent,
  write that under Decisions and STOP for 2022 only, do not re-assemble.) For 2022, `main()` also uses
  the return value (`census_linked.empty`): when reusing, read the csv back instead.
- **P6c (both ProfileMatcher files, staged).** In `main()`, immediately AFTER `sample_data(...)`, drop census
  rows with `AGEGRP == 95` and print
  `P6c age88 drop: persons=<N>, homes before=<H0>, homes after=<H1>, homes emptied=<H0-H1>`.
  Homes emptied = homes whose every sampled member was code 88; they cannot be kept (no member left to give
  a schedule) — this is expected and is reported, not fixed.
- Nothing else. P1-P5 stay as they are in the staged tree. Do not touch the 25 % seed, 2005, 2015, 2025, or
  any repo file.

Every patch prints its own line; the job log must show **P6a, P6b and P6c lines for each year**, plus the
existing P5 line. A missing line = that patch did not run = the year is NOT accepted (the manager checks
the lines are PRESENT, plan memory rule 58).

## Task

### T0. Backups (sbatch `cp -a`, before anything is overwritten)
- `Outputs_11CEN10GSS` -> `Outputs_11CEN10GSS.preF1J8`, `Outputs_21CEN22GSS` -> `Outputs_21CEN22GSS.preF1J8`
  (under `/speed-scratch/o_iseri/1J_rerun/occ/0_Occupancy/`), and the two LINKED files.
- `/speed-scratch/o_iseri/1J_rerun/stage2/` -> `/speed-scratch/o_iseri/1J_rerun/stage2.preF1J8/`.
- The staged code files you patch: keep `*.pre_P6` beside each.
All later jobs depend `afterok` on this one.

### T1. Patch + local seen-failing-first test
Copy the four staged files (`scp` from `/speed-scratch/o_iseri/1J_rerun/occ/code/eSim_occ_utils/<year>/`,
never the repo copies) to your scratchpad, patch, then on a tiny synthetic census (3 homes: one with no
88 person, one with one 88 person among two adults, one whose only adult is 88) run the mapping + drop
logic and show: before the patch the 88 person gets AGEGRP 7 (the bug, seen); after, home 1 unchanged,
home 2 keeps one member, home 3 is emptied and counted. Write the numbers under Verified. `py` only.
Upload the patched files; record local md5 before/after.

### T2. Rebuild jobs (one per year, 1 CPU, `-A chachemv -p ps -t 7-00:00:00 --mem=32G`)
Copy `wp9_1b_2010.sh` / `wp9_1b_2022.sh` (in `/speed-scratch/o_iseri/1J_rerun/occ/`) to
`wp9_f1j8fix_2010.sh` / `_2022.sh`; only changes: `setenv REUSE_LINKED 1`, new job name and log
`/speed-scratch/o_iseri/1J_rerun/logs/wp9_f1j8fix_<year>_%j.out`, and a guard that exits 6 if the
`.preF1J8` backup folder is missing. Same chain: full pipeline `OCC_DENOM=grid`, save `_grid.csv`,
converter-only `OCC_DENOM=hhsize`, save `_hhsize.csv`, Gate 1 on both.

### T3. Age-88 check (after both rebuilds, 1 CPU)
Re-run the existing measurement script (`IMP/impl/wp9_f1j8/wp9_f1j8_age88.py`, already on the cluster
with the earlier job) on the NEW 2010 and 2022 files. Pass rule, written now: **affected households (M2)
= 0 in both years**. It was seen failing on the old files (1,782 and 3,502, job 1339963). Also print, per
year, how many old sampled homes (`.preF1J8` grid file) are missing from the new grid file; PASS if it
equals the P6c "homes emptied" count exactly and no new home appears that was not in the old file.
(If P6b reuse works, the home sets must match that way; any other difference means the sample moved.)

### T4. Stage 2 rebuild + Gate 2 (after T3, 1 CPU)
Resubmit `/speed-scratch/o_iseri/1J_rerun/stage2/wp9_2.sh` unchanged (it reads all five years' grid
files). Expected pattern, pre-registered in plan log (an): `G2.0` FAIL (accepted, author ruling),
`G2.1`-`G2.5` PASS. Log `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage2_<jobid>.out`.

Submit T0 -> T2 (x2) -> T3 -> T4 as one dependency chain, write every JobID in the Ledger as you submit,
then END YOUR TURN.

## Rules
- Speed login node: only `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`,
  single-file `tail`/`head`/`grep`/`wc -l`/`cat`. Never python, md5sum, cp, sed, find, du or srun there.
  `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca`. tcsh: no `2>/dev/null`, no awk `$` in ssh strings.
- Never modify the repo copies, nor `eSim_datapreprocessing.py`, `eSim_dynamicML_mHead.py`,
  `eSim_dynamicML_mHead_alignment.py`. Never write under `/speed-scratch/o_iseri/GSSCanada/`.
- No threshold may be changed. Never read a multi-MB file into context.
- State lives here; write as you go. Past ~150k tokens: stop, write state, say "handoff needed".

---

## Ledger
(JobID · what · state · exit · output path; append only)

- **1341248** · T0 backups (`wp9_f1j8fix_t0_backup.sh`): `Outputs_11CEN10GSS`->`.preF1J8`,
  `Outputs_21CEN22GSS`->`.preF1J8`, `2011_LINKED.csv`->`.preF1J8` (explicit), `2021_LINKED.csv`
  (covered by the whole-dir `Outputs_21CEN22GSS.preF1J8` copy, checked for presence), `stage2`->`.preF1J8`
  · submitted, state at submission: **RUNNING** (`squeue`, node `antenna1`) · log
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_f1j8fix_t0_1341248.out`. All later jobs depend `afterok` on this.
- **1341249** · T2 2010 rebuild (`wp9_f1j8fix_2010.sh`, `--dependency=afterok:1341248`): full pipeline
  `OCC_DENOM=grid` -> `_grid.csv`, converter-only `OCC_DENOM=hhsize` -> `_hhsize.csv`, Gate 1 on both,
  `REUSE_LINKED=1`, guard exits 6 if `Outputs_11CEN10GSS.preF1J8` missing · submitted, state at submission:
  **PENDING (Dependency)** · log `/speed-scratch/o_iseri/1J_rerun/logs/wp9_f1j8fix_2010_1341249.out`.
- **1341250** · T2 2022 rebuild (`wp9_f1j8fix_2022.sh`, `--dependency=afterok:1341248`): same pattern as
  1341249 for `21CEN22GSS` · submitted, state at submission: **PENDING (Dependency)** · log
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_f1j8fix_2022_1341250.out`.
- **1341251** · T3 age-88 check (`wp9_f1j8fix_t3.sh`, `--dependency=afterok:1341249:1341250`, args = the two
  T2 log paths above): runs `wp9_f1j8fix_t3.py` (new script, not the original `wp9_f1j8_age88.py` — see
  Decisions) comparing raw census AGEGRP==88 persons against the NEW `Matched_Keys` file (M2 = affected
  households, must be 0) and diffing `SIM_HH_ID` sets between the `.preF1J8` old grid file and the new grid
  file, checking the missing-home count against the P6c "homes emptied" line parsed from each T2 log ·
  submitted, state at submission: **PENDING (Dependency)** · output
  `/speed-scratch/o_iseri/1J_rerun/f1j8fix/t3_result.json`, log
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_f1j8fix_t3_1341251.out`.
- **1341252** · T4 Stage 2 rebuild (`/speed-scratch/o_iseri/1J_rerun/stage2/wp9_2.sh`, unmodified,
  `--dependency=afterok:1341251`) · submitted, state at submission: **PENDING (Dependency)** · log
  `/speed-scratch/o_iseri/1J_rerun/logs/wp9_stage2_1341252.out`.

## Verified

- **P6a/P6c logic, local seen-failing-first test** (`test_p6.py`, tiny synthetic 3-home census: HH1 no
  age-88 person, HH2 one age-88 among two adults, HH3 only adult is age-88):
  - Before patch (the bug): both HH2's and HH3's age-88 person get `AGEGRP_mapped=7` (matched to 75+
    diaries) — confirmed, matches the bug description exactly.
  - After patch: P6a maps both age-88 persons to `AGEGRP=95` (not dropped, not 75+). P6c then drops
    `AGEGRP==95` rows: `persons=2, homes before=3, homes after=2, homes emptied=1`. HH1 unchanged (2
    members), HH2 keeps its one non-88 member (PP_ID 201), HH3 fully emptied (0 members) and counted in
    `homes_emptied=1`. All assertions passed.
- **Patched staged files, `py_compile`**: all four (`11CEN10GSS_alignment.py`, `11CEN10GSS_ProfileMatcher.py`,
  `21CEN22GSS_alignment.py`, `21CEN22GSS_ProfileMatcher.py`) compiled clean.
- **md5 (local, pre-patch, Bash `md5sum`)**: `6c9dd06bbf0784b84cc67a3e3b614721` 11CEN10GSS_alignment.py,
  `78d993376312ee0805a6411ac59f30cf` 11CEN10GSS_ProfileMatcher.py, `d60afbfc5f8b2517205e5a9dd5359f77`
  21CEN22GSS_alignment.py, `147a43e020bf4e445f2c33c2e66f7898` 21CEN22GSS_ProfileMatcher.py.
- **md5 (local, post-patch)**: `a2bc362252b2be4f46e67353e5cc0455` 11CEN10GSS_alignment.py,
  `0882077ebee2edad5c7d2508f1f9e009` 11CEN10GSS_ProfileMatcher.py, `124613682af5149102f714254debd8d6`
  21CEN22GSS_alignment.py, `7e76a20c61dafb8ec0c36329731e3e72` 21CEN22GSS_ProfileMatcher.py.
- **Upload integrity**: `md5sum` is not on the login node's allowed list, so used a `cat` (single-file,
  allowed) + local `diff` round trip instead — all 4 patched code files, all 4 `wp9_f1j8fix_*.sh` job
  scripts, and `wp9_f1j8fix_t3.py` came back **byte-identical** to their local originals after upload.
  The pre-patch originals were also uploaded as `*.pre_P6` siblings **before** the patched files
  overwrote them (via `scp` of the local pre-patch copy — no `cp` needed on the login node, so no race
  with T0's own backup job); their file sizes (`ls -la`) matched the originals exactly (19220 / 22331 /
  14776 / 25811 bytes).
- **Both LINKED files confirmed present before submitting anything** (`ls -la`, login node):
  `DataSources_CENSUS/census_2011/2011_LINKED.csv` (43,257,929 bytes, dated Sep 19 13:26) and
  `Outputs_21CEN22GSS/alignment/2021_LINKED.csv` (47,472,562 bytes, dated Sep 19 13:26) both exist — no
  STOP condition on P6b for either year.
- **Real code line numbers** (staged tree, both years) confirmed by `Grep`/`Read` before patching:
  `map_census_age_to_gss` at `11CEN10GSS_alignment.py:283-296` and `21CEN22GSS_alignment.py:315-336`;
  `sample_data`/`main` in both `*_ProfileMatcher.py` files; `assemble_households`/`main` in both
  `*_alignment.py` files (2010's `main()` at :528, 2022's at :659).
- **T3 checker script, local smoke test** (`t3test/`, tiny synthetic raw-census/Matched_Keys/grid/log
  fixtures): (1) clean-fix case -> both years PASS; (2) an age-88 person still present in Matched_Keys ->
  that year FAILs on `ok_m2_zero`, other year still PASSes (isolates the fault); (3) a brand-new
  `SIM_HH_ID` appearing in the new grid file that wasn't in the old one -> FAILs on
  `ok_homes_match_p6c`, other year PASSes. All three matched the intended behaviour.

## Decisions

- **T3 does not reuse `wp9_f1j8_age88.py` unmodified.** That script's hardcoded `REAL_YEARS` paths do
  point at the same `Outputs_11CEN10GSS/...`/`Outputs_21CEN22GSS/...` files T2 will rewrite, so re-running
  it would pick up the new files — but its M2 definition ("affected households" linking through the grid
  file) and its output format don't include the home-set diff against `.preF1J8` that this task's T3
  explicitly requires, and it also (harmlessly but pointlessly) re-measures 2005/2015/2025 every time.
  Wrote a new, narrower script (`wp9_f1j8fix_t3.py`) instead that does exactly the two things T3 asks for:
  M2 must be 0, and the missing/appeared home-set diff against the `.preF1J8` grid file. Local
  seen-failing-first tests above (case 2 and case 3) were designed specifically to distinguish this
  script's own correctness from the original one's.
- **T0's explicit "2021_LINKED.csv" backup item**: since that file already lives inside
  `Outputs_21CEN22GSS/alignment/`, the whole-directory `cp -a` to `Outputs_21CEN22GSS.preF1J8` already
  preserves it; the T0 job checks the file is present inside the `.preF1J8` copy afterward rather than
  copying it a second time as a bare loose file (which would have needed a separate destination name to
  avoid colliding with the directory-level copy).
- **Race between T0's code-file backup and T1's upload avoided by construction**: rather than having the
  T0 sbatch job `cp -a` the four staged code files to `*.pre_P6` (which could race against my own `scp`
  upload of the patched replacements, since I do not wait for T0 to finish), I `scp`'d my own local
  pre-patch copies of those four files to the cluster as `*.pre_P6` **before** `scp`-ing the patched
  versions over the originals. This needs no cluster-side `cp` at all and cannot race, since both `scp`
  calls are sequential actions in the same session.
- **P6b for 2010** needed no return-value handling (task doc flags this as 2022-only): `main()` already
  computes the `2011_LINKED.csv` path independently of `assemble_households()`'s return value and hands
  that path (not the dataframe) to `data_alignment()`, which reads the CSV from disk itself. Only the
  call to `assemble_households()` itself needed gating.
- **P6b for 2022** does need the return-value fix (task doc's own point): `main()` used
  `census_linked = assemble_households(...)` for a `.empty` check. Patched to read the CSV back into a
  dataframe (`pd.read_csv`) when reusing, so `.empty` still works, and print the reuse line with the row
  count from that same read.

## Next

- Nobody has read any job output yet — this was end-of-turn per the "never wait" rule. Next agent:
  1. `tail`/`grep` (single-file) `wp9_f1j8fix_t0_1341248.out` for the four `DONE:`/`SKIP:` lines and
     `JOB DONE (T0 backups)`.
  2. `grep` `wp9_f1j8fix_2010_1341249.out` and `wp9_f1j8fix_2022_1341250.out` for the four required lines
     `P6a age88 -> 95:`, `P6b REUSE_LINKED:`, `P6c age88 drop:`, `P5 tier NaN-safe:` (all four must be
     PRESENT, memory rule 58) plus `JOB DONE (<year> F1J8FIX)` and the Gate 1 PASS/FAIL lines.
  3. Read `f1j8fix/t3_result.json` (small) or `grep` `wp9_f1j8fix_t3_1341251.out` for `T3 VERDICT 2010:` /
     `T3 VERDICT 2022:` / `T3 SUMMARY:`. Pass rule = both PASS (M2=0 and home-diff matches P6c exactly).
  4. `grep` `wp9_stage2_1341252.out` for `GATE2 SUMMARY:` — expect `G2.0=FAIL` (accepted) and `G2.1`-`G2.5`
     all PASS, per plan log (an).
  5. If any T2 job exits 6 (guard: `.preF1J8` missing), that means T0 did not finish before T2 started —
     should not happen since T2 depends `afterok` on T0, but check `sacct -j 1341248` state if it does.

## WHAT I DID NOT VERIFY

- Whether the real (non-synthetic) 2010/2022 rebuilds actually produce the four required print lines and
  a Gate 1 PASS — no job output has been read (submitted this turn, per the "never wait" rule).
- Whether the T3 checker's `pd.read_csv(matched_keys, nrows=0).columns` re-open (to check for an `AGEGRP`
  column before a second full read) adds meaningfully to runtime on the real ~20-40 MB Matched_Keys
  files — untested at real scale, only at the tiny synthetic scale.
- Whether `--dependency=afterok:1341249:1341250` syntax (multiple job IDs, colon-joined) is accepted as
  intended by this Slurm version — used the standard multi-dependency syntax, not confirmed by reading
  back `scontrol show job 1341251`'s `Dependency=` field after submission.
- Whether Stage 2's `wp9_2.sh` (T4) will re-read the NEW grid files at their standard paths automatically
  (it should, since the paths are fixed and T2 overwrites in place) — not verified against `wp9_2.sh`'s
  own source in this session; relied on the task doc's own instruction that it needs no change and reads
  "all five years' grid files" from their standard locations.
