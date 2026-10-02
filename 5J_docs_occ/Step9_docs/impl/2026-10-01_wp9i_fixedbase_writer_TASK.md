# 5J Step 9i: writer test on the fixed base + fast-setting check + tiny-flat hold-out list (task doc for a fresh employee)

Written 2026-10-01 17:40 EDT by the 5J manager. Parents: `Step9_docs/impl/2026-10-01_wp9c_idf_writer.md` (AMENDMENT 3 = the
working writer test on the OLD base), `Step9_docs/impl/2026-10-01_wp9h_rebase_fixed.md` (fixed base checked), log
`Step9_docs/5thJ_09_modelA.md` (entries 17:08, 17:14, 17:39; D9-4 decision frame 15:50). State file you keep (new):
`Step9_docs/impl/2026-10-01_wp9i_fixedbase_writer.md` (Ledger, Files, Verified, Decisions, Next, WHAT I DID NOT VERIFY).

## What is known
* Fixed base `_win_2026-10-02` (Madrid `ES-MAD-BERRUGUETE`, Bologna `IT-BOL-GALVANI2`): only vertex order changed vs the old base;
  162 / 209 outdoor walls are still inward (sent to OpenUBEM; a later base may follow; the code must not care which base).
  Desktop folders `C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/eu_evidence/EU-11/<D>_win_2026-10-02/`, Speed copies
  `/speed-scratch/o_iseri/fleets/EU11_<D>_win_2026-10-02/idfs`. `tools/5thJ_modelA_idf.py` reads the base from env
  `MODELA_VINTAGE` (set `win_2026-10-02`).
* Old-base writer test (array 1407436, aggregator 1407449, `/speed-scratch/o_iseri/5J/step9c/win/`): schedules layout, window
  table parse and per-run working folder are fixed. Every R0 task exits 1 only on `tbl_error FileNotFound` because the
  delivered IDF has no tabular output; heating is read fine. G-c5 fails every writer-built run only because the writer adds
  `Output:Meter InteriorLights:Electricity` (the models have no lights; lights are not a target).
* Timing probe (`/speed-scratch/o_iseri/5J/step9b/logs/agg_1406899.out`, no windows, heating only): shading updated every 20 days
  instead of daily = 10 to 13 times faster, plus sizing off = 17 to 27 times faster, heating change at most 0.021 %. The written
  IDFs use `ShadowCalculation PolygonClipping, Periodic, 1` and `SimulationControl` sizing Yes/Yes/Yes. The D9-4 frame allows the
  fast setting ONLY if a windowed check with cooling on shows annual heating AND cooling change at most 1 % median and 3 % worst
  per building.
* Tiny flats (author ruled 17:39: hold them out): manager rule = a building is held out of Model A if ANY of its flats has floor area
  under 15 m2 in `Step9_docs/impl/static_win2/flats_<D>.csv` (column `floor_area_m2`). Manager count: 29 Madrid, 83 Bologna.

## 🔴 Rules (binding)
* **UK licence:** never open, list, copy or pass any path, file or argument for the UK (`GB`, `LDN`, `London`, `STDUNSTANS`, `uk`,
  `_uk`). The `EU-11/` folder holds other countries: never list `EU-11/` itself; open the two district folders by full name only.
* **No folder-wide or repo-wide search, no recursive listing, no wildcard of any kind** (FINDING 5J-2, 5J-4). Open files by full
  name; on Speed list only folders you created, one level at a time.
* **Compute:** Speed via `sbatch` only (`-t 7-00:00:00`, `--exclude=antenna1`, at most 16 CPUs at once for this task). Never python
  or bash loops on the login node (tcsh: write a script, scp it, run it with `sbatch`). Desktop work at most 10 processes. Submit
  with dependencies, write the ids, end the turn. Never wait for a job.
* Write only: new Speed folder `/speed-scratch/o_iseri/5J/step9c/win2fix/` (copy the scripts from `win/`, never edit `win/`),
  `tools/5thJ_modelA_idf.py` (additions only; the old behaviour stays reachable), `Step9_docs/impl/heldout_tinyflats_win2.csv`,
  your state file.

## What to do
1. **Hold-out list.** Write `Step9_docs/impl/heldout_tinyflats_win2.csv` (district, stem, n_flats, min_flat_m2, mean_flat_m2,
   split, reason `flat_under_15m2`). The split comes from the sealed lists in `Step9_docs/impl/buildsplit_win2/` (read each of the six
   list files by name). Print counts per district x split and the flats removed. The lists themselves stay untouched (filtering
   happens at use). Check your count against the manager's 29 / 83 and report any difference.
2. **Writer fix: no lights meter.** Remove `Output:Meter InteriorLights:Electricity` from what the writer adds (additive switch is
   fine, but the fixed-base build must not write it). Seen failing then passing: build one IDF without the fix and show the line,
   then with the fix and show `grep -c InteriorLights` = 0. Do NOT whitelist any warning anywhere: G-c5 stays `severe == 0 and
   invalid/not found == 0`.
3. **Summarizer: table only where it must exist.** In the copied `win_summ.py`, a missing `eplustbl.csv` is a fault for every
   writer-built run, and allowed only for R0 (the delivered file). Seen failing: an R1 run folder copy with `eplustbl.csv` removed
   must still exit 3; the R0 run must exit 0.
4. **Build on the fixed base** (`MODELA_VINTAGE=win_2026-10-02`), six buildings, none in the hold-out list: Madrid
   `919761afea1827b3` (large), `1271cddbf6bd1e8a` (triangle, keeps the degenerate sliver walls: its Severe line must still show),
   `0275c53572b2ff9f` (small, replaces tiny-flat `7307694dddf93fb6`); Bologna `504fa19567bbc2b7` (small), `1ef46361a8060ff9`,
   `13c60875a803e164` (replaces tiny-flat `b3f8d90890ff6314`). Run types per building: R0, R1, D, O as in AMENDMENT 2, plus
   **DF** and **OF** = D and O with `ShadowCalculation` update frequency 20 and the three sizing fields `No` (edit printed and
   asserted, as in the timing probe V2), plus P1 on `504fa19567bbc2b7` and P2 on `919761afea1827b3`. Run the writer's
   `schedcheck` on every written IDF before upload. Submit the array (`%16`) and the aggregator with `afterany`.
5. **Aggregator additions:** (a) the old gates G-c1..G-c6 unchanged (P1 must FAIL G-c1, P2 must FAIL G-c2 by a count of 1);
   (b) **fast-setting check:** per building, heating, cooling and equipment of DF vs D and OF vs O, percent change; verdict PASS
   only if median over the 12 pairs is at most 1 % and the worst is at most 3 % for heating AND cooling, and equipment is equal
   within 1e-6 relative; **seen failing:** the same comparator applied to D vs O must print FAIL; (c) wall seconds per run type
   per building and the DF/D and OF/O speed-up; (d) item 6 of AMENDMENT 3: for one outdoor wall per building that the rebase
   check calls outward, the azimuth in `eplustbl.csv` (Opaque Exterior) vs the Newell azimuth from the vertices: must agree within
   1 degree on this base.
6. **Item 5 confirmation (old base, read only):** from `/speed-scratch/o_iseri/5J/step9c/win/results/` read the D and R0 heating
   of `7307694dddf93fb6` and `b3f8d90890ff6314` (73.79 and 98.27 m2) per m2 next to their O runs, to confirm the tiny-flat
   explanation. Read only after array 1407436 has finished (`sacct`); if not finished, leave it in Next.

## Done means
Items 1-3 shown failing then passing; item 4 submitted with ids in the ledger; the aggregator prints every gate in three outcomes
(did not run / ran and passed / ran and failed) and its exit code meaning is written down; a `Next` naming the aggregator log and
the lines a cold agent copies. Nothing UK opened, listed or passed. End with "job N submitted, state written to <path>".

## Manager note 17:41
OpenUBEM confirmed the leftover inward walls (their exact test: Madrid 261 left + 8 flipped by mistake, Bologna 351 + 6; our counts
differ, to be re-measured on their next base) and will deliver a new tag. Treat `_win_2026-10-02` walls as provisional. This task
still runs on `_win_2026-10-02`: its purpose is working code, the fast-setting check and timing; nothing here is final data. Keep every
path to the base behind `MODELA_VINTAGE` so the next tag is a one-line switch.
