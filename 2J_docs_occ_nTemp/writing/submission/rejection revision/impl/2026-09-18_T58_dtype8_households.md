# T58 — what the 43 households with a bare `DTYPE` of `8` actually are (plan §5 item 32) — implementation state

Task doc:   this file.
Opened by:  manager, 2026-09-18, plan §5 item 32 (Progress Log (cd)).
Status:     IN PROGRESS 2026-09-18. Job 1329676 submitted, PENDING/RUNNING; not polled by this employee (no-wait rule).
Scope:      **Diagnosis and documentation only.** Not a gate, not a fix. **Do not drop, recode or repair a
            single row.** You explain what they are; the manager rules on what the supplement says.

## The finding you are explaining (established, do not re-derive)
- In the frozen 2022 stock (**Nb-f**, 144,465 households, 6,934,320 rows), **43 households carry a `DTYPE`
  value of the literal `8`**.
- `STOCK_WEIGHTS` has four keys, and the stock-weighted sum skips anything not in `ARCH_NAMES`
  (`SingleD`, `OtherDwelling`, `MidRise`, `HighRise`). So those 43 households are **silently excluded from
  every stock-weighted figure, on both the 2022 and the 2030 basis**.
- 43 of 144,465 is immaterial to any number. **That is not the problem.** The problem is that a bare integer
  sits in a dwelling-type column that everywhere else holds a named archetype, nobody has ever said what it
  means, and the supplement is about to describe the dwelling-type classification to a reviewer.

## What to answer, in this order
1. **Confirm the count yourself** — how many households in the frozen 2022 stock carry `DTYPE == '8'`, and how
   many distinct `DTYPE` values exist in that column with the row count of each. Do not take 43 from this doc.
2. **What does `8` mean in the source?** Find it in the codebooks, not by inference. The repository has
   `2J_docs_occ_nTemp/codebooks/` and `references_*` folders; the census/GSS dwelling-type variable will have a
   published value list. **Quote the codebook line and name the file.** If the codebook says "Other, including
   mobile home" or similar, say so exactly; if no codebook covers it, say **NOT FOUND** — a clean NOT FOUND is
   a real answer here and is far better than a guess.
3. **Where does `8` survive the mapping?** Find the code that maps the raw dwelling-type value to the four
   archetype names, cite it as `file:line`, and show what it does with a value it does not recognise — does it
   pass the raw value through, assign a default, or drop the row? That single code path is the whole
   explanation.
4. **Are these 43 households in the simulated sample at all?** Check whether any of them appears in any cell
   manifest of the rebuilt campaigns (T21's `out/step8/<cell>/cell_manifest.csv` is the reference draw). If
   none does, say so — it means they never reached a run and the exclusion is upstream of the weighting.
5. **Do they share anything?** Province, household size, at-home stratum, match tier, survey cycle. Use only
   columns already present. A null result is a real answer.

## Deliverable
Two or three plain sentences the supplement can use, written at the end of this doc under **"Wording for the
supplement"**, saying what these households are, why they are outside the four archetypes, and that they are
excluded from stock-weighted figures. **Do not write them into any manuscript file** — the manager places
them. If the answer is NOT FOUND, the wording says that plainly instead of inventing a category.

## Hard rules
- **Login node `speed-submit2` is for submission only.** Allowed there: `sbatch squeue sacct scancel scontrol
  cd ls scp module load` plus **single-file** `tail head grep wc -l cat`. **Forbidden there, by name:
  `python` (any form, including one-liners), `find`, `mkdir`, `du`, `md5sum`, `cp`, and any blocking `srun`.**
  Create remote directories only by `scp -r` of a local folder containing `.keep` files.
- ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Remote shell is **tcsh**:
  **no `2>&1`, no `2>/dev/null`.**
- Every job `-p ps -t 7-00:00:00`. Python on compute nodes only:
  `/speed-scratch/o_iseri/envs/step4/bin/python`. Submit at **`-c 1 --mem=16G`; do not raise it** — 2J stays
  at or under 32 CPUs in flight whatever the association limit says.
- The stock files are large. **Never read one into your context.** Stream them in the job; read only its report.
- **Read-only on every input.** No row is dropped, recoded or repaired. No pipeline code is edited. Census and
  GSS inputs are research data — no silent cleaning.
- **You never wait.** Submit, write the JobID into the Ledger, end the turn.
- Codebook reading is local and needs no job; the counting needs one. Do the local reading first so the job
  can be written once.

## Controls
- **Seen-working:** your counter must reproduce the total household count of the frozen stock (144,465) and the
  known row total (6,934,320) before any per-value count of yours is quoted.
- **Seen-failing:** run the same counter over a small copy in which you have deliberately changed one
  household's `DTYPE`, and show the per-value counts move by exactly one. Both controls in **one** file under
  `T58/logs/`, from **one** invocation, with "did not run" / "ran and did not fire" / "ran and fired" kept
  distinct.

## Report
`/speed-scratch/o_iseri/2J_revision/T58/logs/t58_dtype8.txt`, `==== CONTROLS ====` first, then
`==== FINDINGS ====` answering 1-5 in order. If the wrapping job exits 0 whatever the inner steps return, say
so here and write each inner exit code into the report by name.

## Ledger
- Job **1329676** · `t58_job.sh` runs `t58_dtype8.py` on Nb-f stock + T21 step8 manifests · submitted `-p ps -c 1 --mem=16G -t 7-00:00:00` from `/speed-scratch/o_iseri/2J_revision/T58/T58_scripts/` · state PENDING/RUNNING at submission time, not polled · will write `/speed-scratch/o_iseri/2J_revision/T58/logs/t58_dtype8.txt` (report, `==== CONTROLS ====` then `==== FINDINGS ====`) and `slurm_1329676.out`/`.err` in the same `logs/` dir. **Next agent: read the report, do not re-run unless it errored.**

## Verified
- **Q2 answered by direct local read (not inference), no job needed.** `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\0_Occupancy\DataSources_CENSUS\cen21.sps` lines 360-364 (Census 2021 PUMF SPSS syntax file):
  ```
  DTYPE
  1   "Single-detached house"
  2   "Apartment"
  3   "Other dwelling"
  8   "Not available"
  ```
  Variable label at line 84: `DTYPE 'Structural type of dwelling'`. So DTYPE==8 is the Census's own "not available" code, not a fifth category and not something invented downstream. This is a real FOUND, not a NOT FOUND — but it was found in `0_Occupancy/DataSources_CENSUS/cen21.sps`, NOT in `2J_docs_occ_nTemp/codebooks/` or the `references_*` folders the task doc pointed at (those are GSS time-use activity/presence codebooks and never mention DTYPE).
- **Q3 answered by direct local read.** `eSim\eSim_occ_utils\21CEN22GSS\21CEN22GSS_occToBEM.py`:
  - Lines 101-105: `self.dtype_map = {"1": "SingleD", "2": "Apartment", "3": "OtherDwelling"}` — three keys only.
  - Line 142: `dtype_label = self.dtype_map.get(val_str, val_str)` — `.get()` defaults to the raw value itself, so `val_str == "8"` returns literal `"8"` unchanged: passthrough, not a drop, not a default to a named archetype.
  - Lines 143-153: the only further branch fires on `dtype_label == "Apartment"` (splits into HighRise/MidRise by BEDRM); a passed-through `"8"` never enters it.
  - Confirmed the frozen stock's schema matches this script's output columns (`SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,Metabolic_Rate`), per `2026-09-15_T20_wp1_d1_2030_build.md:196` and `2026-09-17_T52_T29_diagnosis.md:182` (both state the Nb-f `_framev2.csv` stock has the same columns as `BEM_Schedules_2022.csv`, which this script produces).
  - Confirmed `ARCH_NAMES`/`STOCK_WEIGHTS` downstream guard (`08_simulation_plots.py:55-58,70`, copied into T06/T09/T15/T29 scripts) is a pure `if a in ARCH_NAMES` skip — the exclusion happens at weighting, not at mapping.
- **Q1, Q4, Q5 dispatched to the job, not yet read back** (no-wait rule) — job 1329676, report path above.
- **Stock file used**: `/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv` (608,590,559 B, confirmed present via remote `ls -la` before submit) — this is the file `STOCK_WEIGHTS`-using scripts (`t20_job.sh:45`) call `STOCK`, i.e. the Nb-f frozen 2022 stock referred to in plan item 32, not `BEM_Schedules_2022.csv` (a separate file in the same T18c build with the same schema).
- **Manifest tree**: `/speed-scratch/o_iseri/2J_revision/T21/out/step8/` confirmed present, 25 entries (expect 24 cell dirs, `ls` not broken down further — job itself checks each of the 24 named cells and reports any missing by name).

## Decisions
- Task doc pointed at `2J_docs_occ_nTemp/codebooks/` and `references_*` for the DTYPE codebook; those cover only GSS activity/presence codes. Decided to search the repo broadly instead of stopping at "NOT FOUND in the named folders" — found DTYPE's real codebook (`cen21.sps`) under `0_Occupancy/DataSources_CENSUS/`. This is a genuine FOUND answer, sourced from a Census PUMF syntax file (a legitimate published value-label list), not an inferred category.
- Used the `_framev2.csv` file (not `BEM_Schedules_2022.csv`) as "the frozen 2022 stock" for the job, because that is the file the project's own `STOCK_WEIGHTS`/`ARCH_NAMES` machinery (`t20_job.sh:45`) names `STOCK`. If the report's row/household counts do not reproduce 6,934,320/144,465, this choice needs revisiting against `BEM_Schedules_2022.csv` instead.
- Seen-failing control changes one whole household's DTYPE (all 48 rows) to a sentinel string never otherwise present in the small slice, and checks the household-level bucket counts move by exactly +1/-1 with every other bucket unchanged — chosen over a single-row edit because DTYPE is a household-level attribute duplicated across all 48 rows in this schema, so a single-row edit would leave the household's own value inconsistent and be a less faithful control.
- Q4 checks direct match plus two ID-format variants (`HH` prefix stripped/added) between stock `SIM_HH_ID` and manifest `sim_hh_id`, because the direct-match precedent in `t29_check.py`'s own `.isin()` join was the only evidence found for the ID format, and this was not independently reconfirmed against the real files before dispatch.

## Wording for the supplement
Pending the job's Q1/Q4/Q5 results — the mechanism (Q2/Q3) is already fully verified above, but the sentences the manager will use should also state the actual count reproduced by this job and whether the households ever appear in a simulated run, so this section is filled in by the agent that reads `t58_dtype8.txt`, not before.

## Next
Read `/speed-scratch/o_iseri/2J_revision/T58/logs/t58_dtype8.txt` (small, safe to `cat`/`grep` on the login node — it is a short generated report, not the stock file). Confirm `[seen-working]` and `[seen-failing]` both say "ran and fired" with PASS before quoting any Q1/Q4/Q5 number. If `[seen-working]` reports rows/households different from 6,934,320/144,465, stop and re-open the Decisions item above about which stock file is "the" frozen stock. Then fill in Verified (Q1/Q4/Q5 numbers), and write the final "Wording for the supplement" using Q2+Q3 (already verified) plus the job's Q1/Q4/Q5 findings. Do not touch any manuscript file.

## Manager interim ruling, 2026-09-18 (plan log entry (cl)) — NOT a closure

**Job `1329676` is unread.** Q1, Q4 and Q5 are unanswered. What follows rules only on Q2 and Q3, which needed
no job and which **the manager re-read at source rather than accepting from the report**.

**Q2 is a real FOUND, and I verified it myself.** `0_Occupancy/DataSources_CENSUS/cen21.sps:360-364` reads
exactly `DTYPE / 1 "Single-detached house" / 2 "Apartment" / 3 "Other dwelling" / 8 "Not available"`, and
`:84` labels the variable `'Structural type of dwelling'`. **`8` is Statistics Canada's own missing-value
code.** That reframes plan §5 item 32 completely: these are not 43 households of a mystery fifth dwelling
type, they are **43 households whose dwelling type the Census did not release.** That is a clean sentence the
supplement can carry without apology, and it is the opposite of an invented category.

**Q3 verified at source too.** `21CEN22GSS_occToBEM.py:101-105` maps only `"1"`, `"2"`, `"3"`; line 142 is
`self.dtype_map.get(val_str, val_str)`, i.e. **an unrecognised value is passed through unchanged**, so `"8"`
survives into the stock file as a literal `DTYPE` label. The Apartment branch at 143-153 never fires for it.
**So nothing in the pipeline decides to exclude these households** — the exclusion happens later, and only
because `ARCH_NAMES` has no member called `8`. The wording must reflect that distinction: it is **an absence
of a category, not a rule that drops rows.**

**The employee's scope expansion is upheld, and it is the lesson of this task.** The brief pointed at
`codebooks/` and `references_*`; those hold GSS activity codebooks and never mention `DTYPE`. Stopping there
would have produced a **NOT FOUND that was simply a search in the wrong place** — the worst possible outcome
here, because the brief had pre-blessed NOT FOUND as a real answer and it would have been believed. **Rule
for every future brief: the named search locations are a starting point, not a boundary, and NOT FOUND is
only honest after searching where the variable actually comes from.**

**The employee's own guard stands and must be honoured**: if `[seen-working]` does not reproduce 144,465
households and 6,934,320 rows, the wrong stock file was streamed and **no count from that report may be
quoted** — the choice between `..._framev2.csv` and `BEM_Schedules_2022.csv` reopens instead.

**New finding, made by the manager while verifying Q3, and it is bigger than item 32. Recorded as plan §5
item 34.** The same codebook gives **`BEDRM 8 = "Not available"`** (`cen21.sps:252-259`). The Apartment
branch does `int(float(bedrm_raw))` and then `"HighRise" if bedrm_int <= 1 else "MidRise"`. **`8` parses
cleanly to 8, which is `>= 2`, so an apartment whose bedroom count the Census did not release is silently
classified as a mid-rise** — not because it has two or more bedrooms, but because the missing-data code
happens to be a large number. The separate `default=2` / `except -> 2` fallbacks land the same way.
**This is worse than item 32 in one specific respect: those 43 households are outside every weighted figure,
whereas these households are inside them, carrying a dwelling type they were never measured to have.**
It is **not yet a number** — how many households have `DTYPE == '2'` with `BEDRM == '8'` is unmeasured, and
it may well be none. **Measure before describing it as anything.** `BEDRM` is a column of the stock file
already being streamed, so the agent that reads `1329676` opens **T59** with that one extra count, reusing
`t58_dtype8.py` rather than writing a new streamer. **No MidRise or HighRise split may be described as
bedroom-based in the manuscript until that count is read.** No code is changed either way — the runs are
delivered against the code as it stands.

## Manager, 2026-09-18 (plan log entry (cm)) — job `1329676` FAILED at its own control; T59 opened

**Read this together with the interim ruling above; it does not change any of it.** Q2 and Q3 stand, because
they were answered locally at source and needed no job. Q1, Q4 and Q5 produced **nothing**.

`sacct -j 1329676` says **`COMPLETED`, ExitCode `0:0`, Elapsed `00:00:02`.** The report says:

```
==== CONTROLS ====
[seen-working] did not run: ValueError: Usecols do not match columns, columns expected but not found:
  ['Day_Type', 'Hour', 'SIM_HH_ID']
[controls] FAILED with ValueError: ...
==== INNER EXIT CODES (by section) ====
controls: 1
```

**This is the task working exactly as designed and it is worth more than a clean pass would have been.**
The seen-working control was the first thing to run, it did not run, and **because the brief made
"did not run" a distinct outcome from "ran and did not fire", no count was produced and therefore none was
quoted.** The employee's own Decisions section had pre-registered this precise failure ("if the report's
row/household counts do not reproduce 6,934,320/144,465, this choice needs revisiting") — the guard was
written before the run and it caught the run.

**Add this to the list of times a success signal lied.** `sacct` said `COMPLETED 0:0` on a job whose only
work raised an exception. That is the same family as (cc)'s "three success signals agreed and the output was
still short". **The rule stands and is now evidenced twice: for any job whose wrapper may swallow the inner
status, `sacct` is not a verdict. The report's own per-section exit codes are.**

**The cause, established by the manager without a job.** Two different files exist and T58 read the wrong
one. `..._aug_Full_Aggregated_framev2.csv` is the **person**-level augmented frame — its header begins
`PP_ID,HH_ID,MATCH_TIER,occID,...` and carries `DTYPE` and `BEDRM` as **raw Census codes**; it has no
`SIM_HH_ID`, `Day_Type` or `Hour`. `BEM_Schedules_2022.csv` is the **household × day-type × hour** file and
carries `DTYPE` as the **mapped archetype label**. Item 32's own shape — 144,465 households and 6,934,320
rows, and 6,934,320 = 144,465 × 48 — is the schedule file's. **So item 32 lives in `BEM_Schedules_2022.csv`,
and item 34 lives in `_framev2.csv`, and neither substitutes for the other.**

**That split is a gain, not just a correction.** Item 34 needs the **raw** `BEDRM` and `DTYPE` codes to be
measurable at all, and only `_framev2.csv` has them; the mapped file has already thrown the evidence away.
Had T58's first job succeeded on the schedule file, item 34 would have been unmeasurable there and the
question might have looked answered.

**T59 dispatched** (`impl/2026-09-18_T59_dtype8_rerun_and_bedrm8.md`, fresh Sonnet, 1 CPU): Part A redoes
Q1/Q4/Q5 on `BEM_Schedules_2022.csv` with the 144,465 / 6,934,320 reproduction as a hard stop, and Part B
measures item 34 on `_framev2.csv` — the `DTYPE=='2'` AND `BEDRM=='8'` household count, the full `BEDRM`
distribution within `DTYPE=='2'`, what archetype those households actually carry in the schedule file, and
separately the blank/unparseable `BEDRM` cases that reach `MidRise` by the `except -> 2` path.
**The brief says in advance that zero is a good answer to Part B and closes item 34 cheaply**, so that a null
result is not treated as a failed search.

## WHAT I DID NOT VERIFY
- Did not read back the job's report — job was only just submitted (no-wait rule); Q1 (the real distinct-value/household counts), Q4 (manifest membership) and Q5 (shared attributes) are computed but unread.
- Did not independently reconfirm on the real files that stock `SIM_HH_ID` and manifest `sim_hh_id` use the same ID format (e.g. whether either carries an `HH` prefix) — relied on `t29_check.py`'s precedent of joining them directly via `.isin()`; the job checks three format variants defensively, so this gap is covered by the job itself, not by prior verification.
- Did not check whether `21CEN22GSS_occToBEM.py` is definitely the exact script version that produced the specific Nb-f `T18c` build (the T18c build ran from a repo snapshot under `/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/`, not necessarily this exact working-tree copy) — the schema match (same column names/order) is strong indirect evidence but the script bytes were not diffed against whatever ran in that build.
- Did not check disk space/quota under `/speed-scratch/o_iseri/2J_revision/T58/` before staging (same gap prior T-tasks recorded and did not treat as blocking).
- Did not verify the 25th entry in `T21/out/step8/` (one more than the expected 24 cells) — could be an extra file (e.g. a log) rather than a 25th cell dir; the job's per-cell existence check against the 24 named cells is unaffected either way, but this was not looked at directly.
