# COP-packing re-verification (D-S3-1 LOC-alphabet check) — implementation state
Task doc:   (verbal manager task, this session) — verify the D-S3-1 COP-packing measurement
            (job 1252633) against the possibility that `tools/4thJ_cop_measure.py` measured
            LOC on the wrong alphabet.
Status:     IN PROGRESS

## Ledger
- **Job 1255174** -- COP-packing re-verification (LOC-alphabet corrected). Submitted
  `sbatch -p ps --mem=16G -t 7-00:00:00` from `/speed-scratch/o_iseri`, script
  `4thJ_cop_reverify.py` -> via `4thJ_cop_reverify_setup_and_run.sh` (both scp'd from
  `tools/4thJ_cop_reverify.py` / `tools/4thJ_cop_reverify_setup_and_run.sh`; confirmed LF-only /
  no CRLF via `file` on Speed before submission -- `grep -c $'\r'` failed on tcsh's login shell,
  "Illegal variable name", so `file` was used instead, both scripts reported "ASCII text
  executable" with no CR markers). Reuses `/speed-scratch/o_iseri/envs/4j_tok` (already has
  transformers/pandas/pyarrow/numpy from job 1255143's setup; this job's runner only installs if
  missing). Confirmed present on Speed before submission (via `ls -la`):
  `/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_location.csv` (11,758 bytes),
  `/speed-scratch/o_iseri/4J/outputs_step2/crosswalk_copresence.csv` (16,697 bytes),
  `/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet`
  (18,603,780 bytes, same file A2/job 1255143 used). State: **SUBMITTED, not yet checked** -- do
  not wait for it in this session. Output will land at
  `/speed-scratch/o_iseri/4J_cop_reverify_1255174.out`. Does PART A (in-situ worst-case sweep,
  LOC x COP = 256 combinations per candidate, representative episode DUR=30/ACT=311) and PART B
  (real diaries, n<=2500 seed=42, median/p99/max tokens/diary per candidate, G3.5 band check,
  diaries with any null-loc_class episode excluded and the exclusion count reported). Does NOT
  touch `tools/4thJ_cop_measure.py`, does NOT touch job 1255143 or its files.
  **Next agent: check with a single
  `sacct -j 1255174 --format=JobID,State,Elapsed,ExitCode` (one call, not a poll loop), then read
  the `.out` file with `grep`/`tail`, not a full cat, and write
  `outputs_step3/cop_packing_reverification.md` from it (table: candidate name / accepted worst /
  accepted diary tokens (200/225/200/210/450) / new worst / new median / new p99, plus the loc_class
  prevalence line and the excluded-diary count). Report to the author/manager whether the D-S3-1
  ranking (candidate 1 decimal and candidate 3 octal tied cheapest at 8/200; candidate 2 six-char
  rejected for exceeding G3.5's 220-token median band at 225; candidate 5 baseline worst at 450)
  survives under the corrected LOC alphabet, or flips -- do not decide or change D-S3-1.**

## Verified

### Step 1 — the claim is CONFIRMED, by direct code read

`tools/4thJ_cop_measure.py:42-43` (the script behind the accepted D-S3-1 decision, job 1252633):
```
_LOC = ["11", "31", "11", "91", "11", "11", "31", "11", "11", "11", "11", "41", "31",
        "11", "11", "91", "11", "21", "31", "11", "11", "11", "11", "91", "11"]
```
and `4thJ_cop_measure.py:56`: `REP_DUR, REP_ACT, REP_LOC, REP_V = 30, "311", "11", 22` — the
representative episode (the one actually swept over all 64 COP values to produce the "worst case"
column in the accepted report) is fixed at `LOC="11"`, a short numeric placeholder.

`Step2_docs/4thJ_02_harmonisation.md` D-S2-3 (lines 131-141, restated 517-519, 985-986) is explicit:
"**no range filter, anywhere. Class membership is by explicit crosswalk** ... The target classes are
**at-home / other place / private transport / public transport**". Confirmed directly from
`Step2_docs/outputs_step2/crosswalk_location.csv`'s `target_class` column: the four distinct values
present are exactly `at_home`, `other_place`, `private_transport`, `public_transport` (no numeric
codes ever appear in that column — `source_code`, a separate column, carries the national numeric
codes such as ES `11`/`21`/`31`/`41`, which map to those four classes, e.g.
`crosswalk_location.csv:3` `es,11,Casa,at_home,...`).

`Step3_docs/4thJ_03_serialisation.md:27` (work item 3.2's own decision table) already states this
correctly in prose: "`LOC` is the real HETUS code, **not** `RL07`'s invented 1-6 ... 🔴 **But not
"10-39":** Spain carries `41`, public transport (F-ES-3, D-S2-3). **The serialised alphabet is
whatever `crosswalk_location.csv` emits, read from that file, never written here as a range**" — i.e.
the spec doc anticipated exactly this and still `4thJ_cop_measure.py` (written the same day, per its
own docstring "COP became six binary flags on 2026-08-16") used numeric placeholders, not the four
class strings.

Confirming independently: `tools/4thJ_act2_measure.py:27-33` (a LATER script, the accepted A2 ACT2
measurement, job 1255143, submitted THIS SAME 2026-08-17 session under a different task) already
flags this identical fact in its own docstring, unprompted:
"🔴 LOC is read from the harmonised table's own `loc_class` column, which as of D-S2-3 is one of four
semantic-class strings (at_home / other_place / private_transport / public_transport), NOT a short
numeric HETUS code. This differs from `4thJ_cop_measure.py`'s own synthetic LOC placeholders
("11","31","91","41","21"), which were written before / independent of that decision... it does not
attempt to re-measure or correct the earlier, already-accepted COP result." This is independent
corroboration written by a different agent on a different task, not something this session produced.

**Note: `"91"` used in `4thJ_cop_measure.py`'s `_LOC` array is not even a real Spanish location code**
— `crosswalk_location.csv`'s ES rows only go up to `41` (public transport). So four of the script's
five distinct placeholder values (`11`,`31`,`41`,`21`) map onto real Spanish codes, but `91` was
invented and does not exist in the crosswalk at all.

**Real column name confirmed:** `harmonised.parquet` carries the LOC value in a column named
`loc_class` (confirmed from `4thJ_act2_measure.py:233,238`, which reads it live and prints
`sorted(df["loc_class"].dropna().unique().tolist())`).

**CLAIM CONFIRMED.** The accepted D-S3-1 measurement (job 1252633) and the report at
`Step3_docs/outputs_step3/cop_packing_measurement.md` measured every candidate's episode/diary/
worst-case token cost with `LOC` fixed at 2-character numeric placeholders (`"11"`, `"31"`, `"41"`,
`"21"`, and the invented `"91"`), never with the actual 4-class alphabet
(`at_home`/`other_place`/`private_transport`/`public_transport`) the corpus will emit. The ranking
margin this rested on is thin: candidate 2 (six binary chars) was rejected specifically because its
diary cost (225 tokens) exceeded `G3.5`'s median band of 220 by 5 tokens — a margin narrow enough
that a longer LOC alphabet (`public_transport` = 16 characters vs `"41"` = 2 characters) could
plausibly move every candidate's count enough to change which side of 220 candidate 2 falls on, or
even affect candidates 1/3's tie.

## Decisions
- **New script, not an edit**: `tools/4thJ_cop_reverify.py` (new file). Does not touch
  `tools/4thJ_cop_measure.py`. Mirrors its 5 COP-candidate encodings and its DUR/ACT skeleton exactly
  (same `_DUR`, same `_ACT`, same `_COP_VALS = (7*i+3) mod 64`, same 5 `CANDIDATES` functions,
  byte-identical), changing only the LOC slot and adding a real-diary pass (median/p99), matching how
  `tools/4thJ_act2_measure.py` extended the same base methodology for ACT2.
- **LOC alphabet for the synthetic in-situ sweep**: read live from
  `Step2_docs/outputs_step2/crosswalk_location.csv`'s `target_class` column on Speed (not
  hard-coded), same discipline D-S2-3 itself requires and the same discipline
  `4thJ_act2_measure.py` used for ACT2/bit_position.
- **Representative episode LOC** (single-episode metric, for continuity with the accepted report's
  table shape): `at_home`, the class `"11"` (the original script's fixed REP_LOC) actually maps to,
  confirmed from `crosswalk_location.csv:3` (`es,11,Casa,at_home`).
- **Worst-case sweep dimensions widened**: the accepted script only swept the 64 COP values with LOC
  held fixed. Because the finding is specifically that LOC's own token cost was never exercised, this
  re-verification sweeps **LOC (4 classes) × COP (64 values) = 256 combinations** per candidate at the
  representative DUR/ACT slot, reporting the true worst case and its argmax (loc, v) — not assuming
  the worst case sits at whichever LOC was hard-coded.
- **Real-diary pass added** (median/p99 tokens/diary per candidate, sampled from real diaries), because
  the manager's task explicitly asked for it and because a single synthetic diary (the original
  script's only diary-level metric) cannot show the effect of LOC's real prevalence distribution
  across three countries. Same sampling pattern as `4thJ_act2_measure.py`: `N_SAMPLE_DIARIES=2500`,
  `SEED=42`, diary key `(country,hid,pid,diary_day)`, columns read live
  (`duration_min`,`act`,`loc_class`, six `cop_*` shared flags), `bit_position` read live from
  `crosswalk_copresence.csv` via the same `pack_cop` logic as `4thJ_act2_measure.py:106-118`
  (unset/null shared flags treated as bit 0, same flagged-not-decided caveat carried over verbatim).
  No ACT2 field and no prefix/`<eor>` — the tuple stays `DUR,ACT,LOC,<COP>;`, matching D-S3-1's own
  scope exactly (COP-packing candidates only, not the separate ACT2 question).
- **Reusing the harmonised.parquet already staged on Speed**: same file A2 used,
  `/speed-scratch/o_iseri/4J/outputs_step2/run_20260817-strata/harmonised.parquet`, confirmed
  byte-identical to the local copy in the 2026-08-17 step3-build ledger. No new scp needed for data.
- **Venv reuse**: same `/speed-scratch/o_iseri/envs/4j_tok` venv A2 used and set up (already has
  transformers/pandas/pyarrow/numpy installed as of job 1255143's setup script) — this job's sbatch
  script checks for it and only installs if missing, same pattern as
  `tools/4thJ_act2_setup_and_run.sh`.

## Next
**A FRESH agent (or the manager) picks this up after the job completes.**
1. Check job status with a single `sacct -j 1255174 --format=JobID,State,Elapsed,ExitCode` call. Do
   not poll.
2. If COMPLETED: `grep`/`tail -c` the `.out` file (never full cat) for `SUMMARY`, `PART A`, `PART B`,
   `RANKING`. scp back to `Step3_docs/outputs_step3/cop_packing_reverification.md` (already the
   planned output path — write the report there once the numbers are in hand).
3. Report to the author/manager: whether the D-S3-1 ranking (candidate 1 decimal / candidate 3 octal
   tied best, candidate 2 six-char rejected at the 220 threshold, candidate 5 baseline worst) survives
   under the correct LOC alphabet, or flips. **Do not change D-S3-1, do not edit
   `4thJ_cop_measure.py`, do not move `G3.5`'s threshold — report the number only.**
4. If job 1255143 (ACT2, unrelated) happens to be visible in the same `sacct` sweep, do not report on
   it or touch its files — out of scope for this task.

## WHAT I DID NOT VERIFY
- Did not independently re-derive whether the original 200-token `G3.5` benchmark itself (jobs
  1234177/1234199/1234216, predating even `4thJ_cop_measure.py`) used the correct or wrong LOC
  alphabet — out of scope, flagged only (same caveat the 2026-08-17 step3-build ledger already
  recorded).
- Did not verify country-level prevalence of the four LOC classes (e.g. what fraction of real episodes
  are `public_transport`, the longest and most expensive string) beyond what the real-diary sample
  will show — the real-diary median/p99 pass is the mechanism meant to capture this, not a separate
  prevalence table.
- Did not re-examine whether `crosswalk_location.csv` might carry a 5th class or an "unmapped" residue
  category that could also appear in `loc_class` — relying on D-S2-3's own statement ("every national
  code maps to exactly one, or is listed as unmapped") and the four distinct values actually observed
  in the CSV; if `loc_class` can be null/unmapped in the real data, the real-diary pass will surface it
  as a `NaN`/empty string in the sample and should be checked by whoever reads the job output, since
  this session did not add a sentinel check for it (unlike the ACT2 script's explicit sentinel check).
