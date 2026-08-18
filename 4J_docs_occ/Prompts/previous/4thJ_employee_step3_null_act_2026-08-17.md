# Employee task — D-S3-9: null `act`. Is it a source fact or a Step 2 crosswalk miss?

**Role: employee.** You **measure**. You do not encode, you do not impute, you do not edit
`harmonised.parquet`, you do not touch `encoder.py` or `decoder.py`, and 🔴 **you do not decide
D-S3-9.** You produce the table that lets the author decide, and you report it whichever way it comes
out.

---

## WHAT HAPPENED

Speed job **1255349** built the Step 3 encoder and decoder and refused to emit the corpus:

```
diaries OK: 68006, diaries FAILED: 5248
  ('es', '00005', '00005_01', '6'): EncodeError: act is null
FATAL: round-trip is NOT 100% (5248/73254 diaries failed) -- corpus NOT emitted.
```

**The encoder was right to stop.** `act` is the primary activity — **the thing the model generates**.
Every null `loc_class` and null `cop_*` episode found so far was a *conditioning* field; this is the
target. Loader accounting in that same run was clean: 2,024,068 rows and 73,254 diaries read, **0
dropped**, matching the pre-registered totals per country exactly. So the nulls are in the table, not
in the reading of it.

Output: `/speed-scratch/o_iseri/4J_step3_build_1255349.out`. Every failure printed in the first 100 is
**Spain** — that is a sample, not a finding, and establishing the real per-country split is your Part 1.

## 🔴 THE QUESTION THAT DECIDES THIS, AND IT IS NOT "HOW MANY"

Four earlier null fields were treated as facts about the source. **This one may not be.** `act` is a
harmonised target code produced by a Step 2 crosswalk from a raw source code. There are two completely
different worlds:

* **World A — the respondent reported nothing.** `act_raw` is itself null/blank. The episode genuinely
  has no activity, and Step 3 must represent that somehow. A Step 3 decision.
* **World B — the respondent reported something and the crosswalk could not map it.** `act_raw` carries
  a value, `act` is null. 🔴 **That is a Step 2 coverage hole, and the repair belongs in Step 2, not
  here.** Encoding it as an `unknown` activity in Step 3 would bury a mapping defect inside the model's
  target vocabulary, permanently, and every downstream number would be computed on it.

**Your central deliverable is the split between A and B, per country, in counts.** Everything else in
this task is context for it.

---

## 🔴 CLUSTER RULES

* **`sbatch` only.** Never a blocking `srun`, never bare `python`/`python3` on the login node, not even
  a one-liner. Partition `ps`, `--mem=16G`, `-t 7-00:00:00`, CPU only.
* 🔴 **Submit through a shipped `.sh` launcher, never a hand-rolled `sbatch --wrap`.** Copy
  `/speed-scratch/o_iseri/4thJ_null_structure_setup_and_run.sh` and change the job name, the
  `--output` path and the script it calls. **The venv is `ENVDIR=/speed-scratch/o_iseri/envs/4j_tok`.**
  `envs/step4` has no transformers and two jobs in this family died against it in two seconds.
* tcsh login shell: no `2>&1` in ssh commands, no bash `while ... done` loops, **one `sacct` call, not
  a poll loop**.
* 🔴 **`pd.NA`, not `NaN`.** `act`, `act2`, `loc_class` and the six `cop_*` flags are pandas nullable
  dtypes. A null test written as `isinstance(x, float) and pd.isna(x)` **misses `pd.NA` and crashes**;
  `pd.NA == ""` returns `pd.NA`, whose truth value raises. Use `pd.isna(x)` **alone, before any `==`**.
  Four failed jobs on this exact data, at two sites.

## 🔴 NO PARKING — you never wait for a job

Submit with `sbatch`, write the JobID into your implementation doc, and **end your turn** saying "job N
submitted, state written to `<path>`". **No background polls, no sleeps, no no-op command to hold the
turn open, no "waiting for the notification".** The manager watches the queue and spawns a fresh agent
to collect. Every wake re-sends your whole transcript and produces nothing.

State goes to disk **as it happens**, in `Step3_docs/impl/2026-08-17_null-act.md` — create it before
any job:

```
# Null `act` — implementation state
Task doc:   4J_docs_occ/Prompts/4thJ_employee_step3_null_act_2026-08-17.md
Status:     IN PROGRESS | BLOCKED | DONE
## Ledger        <- one line per job: JobID · what · state · exit · output path (append-only, failures kept)
## Verified      <- numbers actually read, and where from
## Decisions     <- what this task doc did not decide, and what you assumed
## Next          <- the exact next action, written so a cold agent can start there
## WHAT I DID NOT VERIFY
```

Never read a multi-MB file into context — `wc -l`, `grep -n`, `head`, `tail`, `sed -n 'A,Bp'`. Never
read `harmonised.parquet` into your own context. Past roughly 150k tokens: stop, write state, say a
handoff is needed.

---

## WHAT YOU MEASURE

Write `tools/4thJ_null_act_structure.py`, run it once on Speed, and have it **print** the following.
Diary key = `country, hid, pid, diary_day`; ordering column `episode_index`; duration `duration_min`.
🔴 **Lowercase `country` before any crosswalk join** (D-S2-16) — the parquet holds `ES`/`UK`/`IT`, every
crosswalk holds `es`/`uk`/`it` — **and FAIL loudly on a zero-match join**, never an empty result set.

### Part 1 — extent

Per country: total rows and diaries; rows and diaries with a null `act`; and the **share of that
country's episodes**. Confirm the totals against **446,547 / 1,010,140 / 567,381** rows and
**19,140 / 38,260 / 15,854** diaries. 🔴 **If any disagrees, stop and report the disagreement — do not
proceed on your own number and do not proceed on mine.** Confirm the failing-diary count reconciles to
**5,248**; if it does not, say so and say which is right.

### Part 2 — 🔴 WORLD A OR WORLD B. This is the part that decides

For every null-`act` row, read **`act_raw`** and split into exactly three buckets, **per country**:

| bucket | meaning |
|---|---|
| `raw_null` | `act_raw` is itself null / blank / empty — **World A**, the source reported nothing |
| `raw_present_unmapped` | `act_raw` carries a value but `act` is null — **World B, a crosswalk miss** |
| `raw_column_absent` | the country ships no `act_raw` at all — report it and say so |

For `raw_present_unmapped`, print the **top 30 distinct `act_raw` values by frequency, per country**,
with counts, and cross them against `crosswalk_activity.csv`: for each, say whether the value is
**absent from the crosswalk entirely** or **present but mapping to a null target**. Those are two
different defects and the repair differs.

🔴 **If `raw_present_unmapped` is non-zero, that is the headline of your report and it must be the
first thing stated.** It means Step 2 shipped a coverage hole and a Step 3 encoding decision would bury
it. Report it plainly; do not soften it, and do not propose the repair.

### Part 3 — structure, only if World A is non-empty

For the `raw_null` rows only, the same run analysis already used for `loc_class` and `cop_*` in
`Step3_docs/4thJ_03b_null_structure.md` — classify every maximal run of consecutive null-`act` episodes
inside a diary as `whole_diary` / `head` / `tail` / `interior_agree` / `interior_disagree`, crossed by
run length (1, 2, 3, 4-6, 7+), per country, counting **runs and episodes**. Print the null episodes'
**duration** distribution (median, p90, max minutes) per bucket.

Also print, per country: **total null-`act` minutes as a share of that country's total diary minutes**,
and the distribution of **null-`act` minutes per affected diary** (median, p90, max). 🔴 A diary losing
20 minutes and a diary losing nine hours are different objects, and `G3.2` requires `sum(DUR) == 1440`
either way, so **whatever is decided cannot drop an episode without also dropping its minutes.**

### Part 4 — overlap with the four fields already decided

Per country, the count of rows where `act` is null **and** `loc_class` is null; `act` null **and**
`cop_*` null; `act` null **and** `act2` present. And the number of the 5,248 failing diaries that are
**also** in the 8,873 null-`loc_class` diaries or the 9,298 null-`cop_*` diaries.

### Part 5 — is `000` free?

🔴 **Do not use it, do not encode with it. Check only.** Report whether the 3-digit string `000` — and
each of `998`, `999` — appears as a **legal target code** in `crosswalk_activity.csv`, and whether any
appears as a value in the `act` column. **A sentinel that is secretly a valid code tests nothing**:
Step 1 pre-registered `999` as an out-of-list perturbation for Spain and `999` turned out to be a real
INE code, so the perturbation tested nothing. The author will need to know which 3-digit strings are
actually free before choosing anything.

---

## 🔴 THE PRE-REGISTERED DECISION RULE

Written **before** the numbers exist. Manager's rule; the author confirms or overrides it.

> **If `raw_present_unmapped` is non-zero for any country, D-S3-9 is not a Step 3 decision at all —
> Step 2 reopens and the crosswalk is completed. Step 3 does not encode around a mapping hole.**
>
> **If it is zero — every null `act` is a genuine `raw_null` — then D-S3-9 is a Step 3 decision between
> an explicit target code and dropping the affected diaries, and the author takes it.**

**The reasoning, which matters more than the rule:** `act` is the **generation target**. An explicit
`unknown` activity code teaches the model to emit "unknown" as a legitimate output, and every schedule
it generates can then contain hours the model itself cannot name — which is a different and worse
object than an unknown *location*, because the whole product of this pipeline is a sequence of
activities. Dropping 5,248 diaries costs 7.2 % of the corpus and changes the population, which must be
declared, not absorbed. **Both are real costs and neither is obviously smaller**, which is exactly why
the author decides and not you.

🔴 **You do not apply this rule and you do not announce a verdict.** Print the numbers beside it and
stop. If a count lands near a boundary, say that plainly rather than rounding it to a side.

## 🔴 WHAT YOU DO NOT DO

* Do not write `harmonised.parquet` or anything under `outputs_step2/`. **Read only.**
* Do not modify `tools/encoder.py`, `tools/decoder.py` or `tools/4thJ_step3_build.py`. Job 1255349's
  refusal to emit a partial corpus is **correct behaviour** and is the record of what was found.
* Do not impute, and do not encode anything with a sentinel — not even to show what it would look like.
* Do not re-run the Step 3 build.
* Do not move a threshold, and do not soften a finding because it reopens an earlier step. **A
  crosswalk hole discovered late is still a crosswalk hole.**

## DELIVERABLE

1. `tools/4thJ_null_act_structure.py`.
2. The job's `.out` on Speed, path recorded in your ledger.
3. `Step3_docs/4thJ_03c_null_act.md` — the tables above, transcribed from the job output, each with a
   short factual reading, and a final section **WHAT I DID NOT VERIFY**. 🔴 **No recommendation and no
   verdict on D-S3-9.** Part 2's World A / World B split is the first thing in the document.
4. Append one Ledger line to `Step3_docs/impl/2026-08-17_step3-build.md` recording job **1255349** as
   **FAILED, exit 1:0, 00:05:50**, output `/speed-scratch/o_iseri/4J_step3_build_1255349.out`, cause
   "null `act` on 5,248 diaries — corpus deliberately not emitted". 🔴 **Append only. Do not edit or
   remove any existing line, and do not change anything else in that file.**

Report anything this task doc did not decide for you, and say plainly what you assumed.
