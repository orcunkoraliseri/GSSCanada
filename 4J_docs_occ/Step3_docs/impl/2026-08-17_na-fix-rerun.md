# COP re-verify + ACT2 re-run after NA fix — implementation state
Task doc:   (manager prompt, 2026-08-17)
Status:     DONE (both measurements collected; four author decisions listed under "Next")

## Ledger
- 1255143 · 4thJ_act2_measure.py (ACT2 tuple-cost measurement) · FAILED · exit 1 · /speed-scratch/o_iseri/4J_act2_1255143.out · crashed line 116 pack_cop(): TypeError int(pd.NA)
- 1255174 · 4thJ_cop_reverify.py (COP re-verify) · FAILED · exit 1 · /speed-scratch/o_iseri/4J_cop_reverify_1255174.out · crashed line 154 pack_cop(): TypeError int(pd.NA)
- 1255207 · 4thJ_act2_measure.py re-run after NA fix · SUBMITTED · exit pending · /speed-scratch/o_iseri/4J_act2_rerun_na_fix.out
- 1255208 · 4thJ_cop_reverify.py re-run after NA fix · SUBMITTED · exit pending · /speed-scratch/o_iseri/4J_cop_reverify_rerun_na_fix.out
- 1255207 · SUPERSEDED · FAILED exit 1 after 00:00:02 · "FATAL: transformers is not importable in this environment." — the re-run was submitted against `envs/step4`, which has no transformers. The NA fix itself was never exercised.
- 1255208 · SUPERSEDED · FAILED exit 1 after 00:00:02 · same cause, same message.
- 1255222 · 4thJ_act2_measure.py re-run, submitted by the manager via the original `4thJ_act2_setup_and_run.sh` (ENVDIR=/speed-scratch/o_iseri/envs/4j_tok, the venv that carries transformers 5.15.0) · SUBMITTED · exit pending · /speed-scratch/o_iseri/4J_act2_1255222.out
- 1255223 · 4thJ_cop_reverify.py re-run, same correction via `4thJ_cop_reverify_setup_and_run.sh` · SUBMITTED · exit pending · /speed-scratch/o_iseri/4J_cop_reverify_1255223.out

- 1255222 · ACT2 re-run · FAILED · exit 1 · 00:01:23 · /speed-scratch/o_iseri/4J_act2_1255222.out · Part A complete, Part B crashed at `4thJ_act2_measure.py:335`: `a2_val = None if (a2 is None or (isinstance(a2, float) and pd.isna(a2)) or a2 == "") else a2` → `TypeError: boolean value of NA is ambiguous`. **Same defect class as the pack_cop crash, second site: the `act2` column also carries `pd.NA`, and the `isinstance(..., float)` guard misses it.** The NA fix was applied to `pack_cop()` only.
- 1255223 · COP re-verify · **COMPLETED** · exit 0 · 00:02:10 · /speed-scratch/o_iseri/4J_cop_reverify_1255223.out · Part A and Part B both ran.
- 1255237 · 4thJ_act2_measure.py re-run, second NA-fix (act2 column, line 335), submitted via the shipped `4thJ_act2_setup_and_run.sh` · SUBMITTED · exit pending · /speed-scratch/o_iseri/4J_act2_1255237.out

- 1255237 · ACT2 re-run · **COMPLETED** · exit 0 · 00:01:38 · /speed-scratch/o_iseri/4J_act2_1255237.out · Part A and Part B both ran. **Both measurements are now collected; this implementation doc is DONE.**

## ACT2 tuple-cost result (job 1255237, read 2026-08-17)

Sample: 2500 diaries, seed 42, 69,418 episodes, `{'IT':1313,'ES':648,'UK':539}`; act2 present
16,001 / absent 53,417. 2,589 sampled episodes carried a null `cop_*` flag (bit-unset, not dropped).

```
cand form                                          worst/ep   median      p99      max
0    DUR,ACT,LOC,COP  (baseline, no ACT2)                 9    225.0    559.0      716
1    DUR,ACT,ACT2,LOC,COP   absent = sentinel '98'       11    275.0    685.0      877
2    DUR,ACT,LOC,COP,ACT2   absent = sentinel '98'       11    275.0    685.0      878
3    DUR,ACT,ACT2,LOC,COP   absent = empty field         11    238.0    580.0      751
4    DUR,ACT,LOC,COP,ACT2   absent = empty field         11    257.0    627.1      808
```

**What decides the ACT2 question.** Per episode, ACT2 costs a flat **+2 tokens** in every placement
and every absent-encoding — Part A cannot discriminate. Per diary it discriminates sharply, because
77 % of episodes have no secondary activity and the absent-encoding is therefore what dominates:

* **The `'98'` sentinel is the expensive choice: +50 tokens/diary median (+22 %).** It pays two
  tokens on every one of the 53,417 absent episodes.
* **The empty field placed before LOC (candidate 3) is the cheap choice: +13 tokens/diary median
  (+5.8 %), +21 at p99.**
* Placement matters only for the empty-field forms: before LOC costs +13, after COP costs +32. The
  two sentinel forms are identical (275.0) because the field is never empty, so position cannot
  change how the BPE merges around it.

`'98'` remains **verified absent** from the 43 shipped ACT2 target codes, so it is a legal sentinel;
it is simply not a cheap one.

🔴 **Every candidate, including the no-ACT2 baseline, exceeds `G3.5`'s band** (median 220 / p99 400).
The baseline alone is already 225.0 / 559.0. **ACT2 is therefore not what breaks `G3.5`** — the band
is broken before ACT2 is considered at all, and the same p99 finding appeared independently in the
COP job. Deciding ACT2 does not repair `G3.5`, and repairing `G3.5` does not decide ACT2. Two
separate author decisions. **No threshold was moved.**

**Why the two jobs report different baselines (225.0 here, 217.5 in job 1255223):** they sample
different diary populations. `4thJ_cop_reverify.py` excludes the 8,873 diaries that contain a
null-`loc_class` episode; `4thJ_act2_measure.py` does not. Not a contradiction, and not a defect in
either — but it means the two tables must not be read as one table, and whichever sentinel policy
the author sets for null LOC will move one of these baselines.

## Second NA-fix (2026-08-17, this task) — act2 site missed by the first round

The first NA-fix round (see "Verified" below) fixed `pack_cop()`'s null guard in both scripts but
missed a second, textually different site in `4thJ_act2_measure.py` that hits the same `pd.NA`
defect class: the `act2` column (also nullable-string/boolean dtype) has its own None/NaN guard
that job 1255222 crashed on at Part B, line 335.

**File:** `4thJ_act2_measure.py` (local copy fetched fresh from Speed — no local copy existed
before this task; scp'd down, edited, compiled, scp'd back).

**Line 335, before:**
```python
a2_val = None if (a2 is None or (isinstance(a2, float) and pd.isna(a2)) or a2 == "") else a2
```

**Line 335, after:**
```python
a2_val = None if (pd.isna(a2) or a2 == "") else a2
```

`pd.isna()` is checked first, so `a2 == ""` is never evaluated on `pd.NA`. Semantics unchanged:
`a2_val` is `None` when act2 is missing/null/empty string, else the value.

**Grep for `isinstance(` across the whole file found 2 hits total: line 335 (the actual bug, fixed
above) and line 116 (a comment inside `pack_cop()`, `# ... the old \`isinstance(val, float) and
pd.isna(val)\` guard missed it ...` — this is prose documenting the *first* round's fix, not code;
left untouched). So: 1 code site with this pattern, found and fixed; 1 comment mentioning the
pattern, correctly left alone.**

`4thJ_cop_reverify.py` was not opened or touched, per instructions (its job 1255223 already
completed successfully).

Compiled clean: `py -3 -m py_compile 4thJ_act2_measure.py` → no errors. Local file now 17,293
bytes (was 17,335 on Speed before this fix — the file shrank because the removed `isinstance`
clause was longer than nothing). Uploaded to Speed; `ls -la` on Speed confirms
`/speed-scratch/o_iseri/4thJ_act2_measure.py` is now 17,293 bytes, timestamped 14:17. Resubmitted
via `sbatch 4thJ_act2_setup_and_run.sh` (not a hand-rolled `--wrap`) → job 1255237.

## COP re-verification result (job 1255223, read 2026-08-17)

Sample: 2500 diaries, seed 42, 66,689 episodes, `{'IT':1348,'ES':745,'UK':407}`.
`loc_class` prevalence `{'at_home':0.6889,'other_place':0.174,'private_transport':0.128,'public_transport':0.0091}`.

Per-diary token cost under the **correct four-class LOC alphabet**:

```
candidate                       n   median      p99      max
1_decimal_0-63               2500    217.5    519.1      712
2_six_chars                  2500    242.5    577.1      793
3_two_octal                  2500    217.5    519.1      712
4_two_hex                    2500    218.0    519.1      712
5_baseline_csv_bits          2500    467.5   1099.2     1522
```

**D-S3-1's ranking SURVIVES.** Candidate 1 (decimal 0-63) is still tied-cheapest with candidate 3
(two-octal) at median 217.5, still **inside** `G3.5`'s median band of 220; candidate 2 (six chars) is
still **outside** it at 242.5. The reason D-S3-1 chose candidate 1 over candidate 2 is unchanged
under the corrected alphabet. The wrong-alphabet numbers were 200 / 225; the corrected ones are
217.5 / 242.5 — every candidate moved up by roughly the same amount, so the ordering did not change.

🔴 **NEW, and it needs the author: `G3.5`'s p99 band of 400 is exceeded by EVERY candidate**, best
case 519.1. This is not a packing question — even the cheapest possible COP encoding cannot bring the
p99 under 400, because the p99 diary simply has many more episodes than the 25-episode representative
string the 200-token benchmark was measured on. The band and the corpus disagree; the band was
project-chosen against a benchmark that was never a distribution. **No threshold was moved.**

## 🔴 Null co-presence flags — measured extent (job 1255223, full parquet)

```
country  flag                null_rows   distinct_diaries
ES       all six                     0                  0
IT       all six                     0                  0
UK       all six                 68464               9298
TOTAL rows with >=1 null cop_* flag: 68464, distinct diaries touched: 9298
```

The nulls are **UK-only and all six flags together** — a row either has all six or none, which reads
as "co-presence not collected/not answered for this episode", not as six independent missing values.
In Part B, 1,163 of the sampled episodes carried a null flag; they were treated as bit-unset (0) and
**not dropped**. 🔴 Whether "all six null" should encode as `0` (indistinguishable from a genuine
"alone=false, everything else false") or as its own sentinel is an **author decision**, and it is the
same question as the null-LOC one below.

## 🔴 Null `loc_class` — confirmed by this run

`24,800` rows carry a null `loc_class`; `73,254` diaries total, `64,381` usable, **`8,873` excluded
for a null-LOC episode**. The script drops those diaries from its own sample and says so; it does not
decide the sentinel policy. Confirmed, not carried over. Author decision.

## Manager note (2026-08-17)
The NA fix in both .py files is intact on Speed (both files 14:09, `pd.isna(val)` present twice in
each). Only the launcher was wrong: 1255207/1255208 bypassed the two shipped
`*_setup_and_run.sh` scripts and used `envs/step4/bin/python`. Rule for any future re-run of these
two measurements: **submit the shipped .sh, do not hand-roll an sbatch --wrap** — the venv, the pip
install and the `--output` name all live in the .sh.

## Verified
- Root cause (read from both local scripts before fix): pack_cop()'s null guard was
  `if val is None or (isinstance(val, float) and pd.isna(val))`. The cop_* boolean columns use
  pandas nullable "boolean" dtype, whose missing sentinel is `pd.NA` — type NAType, not float and
  not None. `isinstance(val, float)` is False for pd.NA, so the guard fell through to
  `int(val)` → `int(pd.NA)` → TypeError. Identical bug, identical line pattern, in both scripts
  (4thJ_act2_measure.py:116, 4thJ_cop_reverify.py:154).

## Decisions
- Fix applied identically to both scripts, minimal: replaced the null guard with `pd.isna(val)`
  alone (correctly catches None/NaN/NaT/pd.NA). A null flag is still treated as bit-unset (0) —
  same behavior the old code intended, now actually reached instead of crashing first.
- Added a null-flag episode counter: pack_cop() takes an optional `null_episodes` set; when any
  of the six cop_* flags on a row is null, the row's (country, hid, pid, diary_day,
  episode_index) key is added. Part B loops in both scripts create this set, pass it into every
  pack_cop() call, and print `len(...)` after the loop — "episodes in Part B sample with >=1 null
  cop_* flag (treated as bit-unset=0, NOT dropped): N". No episode is dropped.
- Added a null-extent table (per country x per cop_* flag: null row count, distinct diary count),
  computed on the full harmonised.parquet read, printed before Part B in both scripts. Uses a
  local diary-key Series only — nothing is written back onto the scripts' existing `df`/
  `df_clean`/sampling variables, so downstream logic (including cop_reverify's loc_class-null
  drop path) is byte-for-byte unchanged.
- Part A untouched in both scripts — it never calls pack_cop() (uses fixed REP_COP/REP_V
  constants), so Part A's already-produced results are expected to reproduce identically.
- Candidate list, tokenizer, seed (42), sample size (2500 diaries), HARMONISED/CW_* paths: not
  touched.
- NOT ACTED ON (flagging only, per instructions): 4thJ_cop_reverify.py's existing (unrelated,
  unchanged) loc_class-null drop path reported, in job 1255174 before the crash — no, job 1255174
  crashed before reaching that print in Part B this run; the number below is carried over from
  the manager prompt's own citation, not re-derived by this task: "24,800 rows with a null
  loc_class, excluding 8,873 of 73,254 diaries" from Part B sample. This is a separate open
  question for the manager. The existing drop behaviour (dropna on loc_class, whole-diary
  exclusion) was left exactly as it is — not modified, not re-verified in this task.

## Next
- 🔴 job 1255237 (ACT2 re-run, second NA fix) is pending — a fresh agent should poll and read
  `/speed-scratch/o_iseri/4J_act2_1255237.out` once done, confirming Part B no longer crashes at
  line 335 and that G3.5 comparisons print.
- Wait for both resubmitted jobs to finish (manager/fresh agent polls squeue/sacct — NOT this
  agent). When done, read the two new .out files for:
  1. The null-extent table (per country/flag, rows + diaries) — this is a reportable finding.
  2. The "episodes ... with >=1 null cop_* flag" count from Part B.
  3. Confirm Part A's numbers in both files match Part A's numbers in the original failed run's
     stdout (if any was captured before the crash) or are internally consistent (Part A always
     runs to completion since it doesn't touch real data).
  4. Confirm Part B now completes without a crash, and G3.5 band comparisons print.
- JobIDs and output paths for the two new submissions are appended below once `sbatch` returns
  (see Ledger).

## WHAT I DID NOT VERIFY
- Did not run the scripts locally against real harmonised.parquet (no local python env with
  pandas/transformers on this machine, and the file lives only on Speed) — verified only that
  both files compile (`py -3 -m py_compile`), not that they execute correctly against real data.
- Did not re-derive or check the 24,800-row / 8,873-diary loc_class-null figure cited in the task
  doc; carried over verbatim, not verified in this task.
- Did not compare original (pre-crash) Part A stdout against the new run's Part A stdout line by
  line — both original jobs crashed inside Part B, so no original Part B output exists to diff
  against; Part A output from the original runs may exist in the .out files up to the crash point
  and should be diffed by whoever collects the new results.
- (this task) Did not run job 1255237 to completion or read its output — job was submitted and
  this agent ended its turn per the no-parking rule. Did not verify Part A of this run against
  1255222's Part A (should be identical, since Part A doesn't touch pack_cop or act2). Did not
  re-check 4thJ_cop_reverify.py for the same isinstance pattern in this task (out of scope per
  instructions; job 1255223 already completed clean).
