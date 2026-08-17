# Employee task — Step 2, work item 2.4: build and run the harmonisation runner

**Role: employee.** You execute this one task and report. You do not redesign Step 2, you do not
change a decision, and you do not move a threshold. Where this document and your judgement disagree,
this document wins; where this document is silent, **ask rather than invent** — report the gap in
your Progress Log fragment and stop at that point rather than guessing.

**Governing spec:** `4J_docs_occ/Step2_docs/4thJ_02_harmonisation.md`. Read at minimum D-S2-2 through
**D-S2-13**, work item 2.4, and the `OUTPUTS AND INTERFACES` table. **D-S2-12 is the record contract
and D-S2-13 is the age floor. Both are binding.**

---

## 🔴 CLUSTER RULES — VIOLATING THESE COSTS THE ACCOUNT

* **`sbatch` only.** Never a blocking `srun`. **Never bare `python` or `python3` on the login node,
  not even a one-liner, not even to print a schema.** This has been flagged three times; one more
  costs the account and every queued job with it.
* Every job requests `-t 7-00:00:00`. Partition `ps`. CPU only, no GPU.
* Allowed on the login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, and single-file `tail`/`head`/`grep`/`wc -l`/`cat`. Nothing else.
* The login shell is **tcsh**. A bash `while ... done` poll loop dies on "Illegal variable name".
  Check state with **one** call: `sacct -j <id> --format=JobID,JobName,State,ExitCode,Elapsed`.
* **Never use `2>&1` in an ssh command** — tcsh creates a spurious file named `1`.
* Interpreter on Speed: `/speed-scratch/o_iseri/envs/step4/bin/python`.
* Locally the interpreter is `py`, not `python`.

---

## INPUTS — all of them, and where they are

**Episodes, on Speed, already there and already accepted:**
`/speed-scratch/o_iseri/4J/outputs_step1/run_20260816-2210/episodes_{spain,italy,uk}.parquet`

🔴 **Use that run-stamped directory and no other.** The flat `outputs_step1/*.parquet` are an older
round. Confirm with one `ls` before you submit anything.

**Crosswalks, local, in `4J_docs_occ/Step2_docs/outputs_step2/` — you must `scp` these up:**

| file | columns you will read |
|---|---|
| `crosswalk_activity.csv` | `country, source_code, target_code` |
| `crosswalk_activity_secondary.csv` | `country, source_code, target_code_2d` |
| `crosswalk_location.csv` | `country, source_code, target_class` |
| `crosswalk_copresence.csv` | `country, national_field, national_value, national_value_meaning, shared_flag, bit_position` |
| `outdoor_at_home.csv` | `target_code` |
| `activity_target_list.csv` | `target_code` (used only to assert every emitted `act` exists) |

**Do not read any file beginning with `_` in that directory — those are another employee's scratch.**

---

## TASK 0 — print the schemas before you write a line of transform

Submit one small `sbatch` job that opens all three parquets and writes to a text file: every column
name and dtype, the row count, and for each of `act_raw`, `act2_raw`, `loc_raw` the count of null vs
empty-string vs non-empty. Read that file before continuing.

🔴 **Reconcile it against D-S2-12 and against this document, and report every discrepancy rather than
coding around it.** In particular you must discover, not assume: the national age column names, the
co-presence column names actually emitted per country, and whether `act2_raw`'s three states (M-1)
survive as three distinguishable states in the file.

---

## TASK 1 — write `4J_docs_occ/tools/4thJ_harmonise_step2.py`

One script, all three countries, `--country` selecting one per job. Arguments at minimum:
`--in <run dir> --crosswalks <dir> --out <dir> --country <es|it|uk> --age-floor <int>`.

🔴 **`--age-floor` has NO default.** The runner refuses to start without it. A floor that lives in a
default is a floor nobody can see being changed.

Apply the transform in this order. **Every step that could drop or alter a row must count what it
did, per country, and that count goes in `filter_report.md`.**

### 1. Age filter — D-S2-13, floor **11**

Compile the floor into a per-country expression and **print the expression you compiled**:

* Spain: `EDAD >= 11` (exact integer age).
* UK: `DVAge >= 11` (exact integer age).
* Italy: **there is no exact age in this delivery** (F-IT-2). Age is `claseta2`, eleven bands:
  `01 fino a 2`, `02 3-5`, `03 6-10`, `04 11-14`, `05 15-24`, `06 25-34`, `07 35-44`, `08 45-54`,
  `09 55-64`, `10 65-74`, `11 75 e piu'`. The floor 11 **begins band `04`**, so the exact expression
  is `claseta2 >= "04"`.

🔴 **Derive Italy's band threshold from the floor, do not hardcode `"04"`.** Put the band table in
the script as data — lower and upper bound per band — and select the first band whose **lower bound
is greater than or equal to the floor**. If the floor falls **strictly inside** a band, the runner
**raises `SystemExit` with a message naming the band**; it never silently rounds. That is the whole
content of D-S2-13 and it must be executable, not a comment.

### 2. Rotate to a 04:00 day origin — D-S2-5, cyclic

Native origins: **Spain 06:00, UK 04:00, Italy 04:00.** Read them from
`codebook_facts_<country>.md` in the run directory and **assert** they match those values; if one
does not, stop and report.

`offset = (native_origin_hour - 4) * 60` → Spain **+120**, UK and Italy **0**.
`new_start = (start_min + offset) mod 1440`.

**Splitting.** An episode whose `new_start + duration_min > 1440` becomes **two rows**:
`[new_start, 1440)` and `[0, new_start + duration_min - 1440)`. Both carry `split_at_origin = True`
and the **same `episode_index_step1`**; every other row has `split_at_origin = False`.
`episode_index` is then renumbered `0..n-1` in ascending `new_start` order **within each
`(country, hid, pid, diary_day)`**.

🔴 Only Spain can split, because only Spain has a non-zero offset. **If the UK or Italy produces a
single split, that is a defect — stop and report it, do not absorb it.** Report Spain's split count;
D-S2-5 predicts Spain's Step 2 episode count differs from the `430,754` that `G1.1` pinned, and this
count is the explanation.

### 3. Assert the 10-minute grid — never coerce it

For every episode: `start_min % 10 == 0` and `duration_min % 10 == 0`, and per
`(country, hid, pid, diary_day)` the durations sum to exactly **1440**.

🔴 **These are assertions, not repairs.** A runner that rounds a stray value to the grid destroys the
evidence that the reader was wrong. On violation: stop, report the count and three example keys.

### 4. Activity → `act`, `act_level1`, `act_level2`

Join `crosswalk_activity.csv` on `(country, source_code = act_raw)` → `act = target_code`.
`act_level1 = act[0]`, `act_level2 = act[:2]` — **sliced from the emitted code itself**, never
recomputed from the source code. That is exactly what `G2.16` tests.

`act` is a **3-character zero-padded string**. `011` is not `11`; an integer column would silently
make it so. **A source code with no crosswalk row yields `act = null`** — it is never dropped, never
guessed, and never mapped to a residual. `act_raw` rides along unchanged.

Assert: every non-null `act` exists in `activity_target_list.csv`. Count nulls per country.

### 5. Secondary activity → `act2`, `act2_level1`

Join `crosswalk_activity_secondary.csv` → `act2 = target_code_2d`, a **2-character string**.
`act2_level1 = act2[0]`.

🔴 **The three states of `act2_raw` (M-1) must survive as three distinguishable states**, and this is
the step most likely to flatten them:

* **not recorded by the instrument** → `act2` is `null`;
* **recorded and blank** (respondent reported no secondary activity) → `act2` is the **empty
  string**, never `null`;
* **recorded with a value** → the mapped 2-character code.

A sentinel (the UK's `-9`) is **not** the same state as a blank (Italy's ASCII spaces). Count all
three states per country and put the counts in `filter_report.md`. If your Task 0 schema dump shows
the three states are not distinguishable in the input, **stop and report that** — it is a Step 1
defect and not yours to patch.

### 6. Location → `loc_class`

Join `crosswalk_location.csv` on `(country, source_code = loc_raw)` → `loc_class = target_class`.
Unmapped → `null`. **No numeric range test anywhere** (D-S2-3). `loc_raw` rides along unchanged.

### 7. `indoor_presence`

```
indoor_presence = (loc_class == 'at_home') AND (act NOT IN outdoor_at_home.target_code)
```

🔴 **Use `loc_class == 'at_home'`, not `loc_raw == 11`.** Work item 2.2 writes the rule as `LOC == 11`
because it predates the crosswalk; Italy maps **both** `11` and `12` to `at_home` to reproduce
D-S2-4's merge, so testing the raw code would silently drop Italy's `12`. The crosswalk's
`target_class` column is the single place the classes are defined.

Read the exclusion list **from `outdoor_at_home.csv`** — never inline it in code — so validation reads
the same list the transform used.

Nullable boolean, and **`null`, never `False`, wherever `loc_raw` is in its recorded-and-blank
state.** `False` means at home and outdoors, or not at home; `null` means we do not know.

### 8. Co-presence → six shared flags plus extras

For each country, drive entirely from `crosswalk_copresence.csv`: for each row, the national field
and value map to `shared_flag` with truth taken from `national_value_meaning` (`yes`/`no`).

🔴 **Spain codes `1 = yes` and `6 = no`.** A truthy cast of `6` makes every Spanish respondent
co-present with everybody simultaneously. **Read the meaning from the crosswalk column; never cast
the raw value.**

`cop_parent` is the **OR** of its national components (UK `WithMother`/`WithFather`, Italy
`cmadre`/`cpadre`; Spain's `PADRES` maps directly). The components **also** survive as their own
`cop_extra_<country>_<field>` columns — an OR that discards its inputs cannot be audited.

All `cop_*` and `cop_extra_*` are **nullable boolean**: `null` = not recorded, `False` = recorded and
absent. 🔴 **Never collapse the two.** Rows tagged `NOT_A_PRESENCE_FLAG` are not presence flags and
must not become one.

Do **not** pack the flags into an integer here. Packing is Step 3's job; `bit_position` is read at
Step 3 from this same crosswalk.

### 9. Emit

`harmonised.parquet`, one row per episode, **exactly** the D-S2-12 column list:

```
country, wave, hid, pid, diary_day,
episode_index, episode_index_step1, split_at_origin,
start_min, duration_min,
act, act_level1, act_level2,
act2, act2_level1,
loc_class, indoor_presence,
cop_alone, cop_partner, cop_children, cop_parent, cop_other_hh, cop_other_persons,
cop_extra_<country>_<field> ...,
act_raw, act2_raw, loc_raw,
mode, scheme, weight_ind, weight_dia
```

🔴 **`origin_hour` is NOT a column, here or anywhere.** `V2.i` FAILs on **any** column name containing
`origin`. Assert it yourself before writing the file. The native origin goes to the parquet's
**file-level metadata** and to `filter_report.md`, never to a row — a per-country origin column
leaks country identity into leave-one-country-out by the front door.

---

## TASK 2 — `filter_report.md`

🔴 **Count what the filter removed, per clause, per country.** A single total hides the thing worth
seeing. For each country report, per clause, the number of **respondents**, **diaries** and
**episodes** removed, plus:

* the **age floor used** and the **compiled per-country expression**;
* 🔴 for Italy, an explicit line stating the clause was evaluated **on a band, not an exact age**,
  naming band `04` and its bounds, so no later reader mistakes Italy's age filter for an exact one;
* the native origin hour per country, and Spain's **split count**;
* the three `act2` state counts per country;
* unmapped counts for `act` and `loc_class` per country;
* input and output episode counts, reconciling exactly.

---

## TASK 3 — run it

`scp` the crosswalks to `/speed-scratch/o_iseri/4J/outputs_step2/`, then **three unchained jobs**, one
per country, so a country that crashes does not take the other two with it:

```
sbatch -p ps --mem=16G -t 7-00:00:00 --wrap "cd /speed-scratch/o_iseri/4J && /speed-scratch/o_iseri/envs/step4/bin/python tools/4thJ_harmonise_step2.py --country es --in outputs_step1/run_20260816-2210 --crosswalks outputs_step2 --out outputs_step2/run_<stamp> --age-floor 11 > outputs_step2/run_<stamp>/harmonise_es.txt"
```

Create the output directory before submitting. One `sacct` call to check state — not a loop.

---

## 🔴 ACCEPTANCE TESTS — these decide whether the work is accepted

A parquet that exists is not a pass.

1. **`origin` appears in no column name**, asserted by the runner itself before the write.
2. **Spain's split count is reported and non-zero; the UK's and Italy's are exactly zero.**
3. **Episode counts reconcile**: input − filtered + splits = output, per country, arithmetic shown.
4. **Every non-null `act` exists in `activity_target_list.csv`**, and `act_level1 == act[0]` and
   `act_level2 == act[:2]` on every row — `G2.16`'s own condition.
5. **`act2`'s three states are all present** with counts, for every country that records it.
6. **`cop_*` columns are nullable boolean with a genuine `null` count**, not all-`False`. An all-`False`
   column where a country records nothing means missing was collapsed into absent, and that is a
   failure, not a tidy result.
7. **Spain's `cop_*` flags are not inverted** — show the share of Spanish episodes with
   `cop_alone = True` and confirm it is not the near-100 % a truthy cast of `6` would produce.
8. **`filter_report.md` carries the Italian band line.** Its absence fails the task.
9. **The grid assertions passed without a single coercion.**

Report every `NOT CHECKED` with a one-line reason from the spec. **`NOT CHECKED` is never a pass.**

---

## DELIVERABLE

`outputs_step2/harmonised.parquet` (or per-country parts plus the concatenation, your choice — say
which), `outputs_step2/filter_report.md`, `tools/4thJ_harmonise_step2.py`, and a Progress Log
**fragment** at `outputs_step2/proglog_step2_harmonise.md`. **The fragment is not the Progress Log** —
the manager merges it into `4thJ_02_harmonisation.md`.

The fragment must contain a section headed **WHAT I DID NOT VERIFY**. A fragment without one is
incomplete. Report anything you had to decide that this document did not decide for you, and say
plainly what you assumed.
