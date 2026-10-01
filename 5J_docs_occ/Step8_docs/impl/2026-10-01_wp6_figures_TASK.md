# TASK (employee, Sonnet): 5J Step 8 part B: Figures 2-4 from frozen Step 6 data (script plots)

Written 2026-10-01 06:10 EDT by the 5J manager (`date` before every stamp you write). Read first: `Step6_docs/outputs_step6/RESULTS.md`,
the Step 6 spec PROGRESS LOG entry of 2026-10-01 05:04 (post-scoring rule for figure-data jobs; it binds you),
`Step4_docs/outputs_step4/gates_frozen.md` sections 0-2 (runs, targets, pair rule), `writing/5J_manuscript_draft.md` (figure
captions and Sections 3.2-3.5), `figures/scripts/generate_5J_graphical_abstract.py` (house style: fonts, sizes, colours).
State file: create `Step8_docs/impl/2026-10-01_wp6_figures.md` (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules
* Speed sbatch only; nothing on the local CPU. Login node as before. All 5J jobs <= 30 CPUs: submit your jobs with
  `--dependency=afterany:1405283` (Step 7 comparison; the CPUs are full until then) and `-c 4 --mem=32G -p ps -t 7-00:00:00
  --exclude=antenna1`. Spain + Italy only; never a UK file; no folder-wide search or wildcard.
* Post-scoring rule: a figure-data job may read test truth and test predictions; it logs every file it opens
  (`figures/data/openlog_<job>.tsv`), writes its table with an md5, writes no verdict or score, and every number it shows that is
  also a scored number must equal `Step6_docs/outputs_step6/scores.parquet` (print the check).
* Journal, not report: no notes, script names, file names, "Figure N" titles or warnings inside an image; captions in the draft
  say what is shown. matplotlib only; PNG 300 dpi + PDF; widths 90 mm (single) or 190 mm (double); 8 pt text minimum.
* Never wait: submit, write JobIDs, end.

## Figures
* **Figure 2 (load accuracy):** for S, B1, B0 and C on the three test lists, the median hourly CV(RMSE) and median |NMBE| per
  target and class-country cell, with the ASHRAE bands (30 %, 10 %) drawn as lines; data from `scores.parquet` only (no truth
  read). Small multiples: rows = targets (heating, cooling, equipment, total electricity), columns = test lists.
* **Figure 3 (occupancy effect, the key figure):** per pair, annual difference sum(dS) against sum(dEP) for S (left) and C (right),
  heating and cooling (rows), pooled over the three test lists with colour = list; 1:1 line; the cell R² values are NOT redrawn
  (they are hourly); annotate nothing in the image. Data job: read test truth + `test/pred/S`, `test/pred/C` for the pairs of the
  frozen pair rule, write `figures/data/fig3_pairs.parquet` (pair id, list, country, class, target, dEP, dS, dC) + md5. Check:
  per cell, the pair count equals `scores.parquet` `pairs`.
* **Figure 4 (peaks and timing):** left: share of dwelling-days with the peak hour within 1 h, per cell, S vs C vs B1 (from
  `scores.parquet` G5J.5 rows); right: per country x class, the EnergyPlus vs S median presence-heating lag and the share of
  flats within 1 h (from `Step6_docs/outputs_step6/reported_S_<list>.txt`).
* Scripts in `figures/scripts/fig02_load_accuracy.py`, `fig03_occupancy_effect.py`, `fig04_peaks_timing.py` (+ the data job
  `fig03_data.py`); outputs `figures/Figure_02_load_accuracy.{png,pdf}`, `Figure_03_occupancy_effect.{png,pdf}`,
  `Figure_04_peaks_timing.{png,pdf}` copied to `5J_docs_occ/figures/` and `writing/figures/`; each with a sidecar
  `.md5.txt` (the image md5 and the md5 of every input table).

## Report back (short, plain)
JobIDs; what each figure shows in one sentence; checks printed; status.
