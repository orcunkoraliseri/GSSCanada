# Null LOC / COP imputation feasibility — implementation state
Task doc:   4J_docs_occ/Prompts/4thJ_employee_step3_nulls_2026-08-17.md
Status:     DONE

## Ledger
- 1255285 · `4thJ_null_structure.py` via shipped `4thJ_null_structure_setup_and_run.sh`
  (copied from `/speed-scratch/o_iseri/4thJ_act2_setup_and_run.sh`, ENVDIR=`envs/4j_tok`) ·
  SUBMITTED · exit pending · output `/speed-scratch/o_iseri/4J_null_structure_1255285.out`
- 1255285 · COMPLETED · exit 0:0 · elapsed 00:01:59 ·
  output `/speed-scratch/o_iseri/4J_null_structure_1255285.out` (279 lines, collected in full)

## Verified
- Task doc's four numbers (24,800 null-`loc_class` rows / 8,873 diaries; 68,464 null-`cop_*`
  rows / 9,298 diaries, UK-only) are **carried over from `Step3_docs/4thJ_03_serialisation.md`
  ("2026-08-17 (evening)") and `Step3_docs/impl/2026-08-17_na-fix-rerun.md`, both read in full
  this task** — not independently re-derived yet. The submitted script (Part 1) re-derives them
  from the live parquet and prints an explicit `CONFIRM-AGAINST-TASK-DOC` line; the collecting
  agent must check that line before trusting anything downstream in the same output.
- Schema, read from `tools/4thJ_act2_measure.py` (a script proven to run cleanly against this
  exact `harmonised.parquet`, job 1255237, COMPLETED exit 0), not re-guessed: diary key =
  `country, hid, pid, diary_day`; ordering column = `episode_index`; duration column =
  `duration_min`; activity column = `act`; the six co-presence flags = `cop_alone, cop_partner,
  cop_children, cop_parent, cop_other_hh, cop_other_persons` (pandas nullable boolean dtype,
  `pd.NA` on missing). Stratum column names (`strat_day_type`, `strat_age_band`) read from
  `Step2_docs/4thJ_02_harmonisation.md:1730-1890`.
- `4thJ_null_structure.py` reads the **ordering column defensively** (checks `episode_index` is
  present, falls back and warns if not, fails loudly if no candidate exists) per the task doc's
  instruction not to assume the name.
- Local compile check: `py -3 -m py_compile 4thJ_null_structure.py` → no errors.
- scp'd to Speed; `ls -la` on Speed confirms `/speed-scratch/o_iseri/4thJ_null_structure.py`
  (19,307 bytes) and `/speed-scratch/o_iseri/4thJ_null_structure_setup_and_run.sh` (1,323 bytes)
  present, timestamp 14:31.
- `CONFIRM-AGAINST-TASK-DOC` line, output line 73: loc_class null rows=24800 (expected 24800),
  loc diaries=8873 (expected 8873); cop null rows=68464 (expected 68464), cop diaries=9298
  (expected 9298) — all four match exactly, re-derived live from the parquet by the job itself.
- Output line 71: "cop_* flags always null together? rows where SOME but NOT ALL six are null: 0"
  — confirmed zero, no partial `cop_*` nulls anywhere.
- Part 4 (output lines ~276-278): `loc_class` imputable under the strict rule (`interior_agree`,
  run length ≤ 2) = 4,280 episodes = 17.26% of all null `loc_class` episodes; residual = 20,520.
  `cop_*` imputable = 19,882 episodes = 29.04% of all null `cop_*` episodes; residual = 48,582.
  Pre-registered threshold = 99% for both fields. Neither field reaches it.
- Full Parts 1-4 transcribed as tables into `Step3_docs/4thJ_03b_null_structure.md`, with a short
  factual reading under each and a closing WHAT I DID NOT VERIFY section. No recommendation, no
  verdict on D-S3-4 / D-S3-5 in that document.

## Decisions
- **Null indicator for the cop_* field's run-finding uses "any of the six flags null" (not
  "all six null"), for robustness** — the task doc's own Part 1 requires checking whether that
  distinction is ever non-zero, and the script computes and prints
  `_cop_some_not_all_null` explicitly. If that count is 0 (expected, per D-S3-5's prior
  finding), "any" and "all" are the same set and this choice makes no difference. If it is
  *not* 0, the script's Part 1 output flags it in red before Part 2's run structure is read —
  not silently assumed away. This is an assumption the task doc did not pin down explicitly and
  the author should be told: it was resolved in favour of the more permissive ("any") null
  definition.
- Task doc's Part 2 says "cross the interior buckets by run length"; the script crosses **all
  five buckets** (`whole_diary`, `head`, `tail`, `interior_agree`, `interior_disagree`) by
  run-length bin, a superset of what was asked, printed unconditionally. No information is
  hidden; nothing beyond the spec is computed or claimed as a finding.
- D-S2-16's lowercase-before-crosswalk-join rule is stated in the task doc's cluster-rules
  section; this script performs **no crosswalk join at all** (Part 3's `act`, `strat_day_type`,
  `strat_age_band` breakdowns use columns already present in `harmonised.parquet` directly), so
  the rule does not apply. The script prints this explicitly rather than staying silent about
  why it wasn't invoked.
- Added an internal sanity check not requested by the task doc: for each field, the sum of
  bucketed null-episode counts must equal the direct `df[null_mask].sum()` count; the script
  exits FATAL if they disagree (a run-finding bug, not a data property). Purely defensive.

## Next
- Measurement is complete and closed. Nothing further to run for this task.
- The author must now apply the pre-registered rule (≥99% coverage under `interior_agree`,
  run length ≤ 2, else the explicit fallback covers 100%) to the Part 4 numbers in
  `Step3_docs/4thJ_03b_null_structure.md` — `loc_class` at 17.26% coverage, `cop_*` at 29.04%
  coverage — and close D-S3-4 and D-S3-5. This task doc and this implementation doc take no
  position on that decision.
- **Nothing is imputed and no encoder is written until the author closes D-S3-4 / D-S3-5.**
  `harmonised.parquet` is untouched; no file under `outputs_step2/` was written by this task.

## WHAT I DID NOT VERIFY
- Did not run the script or read any of its output — job 1255285 was submitted and this task
  ended its turn immediately per the NO-PARKING rule. Nothing below "sanity check OK" or
  "CONFIRM-AGAINST-TASK-DOC" in the script has been exercised against real data.
- Did not independently re-derive the four carried-over numbers before submitting; relied on
  the task doc's citation and the two source docs it named, both read in full.
- Did not verify `strat_day_type` / `strat_age_band` values or cardinality against the live
  parquet — only that the column names exist per `Step2_docs/4thJ_02_harmonisation.md`.
- Did not check whether `episode_index` is contiguous / gap-free within a diary — run-finding
  assumes the sort by `episode_index` alone gives true episode adjacency; if the source table
  ever has episode_index gaps that skip an episode without recording it as a row, "head"/"tail"/
  "interior" classification would be reading diary-row adjacency, not necessarily clock
  adjacency. Not checked in this task.
- Did not test the script against a small synthetic fixture before running it on the full
  2,024,068-row table — first execution is the real 51-column parquet on Speed.
