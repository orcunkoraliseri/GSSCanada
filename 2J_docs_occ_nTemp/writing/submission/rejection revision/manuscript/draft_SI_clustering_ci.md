# SI Section: Clustering-Aware Confidence Intervals for Load Factor and Midday Share

Draft written by the manager, 2026-09-20, delivering the promise made in the main text
(`draft_S2_framework.md:338-340`: "This interval treats households as independent and does not
account for households sharing a city or an archetype; the consequence of that clustering is
examined in the Supplementary Information."). This is plan item 39's Ruling 1. Numbers below are
read directly from job output on the cluster (T67), not copied from any earlier draft or from the
retired, mislabeled bootstrap that produced the "1.0-3.3% narrower" figure once quoted internally
(never in any manuscript draft) — that figure is invalid and is reported here only as a labeled,
do-not-quote historical control.

This part is scoped to the clustering check only. It does not set the main-text point estimates for
load factor or midday share change — those belong to the results section (WP6/WP11, not yet
started as of this writing) and must be re-read against the cluster-aware interval below once
written, per Ruling 5.

---

## S.10 Does household clustering change the reported uncertainty?

Section 2.11's paired-difference interval (Eq. 16) pools every household's 2022-to-2030 change
together and treats each one as an independent observation. Households sharing a city or an
archetype are not independent in principle, so a genuine cluster bootstrap was run for comparison:
the 24 (archetype, city) cells are resampled with replacement (24 drawn from 24, repeats allowed),
each drawn cell's own paired household deltas are kept intact — no resampling within a cell, since
the cell is itself the resampling unit — and the pooled mean is recomputed over 10,000 replicates
(fixed seed 12345) to build a percentile interval.

Run on the rebuilt 2022/2030 paired data (T21, all 24 cells x 50 households, 2,400 rows, no missing
or short series), the two methods give:

| Metric | Method | Point | 95% interval | Width | Change from plain interval |
|---|---|---|---|---|---|
| Midday share | Plain pooled (main text, Eq. 16) | 0.00732 | [0.00645, 0.00819] | 0.00174 | -- |
| Midday share | Genuine cell-cluster bootstrap | 0.00732 | [0.00616, 0.00859] | 0.00243 | **39.8% wider** |
| Load factor | Plain pooled (main text, Eq. 16) | 0.00494 | [0.00412, 0.00577] | 0.00165 | -- |
| Load factor | Genuine cell-cluster bootstrap | 0.00494 | [0.00413, 0.00574] | 0.00161 | 2.3% narrower |

(All values are raw fractions, i.e. multiply by 100 for percentage points.)

**Plain statement of what this means.** For midday share, accounting for clustering by city and
archetype widens the honest uncertainty band by about two-fifths -- a real, non-trivial effect of
non-independence -- but the interval still excludes zero under either method, so the conclusion that
the 2022-to-2030 change is separable from zero for this metric is unchanged. For load factor,
clustering makes almost no difference (2.3% narrower, i.e. within noise of the same order as the
Monte Carlo bootstrap's own replicate-to-replicate variation); the plain pooled interval is adequate
for this metric on its own. Neither metric's interval crosses zero either way. **This SI section
therefore does not overturn any conclusion reached with the plain interval, but it shows the two
metrics behave differently under clustering, so the plain interval alone understates uncertainty for
midday share specifically.** Whoever writes the main-text point estimate and "separable from zero"
statement for midday share should cite the wider, cluster-aware interval above rather than the plain
one, since it is the more honest number and the two disagree by a material margin (Ruling 5).

**A retired, invalid number, kept only for the record (DO NOT QUOTE).** An earlier script
(`impl/T03_scripts/ci_reproduction.py:67-83`, function `method_b_cluster_bootstrap`) was found to be
a mislabeled *stratified* bootstrap: it resampled households within each of the 24 cells but held
the set of cells fixed in every replicate, which removes between-cell variation rather than
respecting it, and reported an interval 1.0-3.3% *narrower* than the plain one -- the opposite of
what real clustering should do. That run also used the pre-rebuild data, which is separately
disqualified (plan §5 items on the WP1 fix). It is never cited as evidence that clustering is
immaterial, in either this document or the main text.

---

## Number trace table

| Value | What it is | Source | Matches an earlier draft? |
|---|---|---|---|
| 2,400 rows, 24 cells, 50 households/cell, no gaps | Corrected `agg_annual.csv` provenance | `T67/out/run_meta.json` (`n_rows_written: 2400`, `n_cells_found: 24`, `n_missing_facility_column: 0`, `n_short_series: 0`) | n/a, first time computed on rebuilt data |
| Midday share: plain 0.00174 vs cluster 0.00243 (39.8% wider) | Interval widths, corrected data | `T67/out/real_correcteddata/ci_reproduction_t67.csv` | n/a |
| Load factor: plain 0.00165 vs cluster 0.00161 (2.3% narrower) | Interval widths, corrected data | same file | n/a |
| Retired stratified-bootstrap widths 1.05%/3.3% narrower | Historical, invalid, do-not-quote | `impl/T03_out/ci_reproduction.csv` + `run_meta.json`, reproduced exactly by T67's seen-failing control (`T67/out/control_olddata_SEENFAILING/ci_reproduction_t67.csv`) | Matches the figure named in plan item 39's diagnosis, confirming this is the correct retired run to cite as invalid |

## Ledger
- No new cluster jobs run by this write-up task; all three numbers above were read directly from
  T67's completed job output (jobs `1340720`, `1340721`, `1340722`, all `COMPLETED`, exit `0:0`,
  confirmed via `sacct` immediately before this section was written).

## Verified
- `1340720` (`t67_build_agg_annual_t21.py`): `run_meta.json` read in full, `n_rows_written: 2400`,
  `n_cells_found: 24`, all 24 cells listed with `cell_row_counts` of exactly 100 each (50 households
  x 2 years), `n_missing_facility_column: 0`, `n_short_series: 0`.
- `1340721` (seen-failing control, old defective data): CSV read in full, four rows, matches the
  employee's own local functional test to full precision and reproduces the "1.0-3.3% narrower"
  figure from plan item 39's original diagnosis exactly (1.05% / 3.3%).
- `1340722` (real run, corrected data): CSV read in full, four rows, both metrics' point estimates
  identical between the two methods (as expected -- only the interval differs), all four interval
  bounds strictly positive (no interval crosses zero).

## Decisions
1. Wrote this as a new SI file (`draft_SI_clustering_ci.md`, section S.10) rather than appending to
   either existing SI draft, because it is a distinct topic (uncertainty quantification, not model
   selection or schedule completion) and both existing files' own scope statements exclude it.
2. Reported percentages to one decimal place and raw values to five significant figures, matching
   the precision already used elsewhere in `draft_S2_framework.md`'s worked examples.
3. Did not touch `draft_S2_framework.md` itself -- its existing pointer sentence ("examined in the
   Supplementary Information") already covers this without naming a section number, and editing the
   frozen main-text sentence is outside this task's scope (WP10 assembly is what threads section
   cross-references, not this write-up).
4. Did not attempt to write the main-text point-estimate sentence for midday share or load factor
   change -- that is WP6/WP11's job once those tasks start, and doing it here would pre-empt work
   this task was not asked to do. This section only supplies the interval those tasks must use.

## Next
- WP6/WP11 (not yet started): when the main-text results section states the 2022-to-2030 midday
  share and load factor changes and whether they are separable from zero, cite this SI section's
  cluster-aware interval for midday share (the plain interval understates its uncertainty by a
  material margin), and either interval is adequate for load factor.
- WP10 (rewrite/assembly, not yet started): give this file a final SI section number when the whole
  supplementary information is assembled in order (currently drafted as S.10, following S.5-S.9 in
  `draft_SI_schedule_completion.md`); add a section cross-reference at `draft_S2_framework.md:340`
  if the assembled SI's numbering differs from S.10.

## WHAT I DID NOT VERIFY
- Whether any other section of the manuscript (results, abstract, or a table) already states a
  midday-share or load-factor point estimate or interval from an earlier, pre-rebuild source --
  grepped the `manuscript/` folder for these terms and found none outside `draft_S2_framework.md`'s
  Methods definitions, but did not grep the frozen archived (rejected) submission or any tables
  folder, since those are explicitly superseded and out of scope for a rebuilt-data number.
- Whether load factor's 2.3%-narrower result would remain negligible at a different `n_rep` or seed
  -- not re-run at a second seed; the task doc's own control step only required confirming the
  general theoretical direction on old data, which this section does not re-litigate.

## Status: DONE
Draft exists at `manuscript/draft_SI_clustering_ci.md` (this file). Item 39 (plan `00_REVISION_PLAN.md`)
is closed by this section plus the T67 implementation doc. No cluster access used by this write-up
step itself -- it reads T67's already-completed job output only.
