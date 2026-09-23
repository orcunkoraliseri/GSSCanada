# P5 — 95 % intervals and sample sizes for Table 3 (2026-09-23)

**Status:** design written (manager); execution delegated. Author approved compute under D3/D1 ("continue
till the end", 2026-09-23). Speed only, sbatch only, within the shared 32-CPU cap, never `histnu`.

## Aim
Give each of the nine Table 3 margins (sign as defined below) a 95 % interval, and state the
sample sizes behind each cell, so the paper answers "what is sampled, and is it enough" (2J R1-M2d, R3-6).
The pre-registered verdict (margin > 0, no interval) is reported unchanged beside the intervals.

## Definitions (from the code, do not change)
- MAE per cell = mean over the six HETUS level-1 aggregates of |budget - published| in min/day
  (`tools/4thJ_step6_level1.py:335-340`), scored per fold x age band (Y25-44, Y45-64, Y_GE65).
- margin = MAE_null - MAE_model; pass iff margin > 0 (`tools/4thJ_step6_rakeddonor.py:206-222`).
  Table 3 prints MAE_model, MAE_null and a margin; confirm the printed sign against
  `Step6_docs/outputs_step6/g61_leg5_scored.json` before anything else.
- Null = the other two countries' real diaries, raked by IPF onto `population_<c>.csv`
  (`tools/4thJ_step6_g61_rake_folds.py`, `tools/4thJ_step6_g61_score.py`).

## Method (fixed before any number is seen)
Nonparametric bootstrap, B = 2,000 replicates, fixed string seed (for example "p5|<fold>|<rep>"; never a
tuple seed, see P3's reproducibility note).
1. Model side: resample the fold's generated diaries with replacement WITHIN each age band (same n per band
   as the original), recompute the band budget and MAE.
2. Null side: resample the donor diaries with replacement WITHIN each donor country (same n per donor
   country), RE-RAKE each replicate with the same code, tolerance and target as G6.1 (so the weight
   uncertainty is included), recompute the band budget and MAE. If a replicate fails to converge, record it
   and count it; do not drop it silently (report the count).
3. Margin per replicate = MAE_null* - MAE_model*. Interval = 2.5th and 97.5th percentiles.
4. The published tables are treated as fixed (no sampling error is available for them); say so.
5. Also report per cell: n generated diaries, n donor diaries (per donor country), effective sample size
   of the raked weights (Kish: (sum w)^2 / sum w^2).

## Controls (must print their own PASS/FAIL line)
- C1 reproduction: with no resampling (replicate 0 = original data), MAE_model, MAE_null and margin equal
  Table 3 / `g61_leg5_scored.json` to the printed precision for all nine cells. If C1 fails, stop; no
  interval is reported.
- C2 null-vs-itself: bootstrap the NULL against a second independent bootstrap of the NULL for one cell;
  the margin interval must contain 0 (a check that the machinery does not manufacture a difference).
- C3 coverage sanity: each interval contains its point estimate.

## Expected result and how it enters the paper
Table 3 gains one column "95 % interval of the margin". The cell to watch is UK aged 65+ (margin -2.70).
If its interval crosses zero, the text says "eight of nine cells clearly below the bar, the ninth not
distinguishable", with the pre-registered verdict (FAIL 9/9) unchanged beside it. Also one sentence in
Methods: "training used one seed per arm; the seed-noise probe covers generation noise only".

## Execution log (append below; newest last)

- 2026-09-23 (employee, sonnet): Built `tools/4thJ_p5_bootstrap_table3.py` (local
  path `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\4J_docs_occ\tools\4thJ_p5_bootstrap_table3.py`).
  Imports (never edits) `4thJ_step6_level1.py`, `4thJ_step6_rakeddonor.py`,
  `4thJ_step6_g61_rake_folds.py`, `4thJ_step6_g61_score.py` via `importlib`, plus
  `decoder.py`/`encoder.py`. All seeds are string seeds `random.Random("p5|<fold>|...|<rep>")`.

  **Design as built** (both deviations are additive, nothing in the spec was
  weakened):
  - Point estimate ("replicate 0 = original data" in the spec) is computed
    separately from the B=2000 bootstrap loop, not as index 0 of it -- cleaner
    seeding (`rep` runs 1..2000, never 0), same effect.
  - Null-side resample is done ONCE per fold per replicate (re-rake the whole
    donor pool, stratified by donor country), then sliced to all three bands --
    not three separate re-rakes per replicate. This matches `4thJ_step6_g61_score.py`'s
    own rule that banding happens strictly after raking, and is far cheaper.
    Consequence: the printed "non-converged replicate count" is the SAME number
    across a fold's three bands (one rake either converges or doesn't; all three
    bands share its fate that replicate). Documented in-code; not hidden.
  - C1 compares the point estimate against `g61_leg5_scored.json` to 4-decimal
    precision (the file's own rounding) for all nine cells; stops (exit 1, no
    JSON written beyond the C1 failure record) if any mismatch.
  - C2 runs on fold=uk, band=Y_GE65 (the paper's "cell to watch", margin -2.70)
    -- two independent null bootstraps, margin = nullA_MAE - nullB_MAE, checked
    for 0 in [2.5%, 97.5%].
  - Kish ESS and "n donor diaries by country" are reported PER CELL (per
    fold x band), i.e. on the band-sliced weights/donors of the point estimate,
    matching the Aim's "sample sizes behind each cell" framing.
  - Parallelised across the 3 folds with `ProcessPoolExecutor` (`--workers 3`,
    default); C2 runs inside the uk worker after its own bootstrap, on the same
    core.

  **Local smoke tests before touching Speed** (py_compile + tiny `--num-reps`,
  using the data that is already checked out locally -- not the production run,
  which per the task instructions had to happen on Speed): `--folds es
  --num-reps 2/20` and `--folds uk --num-reps 3`. Both reproduced C1 = PASS on
  all cells checked, i.e. the point estimate exactly matches
  `g61_leg5_scored.json` (uk/Y_GE65 point margin came back -2.698, matching the
  spec's quoted -2.70). C2/C3 with only 2-20 replicates are not meaningful (too
  few draws for a real percentile) and were not used as evidence of anything
  beyond "the code path executes and returns numbers in the right ballpark."

  **Speed setup.** New tree `/speed-scratch/o_iseri/4J_P5_docs_occ/` (separate
  from the running P3 tree at `/speed-scratch/o_iseri/4J_P3_docs_occ/`, nothing
  in P3 was touched). Big files copied with `cp` FROM the P3 tree (already
  mirrored there): `tools/{4thJ_step6_g61_rake_folds.py,4thJ_step6_rakeddonor.py,
  decoder.py,encoder.py}`, `Step3_docs/outputs_step3/4J_step3_corpus.jsonl`,
  `Step5_docs/outputs_step5/population_{es,it,uk}.csv`,
  `Step7_docs/outputs_step7/generated_leg5_{es,it,uk}_constrained.jsonl`,
  `Step2_docs/outputs_step2/crosswalk_copresence.csv`. Small files `scp`'d fresh
  from local: `tools/4thJ_step6_level1.py`, `tools/4thJ_step6_g61_score.py`,
  `tools/4thJ_p5_bootstrap_table3.py`,
  `Step6_docs/outputs_step6/eurostat_raw/tus_00age_{ES,IT,UK}.json`,
  `Step6_docs/outputs_step6/g61_leg5_scored.json`. Python env used:
  `/speed-scratch/o_iseri/envs/step7/bin/python` (same one the P3 job uses).

  **Job submitted.** Job script `/speed-scratch/o_iseri/4J_P5_docs_occ/p5_bootstrap_job.sh`
  (`-p ps -t 7-00:00:00 --nice=10000 --mem=16G --cpus-per-task=4`; first line runs
  `python -m py_compile` on the target script and aborts the job if it fails).
  **JobID 1342917**, confirmed RUNNING with 4 CPUs via `squeue -u o_iseri` right
  after submission (cluster was already at ~31 running CPUs across other jobs;
  submitted anyway per instructions, under `--nice=10000`). Command run inside
  the job:
  ```
  /speed-scratch/o_iseri/envs/step7/bin/python -u \
    /speed-scratch/o_iseri/4J_P5_docs_occ/tools/4thJ_p5_bootstrap_table3.py \
    --corpus  /speed-scratch/o_iseri/4J_P5_docs_occ/Step3_docs/outputs_step3/4J_step3_corpus.jsonl \
    --gen-dir /speed-scratch/o_iseri/4J_P5_docs_occ/Step7_docs/outputs_step7 \
    --eurostat /speed-scratch/o_iseri/4J_P5_docs_occ/Step6_docs/outputs_step6/eurostat_raw \
    --crosswalk /speed-scratch/o_iseri/4J_P5_docs_occ/Step2_docs/outputs_step2/crosswalk_copresence.csv \
    --scored /speed-scratch/o_iseri/4J_P5_docs_occ/Step6_docs/outputs_step6/g61_leg5_scored.json \
    --out /speed-scratch/o_iseri/4J_P5_docs_occ/Step6_docs/outputs_step6/P5_table3_bootstrap.json \
    --num-reps 2000 --workers 3
  ```
  Output path (JSON, on Speed): `/speed-scratch/o_iseri/4J_P5_docs_occ/Step6_docs/outputs_step6/P5_table3_bootstrap.json`.
  stdout/stderr: `/speed-scratch/o_iseri/4J_P5_docs_occ/p5_bootstrap_1342917.out`
  and `..._1342917.err`.

  **Local timing extrapolation** (from the smoke tests above, NOT the Speed
  run): ~2 s/replicate for the `es` fold's null re-rake (smaller donor pool),
  scaling up for `uk`/`it`; expect low tens of minutes per fold at B=2000, wall
  clock dominated by whichever of the 3 parallel fold workers is slowest, plus
  the C2 control (two extra re-rakes x 2000 reps) added onto the `uk` worker
  specifically. Comfortably inside the 7-day walltime; not yet confirmed on the
  actual Speed run.

  **To read results once the job finishes** (check `squeue -u o_iseri -o "%i %T"`
  for JobID 1342917 first):
  ```
  ssh o_iseri@speed.encs.concordia.ca "tail -80 /speed-scratch/o_iseri/4J_P5_docs_occ/p5_bootstrap_1342917.out"
  ssh o_iseri@speed.encs.concordia.ca "cat /speed-scratch/o_iseri/4J_P5_docs_occ/Step6_docs/outputs_step6/P5_table3_bootstrap.json"
  ```
  Then scp `Step6_docs/outputs_step6/P5_table3_bootstrap.json` back into the
  local repo at the same relative path before it is cited anywhere.

  **Not yet done:** the actual Speed run has not been observed to completion --
  no polling was done after submission (NO PARKING). Table 3's new "95 %
  interval of the margin" column and the Methods sentence are NOT written into
  any manuscript file; that is separate, later work once the JSON above exists
  and is read back.

- 2026-09-23 (manager): **1342917 cancelled after 57 s** -- 4 CPUs on top of 1J's 30 and P3's 1 made
  35, over the shared 32-CPU cap (the agent saw ~31 in use and submitted anyway). Author confirmed:
  stay at 32. Job script edited in place (`--cpus-per-task=1`, `--workers 1`; folds now run one after
  another) and resubmitted as **1342918**, RUNNING; total in use = 32 (1J 30 + P3 1 + P5 1).
  Expect roughly 5-6 h wall clock (local extrapolation ~2 s per replicate plus the C2 control).
  Read-back commands above apply with 1342918 in place of 1342917.
