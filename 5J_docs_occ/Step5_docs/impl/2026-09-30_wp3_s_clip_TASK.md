# TASK (employee, Sonnet): 5J Step 5 part C-bis: static input clip (rules AMENDMENT 2), re-smoke, re-run the 16-config grid

Written 2026-09-30 21:20 EDT by the 5J manager (`date` before every stamp you write). Read first, in full:
`Step5_docs/outputs_step5/step5_rules.md` (THE RULES; read AMENDMENT 2 at the end twice; md5 must be
65e54b5c3c69351fb7dd10fa4ac26345, same as `/speed-scratch/o_iseri/5J/train/step5_rules_amend2.md5`),
`Step5_docs/impl/2026-09-30_wp3_s_TASK.md` (the part C task; its hard rules bind you unchanged),
`Step5_docs/impl/2026-09-30_wp3_s.md` (part C state + manager sections), `tools/speed/s5_data.py`, `tools/speed/s5_train.py`
(lines 100-160 and 180-320), `tools/speed/s5_smoke.sbatch`, `tools/speed/s5_grid.sbatch`.
State file: create `Step5_docs/impl/2026-09-30_wp3_s_clip.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules (short)
Speed sbatch only; nothing on the local CPU (py_compile runs inside the jobs). Login node: sbatch/squeue/sacct/scancel/
scontrol/scp/ls and single-file cat/tail/grep/wc only. GPU jobs exactly as in the part C task (`-p ps
--gres=gpu:nvidia_a100_2g.20gb:1 -c 3 --mem=48G -t 7-00:00:00 --exclude=antenna1`); grid array `%4` (the account allows 4 GPU
slices at once; 12 CPUs + B1 6 = 18 of 5J's 30). Development / validation only; never test, unused or loco lists. Spain + Italy
only, never a UK file, no folder-wide search or wildcard. Never touch job 1404525 / 1404526 (B1) or anything named
`openubem_t07`. Never wait: submit, write JobIDs, end. At most 6 sacct checks of 30 s per job.

## What changes (and nothing else)
1. `tools/speed/s5_data.py`, static block of `Data.__init__` (the `# --- static vector` lines):
   * when `stats is None` (development): after computing mean and sd, z-score the development static matrix and store
     `stats["zmin"]`, `stats["zmax"]` = per-column min and max of those z values (lists of floats, same order as `s_cols`);
   * always: after z-scoring, `s = np.clip(s, zmin, zmax)` using `stats["zmin"]`, `stats["zmax"]`; if either key is missing,
     `raise KeyError("static_stats without zmin/zmax (rules AMENDMENT 2): refusing to load unclipped")`;
   * print ONE line per Data build: `STATIC_CLIP split=<split> rows=<n> values_clipped=<count> columns_clipped=<names with
     count > 0, comma-joined>` (the count is taken BEFORE clipping: values outside [zmin, zmax]);
   * climate one-hot columns are appended after the clip, unchanged.
   Nothing else in the file changes. `s5_train.py` already saves `dtr.stats` into `best.pt` (`static_stats`) and
   `norm_static.json`, so the bounds travel with every checkpoint; check this, do not re-write it.
2. Copy the patched `s5_data.py` to `/speed-scratch/o_iseri/5J/train/` (scp). Record old and new md5.
3. Void the cancelled grid (lesson: a resume must not reuse runs built from OLD inputs): in a small CPU job, `mv
   /speed-scratch/o_iseri/5J/train/ckpt/S /speed-scratch/o_iseri/5J/train/ckpt/S_void_1404570` and print `ls` of
   `ckpt/` before and after; `ckpt/S` must not exist after. Do the same for `ckpt/smoke` -> `ckpt/smoke_void_1404569`.
4. Smoke checks: add to the smoke path of `s5_train.py` (the `--smoke` branch; add, do not remove any CHECK):
   * `CHECK clip_dev_zero PASS|FAIL` : development `values_clipped` == 0 (it is its own range);
   * `CHECK clip_val_fires PASS|FAIL` : validation `values_clipped` > 0 AND `s_v_c` is among the clipped columns (the
     `es_B40` building, AMENDMENT 2);
   * `CHECK clip_bounds PASS|FAIL` : max over validation of the clipped static matrix <= max zmax + 1e-6 and min >= min zmin
     - 1e-6;
   * `CHECK clip_refuses_old_stats PASS|FAIL` : building `Data("validation", dev, stats={mean, sd only})` raises KeyError
     (seen failing: the old path would have loaded silently);
   * the existing reload-to-4-dp check must still PASS on the new checkpoint (it now carries zmin/zmax).
5. Submit the smoke job (`s5_smoke.sbatch`, unchanged) and the grid (`s5_grid.sbatch`, unchanged except the array throttle in
   the sbatch call: `--array=0-15%4 --dependency=afterok:<smoke>`). Same `s5_grid.json` (print its md5; it must equal the
   md5 printed by job 1404570's logs: read `logs/s5_grid_1404570_0.out` with `grep "grid json md5"`).
6. Ledger: JobIDs, md5s (old/new `s5_data.py`, `s5_train.py`), the void move output. `Step5_docs/outputs_step5/models.md`:
   additive section "S grid (re-run under AMENDMENT 2)" with the JobIDs; mark the 1404570 rows VOID (do not delete them).

## Report back (short, plain)
JobIDs; md5s; the void-move `ls` lines; Status; Next = "manager reads smoke CHECK lines; grid runs".

## What the manager will re-derive
With own code in a Speed job: the clip bounds from the raw development static columns; es_B40 `s_v_c` after clipping equals
the development max z; one validation window's static vector from a re-run checkpoint equals the manager's own clipped vector.
