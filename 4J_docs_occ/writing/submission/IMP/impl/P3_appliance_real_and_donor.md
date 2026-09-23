# P3 — Appliance timing from real and raked-donor diaries (2026-09-23)

**Status:** step 1 DONE (runs do not exist); step 2 design written below, compute approved by the
author (D3, 2026-09-23). Execution delegated; results are appended at the end of this file.

## Step 1 result — the runs do not exist (checked 2026-09-23)

- `tools/4thJ_step9_trigger.py:529-531` hard-codes the diary source to
  `Step7_docs/outputs_step7/generated_<leg>_<fold>_constrained.jsonl`. No argument picks another source.
- `Step9_docs/4thJ_09_enduseLoads.md:90` states the step consumes Step 7's generated diaries; the real
  corpus is used only to calibrate the trigger probability (`:113-117`).
- Households themselves are real: `build_dwellings` draws them from `Step3_docs/outputs_step3/4J_step3_corpus.jsonl`
  (`tools/4thJ_step9_trigger.py:534-536`); only the diaries given to their members are generated.
- The raked-donor population is never written to disk: `tools/4thJ_step6_g61_rake_folds.py` and
  `tools/4thJ_step6_rakeddonor.py` compute the raked weights on the fly (target = `population_<c>.csv`).

## Step 2 design (manager-owned; do not change without asking)

Only the diary source changes. Households, calendar, seed rule, trigger probabilities, appliance
parameters and the aggregation that gives Table 7 stay exactly as they are.

1. **Additive flag.** Add `--pool PATH` to `tools/4thJ_step9_trigger.py`; default = the current generated
   path, so a run without the flag is byte-identical to today. Add `--out` use so nothing overwrites
   `Step9_docs/outputs_step9/`. New outputs go to `Step9_docs/outputs_step9_P3/<source>/<fold>/`.
2. **Pool builder** `tools/4thJ_p3_build_pools.py` writes, per held-out country c, two pools in the exact
   record format `s7.load_pool` reads (read that function first; copy only the fields it uses):
   - `real_<c>.jsonl`: country c's own real diaries from the Step 3 corpus.
   - `raked_<c>.jsonl`: the two other countries' real diaries (never country c), raked by the SAME code
     and the SAME target as `G6.1` (`4thJ_step6_g61_rake_folds.py`, target `population_<c>.csv`), then
     drawn with probability proportional to the raked weight, fixed seed, labelled as country c.
   - Pool size = the generated pool's size for c. Real pool drawn with the survey diary weight used by
     `G6.1` for the real side (confirm the weight name in `4thJ_step6_g61_score.py`; do not guess).
   - Every stratum the household draw asks for must exist in each pool; if one is missing, record the
     count and the backoff the Step 7 loader already applies. Do not invent a new backoff.
3. **Controls, before any real run is trusted (must be seen failing/passing):**
   - C-a reproduction: `--pool` pointed at the generated file reproduces the existing
     `Step9_docs/outputs_step9/enduse_by_dwelling_<c>.csv` byte for byte (hash) for all three folds, and
     Table 7's Spain peak (14:00, 518 W) exactly.
   - C-b non-identity: the real and raked runs give output hashes different from the generated run
     (if identical, the flag is not being read).
   - C-c no self-donor: `raked_<c>.jsonl` contains zero diaries whose source country is c.
4. **Runs:** 3 folds x 3 sources (generated control, real, raked) = 9 runs. Speed only, sbatch only,
   `-p ps -t 7-00:00:00 --nice=10000`, small CPU request that keeps the combined 4J+1J+3J usage within 32
   (check `squeue -u o_iseri` first), never `histnu`. Login node: no python.
5. **Result table:** per country, peak hour and peak power (and the same for the evening peak if Table 7
   reports two), rows real / raked donor / generated, each value read from an output file by path.

## Decision rule for the paper (fixed now, before the numbers)

- Real diaries give the same peak-hour ORDER across the three countries as the generated diaries do in
  Table 7 (read the order from Table 7, do not assume it) -> §6.5 keeps the six-hour-spread claim and adds "and real diaries give the same order".
- Otherwise -> the claim narrows: the paper reports the real-diary peaks as the result and says the
  generated diaries do not carry the timing. Highlights and Conclusion follow.

## Execution log (append below; newest last)
