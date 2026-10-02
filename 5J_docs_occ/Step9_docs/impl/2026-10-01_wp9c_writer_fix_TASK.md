# 5J Step 9c AMENDMENT 3: fix the writer test and re-run it (task doc for a fresh employee)

Written 2026-10-01 16:57 EDT by the 5J manager. Parent: `Step9_docs/impl/2026-10-01_wp9c_idf_writer.md` (read AMENDMENT 2 and the
manager note at its end first; you append an "AMENDMENT 3" section there, same headings). Log: `Step9_docs/5thJ_09_modelA.md`.

## What the manager read (2026-10-01 16:54-16:56, Speed, `/speed-scratch/o_iseri/5J/step9c/win/`)
* Array 1407091: all 26 tasks FAILED. 20 tasks exit 2 in 0-1 s with `unresolved schedule ../../schedules/<stem>/<stem>_F0_dwelling_0_f000_gain.csv`
  (every R0, R1, D, P1, P2). Cause: the gain schedules were copied to `win/<D>/schedules/<stem>/`, but `../../schedules` from
  `win/<D>/idfs/` is `win/schedules/`, which does not exist. (The old no-window layout `step9c/schedules/` is one level higher.)
* The 6 O runs completed (rc 0) but the task exited 1 because `win_summ.py` printed `tbl_error: neither window table found in
  eplustbl.csv`. The tables ARE in the file (`grep -c "Window-Wall Ratio\|Exterior Fenestration"` = 8 in
  `runs/7307694dddf93fb6_O/eplustbl.csv`); the parse tests `r[0] == "Window-Wall Ratio"` (lines 66 and 77), very probably the
  wrong column.
* G-c3 PASS 6/6 (equipment equals design x series exactly). G-c1, G-c2, G-c4, G-c5 not evaluable.
* Run O heating (kWh/yr): 7307694dddf93fb6 420, b3f8d90890ff6314 503, but 1271cddbf6bd1e8a 84,744, 504fa19567bbc2b7 30,918,
  1ef46361a8060ff9 61,578 (919761afea1827b3 see its JSON). Two buildings with almost no heating in Madrid and Bologna winters is
  not plausible on its face and must be explained.
* `runs/1271cddbf6bd1e8a_O/eplusout.err` line 101: `** Severe ** GetSurfaceData: There are 12 degenerate surfaces` (the building
  has 12 outdoor triangle walls). The run still completed; G-c5 must not call a run with a Severe line clean.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). Only `ES-MAD-BERRUGUETE` and `IT-BOL-GALVANI2`.
* **No folder-wide or repo-wide search, no recursive listing, and no wildcard of any kind** (FINDING 5J-2, 5J-4). Open files by full
  name; list only `/speed-scratch/o_iseri/5J/step9c/win/` and its own sub-folders, one level at a time.
* **Compute:** Speed via `sbatch` only (`-t 7-00:00:00`, `--exclude=antenna1`, at most 12 CPUs at once for this task). Never python
  or bash loops on the login node (tcsh there: write a script, scp it, run it with `sbatch`). Submit with dependencies, write the ids,
  end the turn. Never wait for a job.
* Write only: `win/` on Speed, `tools/5thJ_modelA_idf.py` (additions only), the writer state file. This base is NOT final
  (FINDING 5J-5: walls face inward; OpenUBEM is rebuilding), so the goal is working code, not final numbers.

## What to do
1. **Schedules:** make `../../schedules/...` resolve from `win/<D>/idfs/` without changing any IDF (e.g. move the copies to
   `win/schedules/<stem>/`; check no stem exists in both districts). Show one resolved path per building with `ls -l` of the file.
   Fix the writer so the next build puts them in the right place, and make its presence check resolve paths the way the task
   script does (from the idfs folder), so this fault is caught on the desktop next time.
2. **Window tables:** read the first 40 lines around "Window-Wall Ratio" in one kept `eplustbl.csv` (`grep -n` then `sed -n`),
   fix both parses in `win_summ.py` (and the writer's local copy if any), re-run ONLY the summarizer on the 6 kept O run folders
   (one sbatch job) and show the two areas per building against `window_m2`.
3. **Failed-check honesty:** make the summarizer report `severe` > 0 as not clean in G-c5 (it must FAIL on 1271cddbf6bd1e8a_O),
   and write the degenerate surface names (the err lines after line 101) into the state file.
4. **Re-run:** resubmit the 20 failed tasks (`--array=<list>%12`) and the aggregator with `afterany`. G-c1 needs P1 to FAIL and
   G-c2 needs P2 to FAIL (count differs by 1), as AMENDMENT 2 defined.
5. **Near-zero heating (explain, do not fix):** for 7307694dddf93fb6 and b3f8d90890ff6314 versus one normal building, read from
   the kept O runs: conditioned floor area (eplustbl "Building Area"), heating and cooling per m2, the heating setpoint schedule
   name and its winter value in the IDF, the heating availability schedule, the infiltration objects, and January mean zone air
   temperature if output. State the most likely cause with the line that shows it. If you cannot tell, say so.
6. **Manager note 16:10 (FINDING 5J-5):** from one completed D run's `eplustbl.csv`, the "Surface Azimuth" EnergyPlus reports for
   one outdoor wall vs the outward azimuth from its vertices (Newell normal, then the point-in-floor test of the parent state);
   expected about 180 degrees apart on this base.
7. **Timing:** wall seconds per run type (R0, D, O) per building for D9-4.

## Done means
Each fix shown failing before and passing after; jobs submitted with ids in the ledger; a `Next` that names the aggregator log and the
lines a cold agent copies under Verified. Nothing UK opened, listed or passed. End with "job N submitted, state written to <path>".
