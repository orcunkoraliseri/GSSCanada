# T67 -- WP8: build a genuine cell-level cluster bootstrap, rerun on the rebuilt (corrected) data

Task doc written by the manager, 2026-09-20, after item 40 (T66) closed. This is the item-39 fix
(plan `00_REVISION_PLAN.md` lines 3017-3068), dispatched now because it was ruled unblocked and its
fix was already scoped exactly -- see the Rulings block below, copied verbatim from the plan so this
doc is self-contained.

## Background (read once, do not re-derive)

`impl/T03_scripts/ci_reproduction.py:67-83` contains a function `method_b_cluster_bootstrap` that is
**not actually a cluster bootstrap**. It resamples households *within* each (arch, city) cell but
never resamples *which cells* appear in a replicate -- `cell_arrays` is built once, outside the
replicate loop, and every one of the 24 cells appears in every replicate at its exact original size.
That is a **stratified** bootstrap: it holds cell structure fixed and therefore removes between-cell
variation, which is why it reported an interval **narrower** than the plain pooled interval (1.0-3.3%
narrower) -- positive intra-cell correlation should make an honest interval **wider**, never narrower,
so the old result's direction was the tell that the method was wrong, not the data.

A genuine cluster bootstrap resamples **whole cells with replacement** (24 cells drawn from 24, with
repeats), and *within* each drawn cell keeps its own households intact (do not also resample
households inside a drawn cell -- that would be double resampling; drawing the cell already is the
resampling unit).

## Rulings already made (binding, do not relitigate)

1. The SI sentence at `draft_S2_framework.md:338-340` (promises a clustering-aware interval shown
   beside the main-text one) is NOT cut. Deliver it.
2. Nothing from the OLD `method_b_cluster_bootstrap` run may be quoted anywhere, in either direction.
   The "1.0-3.3% narrower" figure is not evidence clustering is immaterial -- it is an artefact of the
   wrong resampling unit, and it was also measured on the pre-WP1-fix defective 2030 rows. Do not let
   it survive into any SI draft as reassurance.
3. The function is renamed at the same time it is fixed (e.g. `cell_cluster_bootstrap`, or similar --
   your choice, but the new name must not contain the word "cluster" attached to logic that isn't one;
   name it for what it actually does).
4. Ownership is WP8 (not WP6) -- this task doc is filed as a WP8 task.
5. It reruns on the **corrected/rebuilt** paired-annual data, never on `outputs_step8/agg/agg_annual.csv`
   (that file carries the pre-WP1-fix defective 2030 rows -- the whole reason the old run was barred).
   Report whatever the honest interval shows -- wider, narrower, or indistinguishable from the plain
   pooled interval. No band is moved and no outcome is assumed in advance.

## What "corrected/rebuilt" data means here -- step 0, do this first, do not guess

The rebuild's 2022 and 2030 main energy runs are T21 (`/speed-scratch/o_iseri/2J_revision/T21/` per
`impl/2026-09-17_T45_T21_collector.md:96`, later re-run clean per plan log (cw): `1340509_15`,
50/50, exit 0). `ci_reproduction.py` expects an `agg_annual.csv` shaped like 24 cells x 50 households
x 5 years, with columns at least `arch, city, sim_hh_id, year, midday_share, load_factor` (see
`build_paired()` in the script). Before writing any bootstrap code:

1. Search the T21 output tree on Speed (`ssh ... find /speed-scratch/o_iseri/2J_revision/T21 -iname "agg_annual.csv"`,
   `find`/`ls` only, no python on the login node) for an already-built aggregate. If one exists and its
   `run_meta.json` or equivalent shows it was built from T21's (rebuilt) hourly outputs, not the old
   `outputs_step8/agg/` tree, use it and record its exact path and how you confirmed provenance.
2. If no such file exists, check whether `08_simulation_val.py` or `08_simulation_plots.py` (both
   reference `agg_annual.csv` as an input, not a thing they build inline from raw hourly meters --
   read the surrounding code to find whichever step actually produces it, likely an earlier Step-8
   aggregation script under `Step8_docs/`) can be pointed at T21's raw output directory to produce a
   corrected `agg_annual.csv`. If you find that script, run it via `sbatch` (never on the login node)
   against T21's raw tree, and confirm the row count and schema before trusting it.
3. If you cannot find or build a corrected `agg_annual.csv` within a reasonable amount of
   investigation (roughly 30-45 minutes of your own work), STOP, write exactly what you tried and what
   is missing in your implementation doc's `## Next` section, and end your turn. Do not guess at a
   path, do not fabricate the file, do not fall back to the old defective one and call it corrected.

## The actual fix (once step 0 gives you a real corrected `agg_annual.csv`)

1. Copy `ci_reproduction.py` to a new file in a new `T67_scripts/` directory (never edit the T03
   original in place -- it is frozen, seen-failing evidence for item 39's diagnosis).
2. In the copy, replace `method_b_cluster_bootstrap` with a genuine cluster bootstrap:
   - Build `cell_arrays` as a list of (arch, city) -> that cell's array of paired deltas, exactly as
     today.
   - Inside each of the `n_rep` replicates, draw **24 cell indices with replacement** from the 24
     available cells (`rng.integers(0, n_cells, size=n_cells)`), then concatenate the (unresampled,
     intact) delta arrays of the drawn cells for that replicate. Do NOT also resample households
     within a drawn cell.
   - Rename the function per Ruling 3.
   - Keep method A (the plain pooled t-interval, `method_a_t_interval`) unchanged -- it is the
     main-text method and stays the baseline for comparison.
3. **Seen-failing control, mandatory before trusting the new code**: run the NEW script against the
   OLD (uncorrected, pre-WP1-fix) `outputs_step8/agg/agg_annual.csv` too, purely to confirm your new
   cluster bootstrap produces a WIDER interval than method A on that data (the theoretically expected
   direction), unlike the old buggy function which produced a narrower one. This is a control, not a
   result -- label it clearly as such in your implementation doc and never let it be quoted as a paper
   number (it still carries the defective 2030 rows).
4. Run the corrected script for real on the corrected `agg_annual.csv` from step 0, both metrics
   (`midday_share`, `load_factor`), 10,000 replicates, fixed seed (reuse 12345 for continuity unless
   you have a reason not to -- record whichever you use).
5. Report, side by side, for both metrics: method A (pooled) point + 95% CI, the new genuine cluster
   bootstrap point + 95% CI, and the old (retired) stratified-bootstrap number labeled "DO NOT QUOTE,
   wrong method, kept for the record only." State plainly whether the genuine cluster interval is
   wider, narrower, or indistinguishable from method A, and by how much.

## Cluster rules (binding, from CLAUDE.md)

- Never run blocking `srun` or bare python on the login node. `sbatch` only, single line, 7-day
  walltime even for short jobs.
- Submit the job(s), write the JobID(s) and every path to your implementation doc, and END YOUR TURN.
  Do not poll, do not background-watch, do not wait. The manager polls.
- Never edit `ci_reproduction.py`, any file under `T03_scripts/`, `archive/`, or any pipeline source
  outside your own new `T67_scripts/` directory.
- Never read a multi-MB file into your context; use `wc -l`, `head`, `grep -n`.
- Write "NOT VERIFIED" rather than guess, at every step, including step 0.

## Implementation doc

Create `impl/2026-09-20_T67_wp8_genuine_cluster_bootstrap_IMPL.md` (or similar name under `impl/`)
with the standard sections (Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFIED) and keep
it current as you go, per the project's no-parking rule.

## Next (for the manager, after this task returns)

Once the corrected interval is in: thread the result into `draft_S2_framework.md`'s clustering
sentence per Ruling 1, and if the honest interval turns out materially wider than method A, re-read
the main-text separability claims (the ones that currently rest on method A alone) against it before
anything is quoted, per Ruling 5.
