# T13 — WP1 stage B, part 1: how the 2022 stock picks its diaries (reading) — implementation state

Task doc:   this file (brief below). Spec: `2026-09-15_WP1_step2_retargeting_spec.md` §5b, §6. Plan log (m).
Status:     DONE

## Why
Author decision (2026-09-15): rebuild the 2022 stock from **2022-cycle diaries only**. Today 77.7 % of
stock persons carry a 2005/2010/2015 diary (T12). Before any build, the manager needs the exact place
where donor diaries are chosen and what a 2022-only donor pool would do to matching.

## Brief (employee, Sonnet, READING ONLY)
Rules: no edits to any existing file except this doc. No python locally on big files, no jobs, no Speed
login-node compute. `wc -l`, `grep -n`, `head` only on multi-MB files. Cite every answer as `file:line`.
Write each answer into Verified as you go. End your turn when done.

Q1. **Chain.** Locate `05_census_linkage.py` (not in `2J_docs_occ_nTemp/` root: search the repo, incl.
    `speed_cluster/`, `eSim_occ_utils/`). List scripts in order from `outputs_step4/augmented_diaries.csv`
    to `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_excl.csv`, including
    the aggregation/exclusion script T11 did not open. Give input, output, and the canonical command line
    for each (from the step docs `05_censusLinkageGSS.md`, `07_bemIntegrationGSS.md`).
Q2. **Donor choice.** In the linkage script, where is the donor diary pool built and filtered? Which keys
    and tiers are used (region tier, age, sex, work, household size, dwelling, day type...)? Is
    `CYCLE_YEAR` used anywhere? Is `IS_SYNTHETIC` used? Is sampling random, and what seed?
Q3. **Filter point.** Name the single narrowest place where restricting donors to `CYCLE_YEAR == 2022`
    could be done **from a new wrapper script** (e.g. filtering the input diaries file before the call,
    or a function argument), without editing the pipeline source. Say what else downstream assumes all
    four cycles (e.g. co-presence columns, `05_postlink_rake.py` raking synthetic to real in the same file).
Q4. **Pool size.** From step docs/logs (not by loading big files): number of diaries by cycle and by
    `IS_SYNTHETIC` in `augmented_diaries.csv`; logged linkage tier shares / match rates for the current
    build (the 2026-07-09 relink, `improvement-planning/2J_improvements_master_log.md:48-56`). If counts by
    cycle are not logged, say so; the manager will send a job.
Q5. **Runtime.** Logged wall time and memory of the linkage, post-link rake and aggregation steps, and
    where they ran (local or Speed).
Q6. **Outputs hash.** Current size (bytes, `ls -l`) of `21CEN22GSS_aug_Full_Schedules.csv`,
    `21CEN22GSS_aug_Matched_Keys.csv`, `21CEN22GSS_aug_Full_Aggregated_excl.csv` so the build can prove it
    did not overwrite them.

## Ledger
(no jobs)

## Verified

### Q1. Chain

`05_census_linkage.py` is at
`eSim/eSim_occ_utils/25CEN22GSS_classification/05_census_linkage.py` (not in `2J_docs_occ_nTemp/`,
confirmed by repo-wide search). Full chain, `outputs_step4/augmented_diaries.csv` →
`21CEN22GSS_aug_Full_Aggregated_excl.csv`:

1. **`05_census_linkage.py --full`** (`05_censusLinkageGSS.md:433-434`). Input:
   `2J_docs_occ_nTemp/outputs_step4/augmented_diaries.csv` (192,183 rows; path constant
   `05_census_linkage.py:33`) + `0_Occupancy/Outputs_21CEN22GSS/alignment/Aligned_Census_2022.csv`
   (286,540 agents, deduped to 286,537, `05_census_linkage.py:34-36,370-376`). Output:
   `0_Occupancy/Outputs_21CEN22GSS/aug_pipeline/21CEN22GSS_aug_Full_Schedules.csv` +
   `21CEN22GSS_aug_Matched_Keys.csv` (`05_census_linkage.py:389-392`). Command:
   `py 05_census_linkage.py --full` (optionally `--region-tier`, `05_census_linkage.py:915-925`).
2. **`05_census_linkage.py --aggregate`** (Sub-step 5E, `05_censusLinkageGSS.md:436-437`, argparse
   flag `05_census_linkage.py:909`, dispatched to `run_aggregate()` at `:415,933`). Input/output:
   reads+writes in the same `aug_pipeline/` dir
   (`21CEN22GSS_aug_Full_Aggregated.csv` — HH aggregation via slot-native adapter, `05_censusLinkageGSS.md:611-626`).
   Command: `py 05_census_linkage.py --aggregate`.
3. **`05_postlink_rake.py`** (Phase 8B-5b; NOT in the 5A-5G sub-step list, invoked separately after
   linkage). Reads and rewrites `21CEN22GSS_aug_Full_Schedules.csv` **in place**
   (`05_postlink_rake.py:31-35`, `_FULL_SCHED_PATH`), raking `IS_SYNTHETIC==1` `hom30`/`act30`/`Spouse30`
   to the `IS_SYNTHETIC==0` rows in the same file (`05_postlink_rake.py:4-6`). Canonical command
   (joint calibration, Task B, 2026-07-09): `py 05_postlink_rake.py --joint`
   (flag confirmed by `07_bemIntegrationGSS.md:47`: "`act30` joint-raked ... `05_postlink_rake.py --joint`").
4. **The aggregation/exclusion script T11 did not open is `05_census_linkage.py` itself**,
   `run_exclusion()` (Sub-step 5H, argparse flag `--exclusion`, `05_census_linkage.py:639-697,915,939`).
   It reads `21CEN22GSS_aug_Full_Schedules.csv` (post-rake) + the aggregated file, drops implausible
   HHs (`fail_ppids`), and writes three parallel `_excl` outputs, including
   `21CEN22GSS_aug_Full_Aggregated_excl.csv` (`05_census_linkage.py:674-675,684-685`) — 285,367 rows
   at the current build (`07_bemIntegrationGSS.md:29`). Command: `py 05_census_linkage.py --exclusion`.
5. (Downstream, outside Q1's requested end-point but confirming closure) `07_aug_to_bem.py --year 2022`
   reads `21CEN22GSS_aug_Full_Aggregated_excl.csv` directly (`07_aug_to_bem.py:204`,
   `07_bemIntegrationGSS.md:18,28-29`) — this is where the chain in the task brief ends.

Execution order per the spec: 5A → **5B (`--full`)** → 5C(smoke, skipped here) → 5D(full, same as
step 1) → **5E (`--aggregate`)** → [`05_postlink_rake.py` — Task B, run between linkage and
exclusion per the 2026-07-09 remediation log: "Full downstream rebuild run
(`--aggregate`→`--bem`→`--exclusion`→BEM 2022/2030)", `improvement-planning/2J_improvements_master_log.md:56`]
→ **5H (`--exclusion`)**. Note the master-log rebuild order cited puts `--aggregate` before the rake
and `--exclusion` after; `05_postlink_rake.py` operates on `Full_Schedules.csv` (pre-aggregation)
so its exact position relative to `--aggregate` does not change its inputs/outputs, only when the
rake's effect becomes visible in the aggregated file.

### Q2. Donor choice

Donor pool is built by `load_augmented_pool()` (`05_census_linkage.py:98-108`): reads
`augmented_diaries.csv` in full, splits only by `DDAY_STRATA` into a weekday pool (`==1`) and a
weekend pool (`in {2,3}`) — **no other filter**. Callers immediately recombine them:
`df_pool = pd.concat([wd_pool, we_pool])` (`05_census_linkage.py:319-320,368-369`), so the donor
pool for both `--smoke` and `--full` is the **entire 192,183-row `augmented_diaries.csv`**, all 4
GSS cycles and both `IS_SYNTHETIC` values mixed together, undifferentiated.

Matching is a 4-tier fallback in `run_slot_match()` (`05_census_linkage.py:75-82,111-213`):
- Tier 1 `1_Perfect`: `AGEGRP, SEX, MARSTH, HHSIZE, LFTAG, PR, CMA` + `DDAY_STRATA` (all 7 keys).
- Tier 2 `2_Core`: `AGEGRP, SEX, LFTAG, PR` (or `REGION` if `--region-tier`) + `DDAY_STRATA`.
- Tier 3 `3_Constraints`: `AGEGRP, SEX` + `DDAY_STRATA`.
- Tier 4 `4_FailSafe`: `DDAY_STRATA` only (random draw from the whole day-type pool).

**`CYCLE_YEAR` is not used anywhere in the matching/filtering logic.** It is only (a) carried
through as a pass-through output column (`05_census_linkage.py:236`, excluded from the
match-key/exclude set at `:93`) and (b) used purely for post-hoc diagnostic reporting — a per-cycle
tier-share crosstab printed after matching (`05_census_linkage.py:304-308`). Grep confirms no other
`CYCLE_YEAR` reference in the file.

**`IS_SYNTHETIC` is likewise not used to filter or weight the donor pool** — it is not a match key,
not in `_POOL_EXCLUDE`, and is carried straight through as an output column
(`05_census_linkage.py:236`). It is only used later, downstream of matching, for diagnostics/reporting
splits (e.g. the Step 5G regression comparison uses the `IS_SYNTHETIC==0` subset as an
apples-to-apples baseline, `05_census_linkage.py:705,732-733`) and by `05_postlink_rake.py` as the
rake target/source split (`05_postlink_rake.py:4-6`) — but never to restrict who a Census agent can
be matched to.

**Sampling is random within the matched tier's key group**, via `np.random.choice(pool_indices)`
(`05_census_linkage.py:184,187,190,193`), one draw per Census agent, **seed 42**
(`np.random.seed(42)` at function entry, `05_census_linkage.py:142`, confirmed by the docstring at
`:121-122`). Day-type (`DDAY_STRATA`) itself is also randomly assigned to each Census agent first
(Census carries no diary-day attribute) by `_assign_dday()` with a 5:1:1 weekday:Sat:Sun probability
split, `seed=42` (`05_census_linkage.py:84-85,272-279,324,377`).

### Q3. Filter point

The **narrowest single filter point, without editing any pipeline source file**, is the module-level
path constant `AUGMENTED_DIARIES` at `05_census_linkage.py:33`. `load_augmented_pool()` is always
called with `str(AUGMENTED_DIARIES)` re-read from that module global at call time inside
`run_linkage_smoke()`/`run_linkage_full()` (`05_census_linkage.py:319,368`), not from a CLI/function
argument. A new wrapper script can do either of:
- **(a) Monkeypatch the global before calling.** `import importlib; m =
  importlib.import_module("...05_census_linkage"); m.AUGMENTED_DIARIES =
  Path("<wrapper-output>/augmented_diaries_2022only.csv"); m.run_linkage_full()` — zero source edits,
  the function body is untouched, only the name it resolves at call time changes.
- **(b) Pre-filter the input file itself** to a new path (`df =
  pd.read_csv(augmented_diaries.csv); df[df.CYCLE_YEAR==2022].to_csv(new_path)`), then use (a) to
  point the constant at it. This is the more auditable option since the filtered CSV is a durable,
  inspectable artifact.

Either way the filter must happen **before** `load_augmented_pool()` is invoked (i.e. before
`--full`/`--smoke`), since nothing downstream in `run_slot_match()`/`expand_slot_schedules()` ever
re-reads `CYCLE_YEAR` to filter — confirmed above in Q2.

**What downstream assumes all four cycles / assumes nothing about cycle composition:**
- `05_postlink_rake.py` rakes `IS_SYNTHETIC==1` rows to the `IS_SYNTHETIC==0` rows **in the same
  file, with no `CYCLE_YEAR` grouping at all** — explicit code comment: "this file has no per-row
  CYCLE_YEAR grouping in its existing hom30 rake either" (`05_postlink_rake.py:433-434`). This means
  restricting the donor pool to 2022 is mechanically safe for the rake step: it will simply rake
  against whatever `IS_SYNTHETIC==0` (2022-only) subset ends up in `Full_Schedules.csv`, which is a
  much smaller observed anchor (2022 has 12,336 observed respondents vs 64,061 pooled across all
  cycles — see Q4) but the code path does not branch or assert on cycle.
- `05_postlink_rake.py` and `05_census_linkage.py`'s `run_exclusion()`/`run_linkage_full()` both hard
  -assert `len(df) == EXPECTED_ROWS` where `EXPECTED_ROWS = 286_537`
  (`05_census_linkage.py:37,529,679-680,715-720,766,896-897,917-920`; same constant in
  `05_postlink_rake.py:37`) — this is the **Census-agent** row count, not the diary-pool count, and
  is unaffected by restricting `augmented_diaries.csv` to 2022, since every Census agent still gets
  exactly one match (Tier 4 FailSafe guarantees a match against the `DDAY_STRATA`-only pool even if
  Tiers 1-3 are starved). What **would** change is the tier distribution (more agents falling to
  Tier 3/4 as the pool shrinks) — this is exactly what spec §5b's acceptance test **N4** is designed
  to catch (`2026-09-15_WP1_step2_retargeting_spec.md:76-77`).
- Co-presence columns (`Spouse30_*`, `colleagues30_*`, etc.) are pooled straight through
  (`05_census_linkage.py:235-249`) and are not cycle-aware either; `colleagues30_*` is
  spec-documented as forced to 0 for all 2005/2010 synthetic diaries
  (`05_censusLinkageGSS.md:146`/Gate 5.2) — restricting to 2022-only removes this asymmetry entirely
  (2022 diaries do carry non-zero `colleagues30`), which is a **behaviour change**, not just a
  smaller sample, and should be flagged to the author as a side-effect of the 2022-only rebuild.

### Q4. Pool size

**By `IS_SYNTHETIC` (whole pool, all cycles), directly logged:**
`04_augmentationGSS_val.md:270` — "Observed rows: 64,061 | Synthetic rows: 128,122" (total 192,183).

**By cycle, observed (`IS_SYNTHETIC==0`) — directly logged**, `writing/submission/tables/Table_02_gss_cycles.md:7-11`
("n valid diaries"): 2005 = 19,221; 2010 = 15,114; 2015 = 17,390; 2022 = 12,336; total 64,061
(matches the observed total above exactly).

**By cycle, synthetic — only 2022 is directly logged**: `outputs_step6/improvement/step6_improvement_notes.md:852`
states the (unfiltered) `CYCLE_YEAR==2022` subset of `augmented_diaries.csv` "mixes 12,336 observed +
24,672" synthetic rows (37,008 total for 2022). **2005/2010/2015 synthetic-row counts by cycle are
NOT directly logged anywhere found.** They can be inferred (not verified) from the same fixed 1
observed : 2 synthetic ratio implied by the 2022 figure and by a separate deviation note
("MARSTH NaN — 183 rows (61 observed / 122 synthetic). Ratio is ~1:2 consistent with IS_SYNTHETIC
amplification", `05_censusLinkageGSS.md:529`), giving inferred synthetic = 2005 38,442 / 2010 30,228
/ 2015 34,780 / 2022 24,672 (sums to 128,122, consistent) — **flagged as inferred, not logged; the
manager should send a job to confirm directly if the 2022-only rebuild needs it.**

**Linkage tier shares / match rates for the current build (2026-07-09 relink,
`improvement-planning/2J_improvements_master_log.md:48-56`):** Tier 1 (`1_Perfect`) 128,778 rows,
byte-identical before/after the relink (44.94% of 286,537). Per-cycle matched share (post-relink):
2005 15.76% (45,164 rows, up from 9.03%/25,863), 2010 29.93% (down from 32.52%), 2015 32.04% (down
from 34.80%), 2022 22.27% (down from 23.66%) — `improvement-planning/2J_improvements_master_log.md:48-54`.
Overall tier distribution at full run: `1_Perfect` 128,778 (44.94%), `2_Core` 61,294 (21.39%),
`3_Constraints` 96,465 (33.67%), `4_FailSafe` 0 (0.00%) — `05_censusLinkageGSS.md:585-589`
(pre-region-tier numbers; with `--region-tier` a `2b_Region` sub-tier of 1,352 rows appears inside
Tier 2, per `outputs_step4/improvement_planning/step4_improvements_implementation.md:283`).

### Q5. Runtime

**No measured (post-hoc, logged) wall-time or memory figures were found** for `05_census_linkage.py`
(any sub-step), `05_postlink_rake.py`, or `run_exclusion()`. Only **pre-run estimates** exist in the
spec doc's planning table (`05_censusLinkageGSS.md:463-471`): 5A audit < 1 min, 5B script-write
1-2 hrs (dev time, not runtime), 5C smoke < 2 min, 5D full run 5-15 min, 5E aggregation 2-5 min, 5F
occToBEM 2-5 min, 5G regression < 2 min. No equivalent estimate/measurement table exists for 5H
(`--exclusion`) or for `05_postlink_rake.py` in the docs read.

**Where they ran — explicitly stated:** "All sub-steps T5-1 through T5-7 run locally (CPU only). No
GPU, no sbatch, no cluster." (`05_censusLinkageGSS.md:460`). This line covers 5A-5G; `05_postlink_rake.py`
and 5H `--exclusion` are not individually named in that sentence but are grouped with the same
local-only Step-5 family in every place they are described (e.g. T11's Q6 finding: "consistent with
it being a lightweight CPU raking script run locally, same class as `05_postlink_rake.py`" —
`impl/2026-09-15_T11_wp1_chain_facts.md:119`, itself flagged there as inferred from absence of a
SLURM job ID, not an explicit statement for that specific script).

### Q6. Outputs hash

Current sizes (`ls -l`, this session):
- `21CEN22GSS_aug_Full_Schedules.csv`: **573,177,990 bytes**, mtime Jul 9 20:44.
- `21CEN22GSS_aug_Matched_Keys.csv`: **10,809,829 bytes**, mtime Aug 13 08:13.
- `21CEN22GSS_aug_Full_Aggregated_excl.csv`: **598,812,455 bytes**, mtime Jul 9 20:47.

(`Full_Aggregated_excl.csv`'s size matches T12's independently-recorded byte count exactly —
`impl/2026-09-15_T12_wp1_stageA_diagnostic.md:75` — cross-check consistent. `Matched_Keys.csv`'s
Aug 13 mtime is later than the Jul 9 Schedules/Aggregated files; not investigated further here —
see WHAT I DID NOT VERIFY.)

## Decisions
- Treated `run_exclusion()` inside `05_census_linkage.py` (`--exclusion` flag) as "the
  aggregation/exclusion script T11 did not open" named in the brief — confirmed by grep (it is the
  only code in the repo that writes `21CEN22GSS_aug_Full_Aggregated_excl.csv`,
  `05_census_linkage.py:675`) and by T11's own note that it never identified this script
  (`impl/2026-09-15_T11_wp1_chain_facts.md:132`).
- For Q1's execution order, took the 2026-07-09 remediation log's stated rebuild order
  ("`--aggregate`→`--bem`→`--exclusion`→BEM 2022/2030", `improvement-planning/2J_improvements_master_log.md:56`)
  as canonical, and placed `05_postlink_rake.py` between linkage and aggregation per the spec's own
  file-dependency statement (it rewrites `Full_Schedules.csv` in place, which `--aggregate` then
  reads) rather than assuming a single universally-fixed order — flagged since no single doc states
  the full 4-step order end-to-end in one place.
- For Q4's non-2022 synthetic-row counts, used the fixed ~1:2 observed:synthetic ratio (evidenced
  directly for 2022 and by the MARSTH-NaN deviation note) as an assumption, not a verified count.

## Next
Employee answers Q1–Q6 delivered above, all with `file:line` citations. Manager can now design the
build (T18) with N0–N4, with the open item that per-cycle synthetic-row counts (Q4) and any measured
runtime (Q5) for `05_postlink_rake.py`/`--exclusion` are not on disk and would need a job if required
before the build.

## WHAT I DID NOT VERIFY
- Did not open `augmented_diaries.csv`, `Aligned_Census_2022.csv`, or any of the three big output
  CSVs to recompute row counts or per-cycle breakdowns directly — all counts above are as logged in
  docs or from `ls -l`, per the reading-only/no-big-file-load rule.
- Did not confirm 2005/2010/2015 synthetic-row counts in `augmented_diaries.csv` directly — inferred
  from a ratio pattern, not logged as an explicit per-cycle table anywhere found (see Q4, Decisions).
- Did not find a measured wall-time or memory figure for `05_postlink_rake.py` or `run_exclusion()`
  (`--exclusion`) specifically — only the general "Step 5 runs locally" statement and the pre-run
  estimate table for 5A-5G (see Q5).
- Did not investigate why `21CEN22GSS_aug_Matched_Keys.csv`'s mtime (Aug 13) is over a month after
  `Full_Schedules.csv`/`Full_Aggregated_excl.csv` (both Jul 9) — could be a later re-write of just
  that file (e.g. the `--region-tier` run noted in `step4_improvements_implementation.md:283`) or
  unrelated; not chased down, out of scope for this reading task.
- Did not verify whether `05_postlink_rake.py --joint` is the exact/only flag combination used in
  the current on-disk `Full_Schedules.csv` (vs. plain `05_postlink_rake.py` with no flag) — inferred
  from `07_bemIntegrationGSS.md:47`'s "joint-raked (calibrated)" description, not from a run log
  showing the literal command invoked on 2026-07-09.
- Did not check `05_census_linkage.py`'s `run_exclusion()` for what "implausible HH" criteria
  (`fail_ppids`) actually are beyond the `hom30` HH-mean < 0.30 floor check visible at
  `05_census_linkage.py:689-690` — full exclusion-rule logic (lines ~639-670) was not read in detail.
