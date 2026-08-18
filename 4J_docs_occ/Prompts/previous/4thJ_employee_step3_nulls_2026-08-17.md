# Employee task — D-S3-4 / D-S3-5: is imputation of the null `LOC` and null `COP` episodes defensible?

**Role: employee.** You **measure**. You do not impute, you do not edit `harmonised.parquet`, you do
not write an encoder, and 🔴 **you do not decide D-S3-4 or D-S3-5.** You produce the table that lets
the author decide, and you report it whichever way it comes out.

**Context.** The author ruled on 2026-08-17: *assess whether imputation from neighbouring episodes is
possible; if it is not, fall back to an explicit `unknown` LOC class and an explicit out-of-range
"not reported" COP code.* Both fallbacks are already approved. **Your job is only to establish
whether the imputation branch is even available.** See `Step3_docs/4thJ_03_serialisation.md`, entry
"2026-08-17 (evening)", and `Step3_docs/impl/2026-08-17_na-fix-rerun.md` for the measured extents.

**What is already known, and must not be re-derived as if new:**

* `loc_class` is null on **24,800 rows**, inside **8,873 of 73,254 diaries**.
* All six `cop_*` flags are null **together** on **68,464 rows**, inside **9,298 diaries**, and
  **only in the UK** — zero rows in ES, zero in IT.
* Source table: `/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet`,
  2,024,068 rows, 51 columns.

Confirm these four numbers as your first output. 🔴 **If any of them disagrees with what you measure,
stop and report the disagreement — do not proceed on your own number and do not proceed on mine.**

---

## 🔴 CLUSTER RULES

* **`sbatch` only.** Never a blocking `srun`, never bare `python`/`python3` on the login node, not
  even a one-liner. Partition `ps`, `--mem=16G`, `-t 7-00:00:00`, CPU only.
* 🔴 **Submit through a shipped `.sh` launcher, never a hand-rolled `sbatch --wrap`.** Copy
  `/speed-scratch/o_iseri/4thJ_act2_setup_and_run.sh` as your template and change the job name,
  `--output` and the script it calls. The venv is `ENVDIR=/speed-scratch/o_iseri/envs/4j_tok` — it
  carries pandas, pyarrow and transformers. A previous re-run of this exact family of jobs died in
  two seconds against `envs/step4`, which has no transformers.
* tcsh login shell: no `2>&1` in ssh commands, no bash `while ... done` loops, **one `sacct` call,
  not a poll loop**.
* 🔴 **`pd.NA`, not `NaN`.** The `cop_*` flags are pandas nullable dtype and `loc_class` may be too.
  A null test written as `isinstance(x, float) and pd.isna(x)` **misses `pd.NA` and crashes**. Use
  `pd.isna(x)` alone, and test it **before** any `==` comparison — `pd.NA == ""` returns `pd.NA`,
  not `False`, and taking its truth value raises. This defect has already cost four failed jobs on
  this exact data.

## 🔴 NO PARKING — you never wait for a job

Submit with `sbatch`, write the JobID into your implementation doc, and **end your turn** saying
"job N submitted, state written to `<path>`". **No background polls, no sleeps, no no-op command to
hold the turn open, no "waiting for the notification".** The manager watches the queue and spawns a
fresh agent to collect the result. Every wake re-sends your whole transcript and produces nothing.

Your state goes to disk **as it happens**, in `Step3_docs/impl/2026-08-17_null-imputation.md` —
create it before any job:

```
# Null LOC / COP imputation feasibility — implementation state
Task doc:   4J_docs_occ/Prompts/4thJ_employee_step3_nulls_2026-08-17.md
Status:     IN PROGRESS | BLOCKED | DONE
## Ledger        <- one line per job: JobID · what · state · exit · output path (append-only, failures kept)
## Verified      <- numbers actually read, and where from
## Decisions     <- what this task doc did not decide, and what you assumed
## Next          <- the exact next action, written so a cold agent can start there
## WHAT I DID NOT VERIFY
```

Never read a multi-MB file into context — `wc -l`, `grep -n`, `tail -c`, `head`. Past roughly 150k
tokens: stop, write state, say a handoff is needed.

---

## WHAT YOU MEASURE

Write `tools/4thJ_null_structure.py`, run it once on Speed, and have it **print** the tables below.
Episodes are ordered within a diary by `episode_index` (or whatever the table's actual ordering
column is — read it, do not assume the name). A "diary" is the full key: country + household +
person + diary day. 🔴 **Lowercase `country` before any crosswalk join (D-S2-16), and fail loudly on
a zero-match join** — `harmonised.parquet` holds `ES`/`UK`/`IT`, every crosswalk holds `es`/`uk`/`it`.

### Part 1 — extent, confirmed

Per country: total rows, total diaries, null-`loc_class` rows and diaries, null-`cop_*` rows and
diaries, and the count of rows null in **both**. Check and print explicitly whether the six `cop_*`
flags are **always null together** — report the number of rows where some but not all six are null.
🔴 **If that number is not zero, say so.** The whole reading of D-S3-5 rests on it being zero.

### Part 2 — run structure (this is the part that decides)

For each of `loc_class` and `cop_*`, classify **every maximal run of consecutive null episodes**
inside a diary into exactly one bucket, and report counts of runs **and** of episodes, per country:

| bucket | meaning |
|---|---|
| `whole_diary` | every episode in the diary is null — no neighbour exists anywhere |
| `head` | run starts at the diary's first episode — no known predecessor |
| `tail` | run ends at the diary's last episode — no known successor |
| `interior_agree` | known episode on both sides, and the two carry the **same** value |
| `interior_disagree` | known episode on both sides, values **differ** |

Cross the interior buckets by **run length** (1, 2, 3, 4-6, 7+) and print the table. Also print, for
the null episodes, the **duration** distribution (median, p90, max minutes) per bucket — a 10-minute
gap between two identical neighbours is a different object from a 6-hour block.

For `cop_*`, "same value" means the full 6-bit pattern is identical on both sides.

### Part 3 — is the missingness structured?

Print null prevalence broken down by `act` (top 15 activity codes by null count, with each code's
share of all null rows **and** its null rate within that code), and by `strat_day_type` and
`strat_age_band`. 🔴 **If nulls concentrate on one activity — travel, for instance — then the
location is recoverable from the activity, not from the neighbours, and that is a different and
better mechanism than imputation. Say so if you see it; do not implement it.**

### Part 4 — the coverage number

Print one line per field:

```
<field>: episodes imputable under the strict rule = N (X.XX% of all null episodes); residual = M
```

where **the strict rule is `interior_agree` with run length ≤ 2**, pre-registered here before the
measurement, not chosen after seeing it.

---

## 🔴 THE PRE-REGISTERED DECISION RULE

Written down **before** the numbers exist. Manager's rule; the author confirms or overrides it.

> **Imputation is adopted only if it covers ≥ 99 % of that field's null episodes under the strict
> rule. Otherwise the explicit class is used alone, for 100 % of them.**

**The reasoning, which matters more than the threshold:** any residual still needs the `unknown`
class, so a partial imputation ships **two** mechanisms instead of one and the model must learn both
— while the `unknown` class alone ships one mechanism and never invents a value that was not
observed. Imputation is only worth its complexity if it removes the fallback entirely. **A hybrid is
the worst of the three outcomes**, and 99 % is not a hedge toward it.

🔴 **You do not apply this rule and you do not announce a verdict.** Print the coverage number
beside the threshold and stop. If coverage lands near 99 % either way, say that plainly rather than
rounding it to a side.

## 🔴 WHAT YOU DO NOT DO

* Do not write `harmonised.parquet` or any file under `outputs_step2/`. **Read only.**
* Do not impute anything, not even to show what it would look like.
* Do not touch `4thJ_cop_measure.py`, `4thJ_cop_reverify.py` or `4thJ_act2_measure.py` — jobs 1255223
  and 1255237 are collected and their scripts are the record of what was run.
* Do not move a threshold, and do not soften the strict rule because coverage came out low. **Low
  coverage is the answer to the question, not a problem with the question.**

## DELIVERABLE

1. `tools/4thJ_null_structure.py`.
2. The job's `.out` on Speed, path recorded in your ledger.
3. `Step3_docs/4thJ_03b_null_structure.md` — the tables above, transcribed from the job output, with
   a short factual reading of each and a final section **WHAT I DID NOT VERIFY**. 🔴 **No
   recommendation, no verdict on D-S3-4 or D-S3-5.** The author decides from this document.

Report anything this task doc did not decide for you, and say plainly what you assumed.
