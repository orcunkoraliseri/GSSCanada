# TASK (employee, Sonnet): 5J Step 6 part B0: the reported (not gated) analyses, written and locked BEFORE the scoring job

Written 2026-10-01 01:08 EDT by the 5J manager (`date` before every stamp you write). Why: spec `Step6_docs/5thJ_06_sealedScoring.md`
6A lists two REPORTED analyses (thermal-mass lag, mild-climate cooling) and 6D adds a third (level versus timing). All three need
the test truth, and the test truth may be read only inside the ONE scoring job. So the analysis code is written now, run on
VALIDATION (seen working, numbers recorded), md5-locked, and the scoring job calls the locked copy once with `--test`.
Read first, in full: the Step 6 spec (6A, 6B, 6D), `Step6_docs/impl/2026-09-30_wp4_scoring_TASK.md` (hard rules bind you),
`Step4_docs/outputs_step4/gates_frozen.md` sections 0-2 (runs, targets, pair rule), `tools/speed/5thJ_04_scorer.py` lines 60-120
(how runs are listed and read, `read_run`, open log) and `Step5_docs/outputs_step5/winner.md`.
State file: create `Step6_docs/impl/2026-10-01_wp4_reported.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules
* Speed sbatch only; nothing on the local CPU. Login node: sbatch/squeue/sacct/scancel/scontrol/scp/ls and single-file
  cat/tail/grep/wc/head only. Spain + Italy only; never a UK file; no folder-wide search or wildcard.
* 🔴 In this task you run the script on VALIDATION only (lists `validation`, `b0_dev`, `b0_val` through `split_loader.load_split`).
  The `--test` path is written but NEVER executed by you; a planted call with `--test` and no lock file must REFUSE (exit 9)
  and that refusal is the only `--test` run you do (on a scratch copy of the script with ROOT pointing at an empty folder).
* CPU budget: one job, `-c 4 --mem=32G -p ps -t 7-00:00:00 --exclude=antenna1`, submitted with
  `--dependency=afterok:1405055` (Step 5 scorers must be done so all 5J jobs stay <= 30 CPUs). Never wait: submit and end.

## The script `tools/speed/s6_reported.py --pred <S folder> --split <list> --out <dir> --tag <tag> [--test]`
Reads truth like the frozen scorer (same layout, same open log `openlog_<tag>.tsv`, same list check), predictions from
`--pred`, household drivers from the store that belongs to the split (`train/store/` for validation; `test/store/` for test,
same columns). Writes `<out>/reported_<tag>.txt` (one line per result, `REPORTED <analysis> country=.. class=.. ...`) and
`<out>/reported_<tag>.parquet`. All INFO; no PASS/FAIL words except the script's own CHECK lines.
1. **Thermal-mass lag** (spec 6A, RQ3), runs of the split, per flat: Pearson cross-correlation between people at home (driver)
   and heating, hourly, over the heating hours of the year (hours where EnergyPlus heating > 0 in that flat; skip the flat if
   fewer than 500), at lags 0..+24 h (heating after presence); lag of the peak for S and for EnergyPlus. Report per country x
   class: number of flats, median lag EP, median lag S, share of flats with |lag S - lag EP| <= 1 h.
2. **Mild-climate cooling** (spec 6A), per climate (6) x class: annual cooling per flat, S vs EP: median relative error,
   and the R² of the annual PAIR effect on cooling (pairs by the frozen pair rule, gates_frozen section 1) with its pair count.
3. **Level versus timing** (spec 6D), per country x class x target (heating, cooling): for each pair, x1 = difference of annual
   people-hours, x2 = difference of annual appliance kWh (design level x fraction, from the store), y = annual pair effect.
   Ordinary least squares y ~ x1 + x2 (with intercept): R² for y = EP's effect and for y = S's effect, pair count.
   "Share of the pair effect explained by level" = that R².
CHECK lines (each PASS/FAIL, printed): pair count per cell equals the frozen scorer's `pairs=` for the same list and model
(read the scorer's score file for the validation run of S3: `train/score/score_S3.txt`); a planted copy of one EP file with
heating shifted by +6 h moves the EP lag of that flat by 6 h (seen failing); a planted constant S cooling gives a cooling
pair R² <= 0 (seen failing); `--test` without `/speed-scratch/o_iseri/5J/gates_frozen_amend1.md5` present refuses with exit 9.

## Run (validation, S3)
`--pred /speed-scratch/o_iseri/5J/train/pred/S3 --split validation --out /speed-scratch/o_iseri/5J/train/reported/ --tag S3_val`.
Then lock: copy to `/speed-scratch/o_iseri/5J/freeze/s6_reported.py`, chmod 444, append its md5 line to a NEW file
`/speed-scratch/o_iseri/5J/freeze/s6_reported.md5` (chmod 444). Record the md5 and every REPORTED/CHECK line in the state file.

## Report back (short, plain)
JobID; the CHECK lines; one REPORTED line per analysis for one cell; the locked md5; status. Next = "manager verifies; the
scoring job (part B) gets one more call: the locked s6_reported.py with --test on the three test lists".

## What the manager will re-derive
One thermal-mass lag of one flat and one level-versus-timing R² from the validation files with own code.
