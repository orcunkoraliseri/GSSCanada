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

### 2026-09-23 — manager reconstruction (execution agent stopped: it parked waiting on its own poll and wrote nothing here)

**Built (local, mirrored on Speed at `/speed-scratch/o_iseri/4J_P3_docs_occ/`):**
- `tools/4thJ_step9_trigger.py`: additive `--pool` / `pool_path=None` (diff checked against the backup
  `tools/previous/4thJ_step9_trigger.py.pre_P3_20260923`; default path unchanged; Step 8 identity check
  skipped only for a non-default pool, with a printed note).
- `tools/4thJ_p3_build_pools.py` (205 lines): real and raked pools, 5,200 diaries each per country.
- `tools/4thJ_p3_run_campaign.py` (264 lines): builds pools, 9 runs, controls C-a/C-b/C-c, writes
  `Step9_docs/outputs_step9_P3/P3_results_summary.json` and per-run outputs under
  `Step9_docs/outputs_step9_P3/<source>/<fold>/`.

**Ledger:**
- 1342913 · 4J_P3_step9 · `-p ps`, 1 CPU, 8G, `--nice=10000`, 7-day · RUNNING (checked 2026-09-23) ·
  script `/speed-scratch/o_iseri/4J_P3_docs_occ/4J_P3_step9.sbatch` · log
  `/speed-scratch/o_iseri/4J_P3_docs_occ/P3_step9_1342913.out`.

**Verified from the job log (read by the manager):** py_compile rc 0; corpus 73,254 records; pools
5,200 per country; raking converged (es 3 sweeps, 0.25 pp; uk 5 sweeps, 0.42 pp; it 4 sweeps, 0.24 pp,
all under the 0.5 pp tolerance); C-c no-self-donor PASS for all three. The 9 runs had started.

**Deviations from the design (decided by the agent, recorded here):**
1. Real pool is a UNIFORM draw of the country's diaries, not survey-weighted. The agent's reason (the real
   side of the `G6.1` scorer uses no weight) is wrong: the real side of that scorer is the published table,
   not diaries. Effect is probably small (members draw diaries within their own stratum), but the result
   must say "unweighted real diaries". A weighted sensitivity run is a possible follow-up.
2. C-a peak control scored against the shipped data (Spain 14:00, 502.88 W), not 518 W, because
   Table 7's watt values do not match the shipped data (see finding below). Hour control unchanged.

**Finding (for P9, the number sheet): Table 7's peak powers do not match the data behind them.**
Manuscript Table 7 says Spain 518 W, Italy 395 W, UK 422 W. `Step9_docs/outputs_step9/agg_diurnal.csv`
(and `writing/4thJ_crossStep_analysis.md:108`) give Spain 502.9 W, Italy 403.5 W, UK 416.1 W. Peak hours
(14:00 / 18:00 / 20:00) match. Source of 518/395/422 not found. Fix at rewrite: use the data values.

**Reproducibility note:** `4thJ_p3_build_pools.py` seeds `random.Random` with a tuple
(`("p3real", seed, c)`). On Python before 3.11 a tuple seed is hashed with the per-process string hash, so
the pool draw is NOT reproducible across runs unless PYTHONHASHSEED is fixed (Python 3.11+ refuses tuples).
The pool files and their md5s are saved (es real 8da0d3b2..., raked 689fed6c...; uk real b0057b6d...,
raked 079a944e...; it real 5e5d19a2..., raked 7c1259b4...), so this run's results stay traceable. Before
any rerun, change the seed to a string (for example "p3real|1|es").

**Next:** when 1342913 ends, copy back `P3_step9_1342913.out` and `Step9_docs/outputs_step9_P3/` (summary
JSON + stock series), read C-a/C-b/C-c, fill the result table, apply the decision rule above.

### 2026-09-23 — result (manager; job 1342913 COMPLETED, 1 h 10 min, exit 0; campaign script rc 1 because C-a strict failed)

Outputs copied back to `Step9_docs/outputs_step9_P3/` (summary `P3_results_summary.json`, job log
`P3_step9_1342913.out`, per-run `stock_series_<c>.csv`, pools).

**Controls as printed by the job**
- C-a strict (per-dwelling file byte-identical to the shipped one): uk PASS; es FAIL, it FAIL. Printed OVERALL FAIL.
- C-a peak (Spain 14:00, 502.88 W against the shipped data): PASS.
- C-b non-identity: PASS for all 6 real/raked runs. C-c no self-donor: PASS for all 3 (0 of 5,200).

**Why C-a strict failed (diagnosed by the manager, diff of the two files):** in each failing file exactly
ONE of 100 rows differs, in ONE cell, by 0.001 in the annual total rounded to 3 decimals
(es dwelling 08645 `elec_kwh_per_year` 1740.354 shipped vs 1740.355 new; it dwelling 006415 1129.956 vs
1129.955). `tools/4thJ_step9_trigger.py:1163` rounds an accumulated float sum; the shipped files were
made on Windows (2026-08-25), the new ones on Linux (Speed), so the last bit of the sum differs and flips a
half-way rounding. No other cell differs.
**Additive check, defined AFTER seeing the failure (labelled as such):** the stock series that Table 7 and
every peak below are computed from (`stock_series_<c>.csv`) is byte-identical to the shipped file for all
three folds (md5 es c7023802..., uk af838972..., it 78b03a5c...). The manager re-derived all nine hourly
profiles from these files (mean over the year at each hour, divided by 100 dwellings) and got the job's
numbers exactly. Verdict: reproduction of the reported quantity HOLDS; strict C-a stays recorded as FAIL
with this cause. For a future rerun: compare the per-dwelling file with a 0.001 tolerance, or run on the
same platform.

**Result table** (peak hour of the stock-mean electricity profile, W per dwelling; 100 dwellings, one year;
source `Step9_docs/outputs_step9_P3/<source>/<c>/stock_series_<c>.csv`)

| Country | Generated (Table 7) | Real diaries (unweighted) | Raked donor diaries |
|---|---|---|---|
| Spain | 14:00, 502.9 W (2nd: 19:00, 436.5) | 21:00, 421.5 W (2nd: 13:00, 405.9) | 19:00, 408.5 W (2nd: 20:00, 402.5) |
| Italy | 18:00, 403.5 W (2nd: 22:00, 332.0) | 19:00, 444.4 W (2nd: 20:00, 411.7) | 21:00, 396.5 W (2nd: 20:00, 379.4) |
| UK | 20:00, 416.1 W (2nd: 13:00, 348.0) | 18:00, 427.2 W (2nd: 19:00, 415.7) | 21:00, 425.9 W (2nd: 20:00, 411.3) |

**Decision rule applied (rule fixed before the runs):** Table 7 order (generated) is Spain 14:00 < Italy
18:00 < UK 20:00. Real diaries give UK 18:00 < Italy 19:00 < Spain 21:00: a different order (Spain goes
from earliest to latest). → **Branch 2: the claim narrows.** The paper reports the real-diary peaks as the
result and says the generated diaries do not carry the timing. The "six-hour spread" claim is withdrawn;
real diaries place the evening peak within 18:00-21:00 (a three-hour spread, Spain latest). Highlights and
Conclusion follow.

**Wording limits for the paper (manager):**
- Say "unweighted real diaries" (deviation 1 above).
- Real and raked peaks are flat-topped: the runner-up hour is within 1-8 % of the peak (UK real 427 vs
  416 W; Spain raked 409 vs 403 W). Report the peak hour with its neighbour, not as a sharp point; do not
  rank countries on a one-hour difference.
- Spain's real profile also has a midday maximum at 13:00 (405.9 W, 4 % below the 21:00 peak): the
  generated 14:00 peak reflects a real midday feature, but at 502.9 W it is 19 % above the real diaries'
  highest hour (421.5 W) and it outranks the evening, which the real diaries do not.
- Raked donor diaries (other two countries, reweighted) put every country's peak at 19:00-21:00, so the
  donor baseline also does not reproduce the real order; neither synthetic source carries country timing.
- 100 dwellings, one year, one seed per run: no interval on the peak hour; say so as a limitation only.

**Status: P3 DONE.** Next: the rewrite (P2-P13 brief) carries this branch.
