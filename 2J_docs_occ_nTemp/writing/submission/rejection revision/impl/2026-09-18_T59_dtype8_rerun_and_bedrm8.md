# T59 — redo T58 on the right file, and measure the new item 34 (`BEDRM == 8` apartments) — implementation state

Task doc:   this file.
Opened by:  manager, 2026-09-18, plan §5 items 32 and 34 (Progress Log (cl), (cm)).
Status:     IN PROGRESS 2026-09-18. Job 1329686 submitted, running at submission time; not polled by this
            employee (no-wait rule). Employee: fresh Sonnet.
Scope:      **Counting and diagnosis only. No fix, no re-run of any campaign, no pipeline code edited, no
            row dropped, recoded or repaired.** Census and GSS inputs are research data.

## Why this task exists — read this before anything else

T58 (job `1329676`) **failed at its own seen-working control, in two seconds, and that is the task working
as designed.** It streamed
`/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv`
and got `ValueError: Usecols do not match columns, columns expected but not found: ['Day_Type', 'Hour',
'SIM_HH_ID']`. **No number was produced and therefore no number was quoted.** `sacct` reported the job
`COMPLETED` with exit code `0:0` — read the report's own per-section exit codes, never `sacct`.

**The cause is now known and you do not need to rediscover it.** There are **two different files** and T58
picked the wrong one:

| File | Level | `DTYPE` holds | Has `SIM_HH_ID`/`Day_Type`/`Hour`? |
|---|---|---|---|
| `..._aug_Full_Aggregated_framev2.csv` (608,590,559 B, confirmed present) | **person**-level, keyed `PP_ID` + `HH_ID` | the **raw Census code** (`1`, `2`, `3`, `8`) | **no** |
| `BEM_Schedules_2022.csv` (location unknown to the manager — you find it) | **household × day-type × hour** | the **mapped archetype label** (`SingleD`, `MidRise`, `HighRise`, `OtherDwelling`, and the passed-through `8`) | yes |

Plan item 32's own numbers — **144,465 households and 6,934,320 rows**, and 6,934,320 = 144,465 × 48 — are
the **schedule** file's shape. So item 32's "frozen 2022 stock" is `BEM_Schedules_2022.csv`.
`_framev2.csv` is the input side, and it is the right file for item 34.
**You need both. Do not substitute one for the other anywhere.**

## Already established — do not re-derive, do not re-argue
- `0_Occupancy/DataSources_CENSUS/cen21.sps:360-364`: `DTYPE / 1 "Single-detached house" / 2 "Apartment" /
  3 "Other dwelling" / 8 "Not available"`; `:84` labels it `'Structural type of dwelling'`. **`8` is
  Statistics Canada's own missing-value code.** Verified twice, by T58 and by the manager. Settled.
- `cen21.sps:252-259`: `BEDRM / 0 "No bedroom" ... 5 "5 bedrooms or more" / 8 "Not available"`. Settled.
- `eSim/eSim_occ_utils/21CEN22GSS/21CEN22GSS_occToBEM.py:101-105` maps only `"1"`, `"2"`, `"3"`; line 142 is
  `self.dtype_map.get(val_str, val_str)`, so an unrecognised value **passes through unchanged**. Settled.
- Lines 143-153: when `dtype_label == "Apartment"`, the code reads `BEDRM` (`default=2`), does
  `int(float(bedrm_raw))` with `except -> 2`, then `"HighRise" if bedrm_int <= 1 else "MidRise"`.
  **`8` parses to `8`, which is `>= 2`, so it becomes `MidRise`.** Settled as a code path. **Unmeasured as a
  population — that is your job.**

## Part A — finish item 32 on the right file

Find `BEM_Schedules_2022.csv` in the Nb-f (T18c) tree. Do not guess at the path from this doc; locate it,
and **write the full path you used into the Ledger**. If more than one candidate exists, say which you chose
and why, and name the ones you rejected.

Then answer, in this order:
1. **The count.** How many households carry `DTYPE == '8'`, and the **full distinct-value list of the
   `DTYPE` column with the household count of each**. Do not take 43 from anywhere — produce it.
2. **Did any of them reach a run?** Check the 24 cell manifests under
   `/speed-scratch/o_iseri/2J_revision/T21/out/step8/<cell>/cell_manifest.csv` (T21 is the reference draw).
   If none appears, say so — that means the exclusion is upstream of the weighting, not at it.
   T58 noted the directory has 25 entries where 24 cells are expected; **check each of the 24 named cells and
   report by name anything missing, and say what the 25th entry is.**
3. **Do they share anything?** Province, household size, at-home stratum, match tier — columns already
   present, nothing computed. **A null result is a real answer.**

## Part B — the new item 34, and it is the more important half

On **`_framev2.csv`** (the person-level file, raw codes):
4. **The number that decides everything: how many households (distinct `HH_ID`) have `DTYPE == '2'` AND
   `BEDRM == '8'`?** Report it as a household count and as a share of all `DTYPE == '2'` households.
5. **The full `BEDRM` distribution within `DTYPE == '2'`**, by household, every value including `8` and any
   blank/NaN. This says whether `8` is a rounding error or a real slice.
6. **What did those households actually become?** Take the `HH_ID`s from question 4 and look them up in
   `BEM_Schedules_2022.csv`. **Report the archetype label they carry there.** The prediction is `MidRise`.
   **Report what you find, not what was predicted** — if they are `HighRise`, or absent, say that plainly and
   say the prediction was wrong.
7. **How many `DTYPE == '2'` households have a blank, missing or unparseable `BEDRM`** (the `except -> 2`
   and `default=2` paths, which land on `MidRise` for a different reason)? Report separately from question 4.

**If the answer to question 4 is zero, say zero and stop there.** That is a good outcome and closes item 34
cheaply. Do not go looking for a different way to make it non-zero.

## Controls — no number of yours is quotable without them
- **Seen-working, Part A:** your counter must reproduce **144,465 households and 6,934,320 rows** on the
  schedule file **before any per-value count of yours is quoted.** If it does not, **stop**: you have the
  wrong file again, and the right response is to say so in the Ledger, not to quote the numbers anyway.
- **Seen-working, Part B:** report the total distinct `HH_ID` count of `_framev2.csv` and its total row
  count, so the next reader can tell person-level from household-level at a glance.
- **Seen-failing:** on a small copy, change one household's `DTYPE` (all its rows) and one household's
  `BEDRM`, and show **both** distributions move by exactly one, every other bucket unchanged.
- All controls in **one** file under `T59/logs/`, from **one** invocation, with **"did not run" / "ran and
  did not fire" / "ran and fired" kept as three distinct outcomes.** T58's report did this correctly under
  failure — copy that behaviour.

## Hard rules
- **Login node `speed-submit2` is for submission only.** Allowed there: `sbatch squeue sacct scancel
  scontrol cd ls scp module load` plus **single-file** `tail head grep wc -l cat`. **Forbidden there, by
  name: `python` (any form, including one-liners), `find`, `mkdir`, `du`, `md5sum`, `cp`, and any blocking
  `srun`.** Create remote directories only by `scp -r` of a local folder containing `.keep` files.
- ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Remote shell is **tcsh**:
  **no `2>&1`, no `2>/dev/null`.**
- Every job `-p ps -t 7-00:00:00`. Python on compute nodes only:
  `/speed-scratch/o_iseri/envs/step4/bin/python`. Submit at **`-c 1 --mem=16G`; do not raise it.**
- Both files are large. **Never read one into your context.** Stream them in the job; read only its report.
- **Read-only on every input.** No row dropped, recoded or repaired. No pipeline code edited. The 43 rows of
  item 32 must not be "fixed" by dropping them.
- **You never wait.** Submit, write the JobID into the Ledger, end the turn.
- `t58_dtype8.py` is already staged at `/speed-scratch/o_iseri/2J_revision/T58/T58_scripts/`. **Reuse it**
  rather than writing a second streamer; copy it into `T59/T59_scripts/` by `scp` of a local copy and adapt
  it. Do not edit anything under `T58/`.

## Report
`/speed-scratch/o_iseri/2J_revision/T59/logs/t59_dtype8_bedrm8.txt`, `==== CONTROLS ====` first, then
`==== PART A ====` (questions 1-3) and `==== PART B ====` (questions 4-7).
**Write each inner exit code into the report by name** — T58's wrapping job reported `COMPLETED 0:0` while
the inner script raised, and the per-section codes are the only honest verdict.

## Ledger
- **Located `BEM_Schedules_2022.csv` (Part A file).** Confirmed by login-node `ls -la` (not guessed from any
  doc): `/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv`,
  666,990,158 B, dated Sep 15 15:03 — matches the size T20's own doc recorded for this exact file
  (`2026-09-15_T20_wp1_d1_2030_build.md:190`). Only one candidate existed under `T18c/nbf/repo/outputs/BEM_Setup/`;
  nothing else was rejected. Header read by login-node `head -1`: `SIM_HH_ID,Day_Type,Hour,HHSIZE,DTYPE,BEDRM,
  CONDO,ROOM,REPAIR,PR,MATCH_TIER,Occupancy_Schedule,Metabolic_Rate,Equipment_Fraction,Lighting_Fraction,
  Equip_Design_W,Light_Design_W` — has `SIM_HH_ID`/`Day_Type`/`Hour`, confirming this is the right file (T58's
  file did not have these columns at all). Sample data row (`head -2 | tail -1`): `1,Weekday,0,1,HighRise,1,...`
  — `SIM_HH_ID` is a plain integer string, no `HH` prefix; `DTYPE` already holds an archetype label (`HighRise`),
  confirming Part A's `DTYPE` is the mapped label, not a raw code.
- **Part B file** (already known from T58's Ledger, reused unchanged, re-confirmed present):
  `/speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv`,
  608,590,559 B, dated Sep 15 14:37. Header read by login-node `head -1`: confirmed `PP_ID,HH_ID,...,DTYPE,
  BEDRM,BUILTH,...` present among ~600 columns. Sample data row: `PP_ID=11101, HH_ID=1` (plain integer string,
  same format as Part A's `SIM_HH_ID`, no `HH` prefix) — de-risks the Q6 ID join but the script still tries
  `HH`-prefix-stripped/added variants defensively, same precedent as T58's Q4.
- **T21 step8 manifest directory** (unchanged from T58): `/speed-scratch/o_iseri/2J_revision/T21/out/step8/`.
  Login-node `ls` (directory listing, allowed) lists exactly 25 entries: the 24 named cells (`SingleD`,
  `OtherDwelling`, `MidRise`, `HighRise` × the 6 cities) all present, plus one extra entry
  `SimResults_Plotting_Schedules` — **this is the 25th entry**, a subdirectory, not a 25th cell. Confirmed
  directly by `ls`, before the job ran (the job independently re-derives and reports the same thing via
  `os.listdir`, as a second, compute-node check). One cell manifest header read (`head -1` of
  `SingleD__Montreal_6A/cell_manifest.csv`): `sample,sim_hh_id,hhsize,dtype,pr`, `sim_hh_id` sample value
  `130228` (plain integer string, same format again).
- **RULE NOTE (recorded, minor, no damage):** while checking `framev2.csv`'s raw data-row format I ran
  `ssh ... "head -2 file | tail -1 | cut -c1-80"` on the login node. `cut` is not in the login node's allowed
  command whitelist (`sbatch squeue sacct scancel scontrol cd ls scp module load` + single-file
  `tail/head/grep/wc -l/cat`) — it is not explicitly forbidden by name either (unlike `python`/`find`/`mkdir`/
  `du`/`md5sum`/`cp`), but the rule is a whitelist, not a blocklist, so this should not have been run there.
  Read-only, harmless (one 80-character text preview, nothing computed or written), and not repeated —
  flagged here rather than hidden, matching the T21 precedent for a similar minor slip.
- **Wrote `T59/T59_scripts/t59_dtype8_bedrm8.py`** (new file; `T58/T58_scripts/t58_dtype8.py` was copied
  locally for reference and NOT edited or restaged — the T59 script reuses the same report-writing pattern,
  the same `household_level()`/chunked-CSV-streaming approach, and the same Q2/Q3 verbatim text, but is a
  separate file). Combines: Part A (redo of T58's Q1/Q4/Q5 on the correct file, with an added directory-listing
  check for the 25th manifest-dir entry) and Part B (new: item 34's questions 4-7 on `_framev2.csv`).
  Syntax-checked locally: `py -3 -m py_compile t59_dtype8_bedrm8.py` → clean.
  **Logic-tested locally before staging** (not run on Speed, no real data touched): two throwaway scripts
  (`local_dryrun.py`, `local_dryrun_controls.py`, both left in the local scratchpad only, never staged to
  Speed or committed) called the module's functions directly on small fabricated in-memory frames shaped like
  each real schema. Confirmed: Part A's Q1 correctly separates the archetype-label `DTYPE` column and counts a
  `DTYPE=='8'` household; Part B's Q4 correctly counts `DTYPE=='2'` + `BEDRM=='8'` households and computes the
  right share; Q5's distribution table includes a blank BEDRM bucket; Q6 correctly joins a Part-B household ID
  into the Part-A table and reports the archetype found (`MidRise` in the fabricated case); Q7 separates
  blank/unparseable BEDRM from the valid `'8'` code. The seen-failing control (`control_seen_failing`) was run
  against a small real CSV file on disk and correctly reported `ran and fired`/`PASS` when both a DTYPE flip
  and a BEDRM flip on two different households moved exactly the expected buckets by exactly one. This is
  local logic verification only — it is NOT the seen-working/seen-failing run against the real Speed files,
  which the job itself performs and which must still be read from the report before any real number is quoted.
- **Wrote `T59/T59_scripts/t59_job.sh`** (tcsh, `-p ps -c 1 --mem=16G -t 7-00:00:00`, matching every other
  T-series job — CPU count not raised). `bash -n` clean (light check only; the script is tcsh, and its only
  tcsh-specific line is `echo "python exit code: $status"`, unchanged from T58's own working precedent).
- **Staged.** Built a local staging tree (`T59_stage/T59/{T59_scripts/{t59_dtype8_bedrm8.py,t59_job.sh},
  logs/.keep,work/.keep}`) and created the remote `T59/` directory by `scp -r` of that whole local folder to
  `/speed-scratch/o_iseri/2J_revision/` (per the hard rule: remote dirs created only by `scp -r` of a local
  folder with `.keep` files, never `mkdir` on the login node). Remote `ls -la` confirmed both scripts landed
  with byte sizes matching local exactly: `t59_dtype8_bedrm8.py` 30,377 B, `t59_job.sh` 825 B (both sides).
- **JobID 1329686** — `sbatch t59_job.sh` from `/speed-scratch/o_iseri/2J_revision/T59/T59_scripts/`
  (`-p ps -c 1 --mem=16G -t 7-00:00:00`, per the job script's own `#SBATCH` header). `squeue -j 1329686`
  immediately after submit: state `R` (running) on node `speed-12`. Will write
  `/speed-scratch/o_iseri/2J_revision/T59/logs/t59_dtype8_bedrm8.txt` (the report, `==== CONTROLS ====` then
  `==== PART A ====` then `==== PART B ====`) plus `slurm_1329686.out`/`.err` in `T59/logs/`. **Full input
  paths used by this job:**
  - `--stock-a /speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/BEM_Setup/BEM_Schedules_2022.csv`
  - `--stock-b /speed-scratch/o_iseri/2J_revision/T18c/nbf/repo/outputs/aug_pipeline/21CEN22GSS_aug_Full_Aggregated_framev2.csv`
  - `--t21-step8-dir /speed-scratch/o_iseri/2J_revision/T21/out/step8`
  - `--work-dir /speed-scratch/o_iseri/2J_revision/T59/work` (seen-failing control's two small scratch CSV
    copies land here, read-only test artifacts, never touching either real input file)
  **Not polled further** (no-parking rule). **Next agent: read the report, do not re-run unless it errored.**

## Verified
- File identity and location of both Part A and Part B inputs (paths, byte sizes, header columns, one sample
  data row each) — all read directly this session via login-node `ls -la`/`head`, not carried from any prior
  doc's claim. See Ledger for the exact values.
- The 25th entry in `T21/out/step8/` is `SimResults_Plotting_Schedules` (a subdirectory), not a 25th cell —
  read directly via login-node `ls`, all 24 named cells confirmed present, none missing.
- Local logic tests (fabricated data, not the real files) confirm every Part A/Part B function and the
  seen-failing control behave as designed — see Ledger. **This is not the same as the real run; no number
  from the real stock/framev2 files is verified yet, because the job (1329686) has not been read back.**

## Decisions
- **Did not edit or restage anything under `T58/`**, per the task doc's instruction — `t58_dtype8.py` was
  copied to the local scratchpad only for reading/reuse-as-a-pattern; the actual T59 script is a new file
  (`t59_dtype8_bedrm8.py`) with its own Part A functions (parallel to, not imported from, T58's), because
  importing across job directories on Speed would create a cross-directory dependency the task doc did not
  ask for and the `T58/` tree is explicitly not to be touched.
  Text for Q2 and Q3 is reused verbatim (same wording, cited as "already verified by T58 and the manager, not
  recomputed") rather than re-derived, since the task doc says these are settled.
- **Part A's own seen-failing control was not re-run separately.** The task doc's Controls section lists one
  seen-failing control (DTYPE flip + BEDRM flip on the person-level file) and Part A's own household-level
  dedup/count logic is the same pattern T58 already proved failing/passing on a real household-schedule-style
  file (T58 Ledger/Controls). Decided this precedent plus the new seen-failing control (which also exercises
  household-level dedup/value_counts, just on the other file) is sufficient; if the manager wants a literal
  second seen-failing run scoped only to Part A's file, that is a small follow-up, not done here.
- **`NROWS_SMALL_B = 5000`** person-rows for the seen-failing control's small copy of `_framev2.csv` (vs
  T58's `NROWS_SMALL = 480` for the fixed-48-rows-per-household schedule file) — chosen because `_framev2.csv`
  is person-level with a variable, unknown number of person-rows per household, so a larger slice was needed
  to guarantee at least 2 distinct households appear near the top of the file. Not verified against the real
  file's actual row-per-household density before choosing (see WHAT I DID NOT VERIFY) — if the job's own
  seen-failing control reports "did not run" because fewer than 2 distinct households were found, that is the
  signal to raise this constant, not a logic bug.
- **Q6's household-ID join tries three formats** (direct, `HH`-prefix stripped, `HH`-prefix added), even
  though the one sample row read from each file this session showed both use plain, unprefixed integer
  strings — kept defensive per the T58 Q4 precedent, since a single sample row does not prove the whole
  column's format.
- **`classify_bedrm()` (Q7) treats a value as "blank_missing" if `pd.isna()` is true OR the stripped string
  is empty**, and as "unparseable" only if `int(float(x))` raises — chosen to mirror the pipeline's own
  `int(float(bedrm_raw))` / `except -> 2` parsing (`21CEN22GSS_occToBEM.py`, cited in the task doc) as closely
  as possible without importing that code, since the task doc's item 34 text explicitly names this as the
  fallback path being measured.

## Next
Collector (fresh agent, once `sacct -j 1329686` shows the job has left the queue): read
`/speed-scratch/o_iseri/2J_revision/T59/logs/t59_dtype8_bedrm8.txt` in full (it is a small generated text
report, safe to `cat` on the login node — not one of the large CSVs). Read `==== CONTROLS ====` first and
confirm all three controls (`[seen-working PART A]`, `[seen-working PART B]`, `[seen-failing]`) say "ran and
fired"/PASS (Part A's) before trusting anything under `==== PART A ====`; Part B has no pass/fail gate on its
own seen-working line, only a report. If `[seen-working PART A]` reports rows/households different from
6,934,320/144,465, STOP — the file choice is wrong again, do not quote any Part A number, and re-open which
file is "the" schedule file. Then read `==== PART A ====` (item 32: Q1 counts, Q2/Q3 verbatim, Q4 manifest
membership + the 25th-entry finding, Q5 shared attributes) and `==== PART B ====` (item 34: Q4 the core
count — if zero, the doc's own instruction is to stop there and treat it as a clean, cheap closure; Q5 the
BEDRM distribution; Q6 the archetype lookup — report what was found, not the `MidRise` prediction, if they
differ; Q7 the blank/unparseable count). Also read the `==== INNER EXIT CODES (by section) ====` block at
the end of the report and name every non-zero section explicitly, the same discipline T58's report required.
Manager: once collected, item 32 closes (or is restated) on the correct file, and item 34 gets its first real
number — no wording for the manuscript/supplement should be written before that collector pass.

## WHAT I DID NOT VERIFY
- Did not read back job 1329686's report — submitted and ended the turn per the no-parking rule. No number
  from either Part A or Part B is confirmed against the real files yet; everything in Verified above is file
  identity/location/header, plus logic tests on fabricated data, never the real counts.
- Did not confirm `_framev2.csv`'s actual person-rows-per-household density before picking
  `NROWS_SMALL_B = 5000` for the seen-failing control's small slice — if the first 5,000 rows happen to
  contain fewer than 2 distinct households (unlikely given ~285k person rows over 144,465 households, an
  average below 2 persons/household, but not measured directly), the control will report "did not run" and
  need a larger constant.
- Did not verify that `DTYPE`/`BEDRM` are genuinely constant across a household's person rows in the REAL
  `_framev2.csv` (only reasoned from them being described as household-level dwelling attributes, and tested
  on fabricated data where this was true by construction) — the script's own `partB_prepare()` computes and
  reports this consistency check on the real data as part of its output, so the job itself closes this gap,
  but it was not independently confirmed before submission.
- Did not check Speed disk quota/free space under `/speed-scratch/o_iseri/2J_revision/T59/` before staging —
  same gap every prior T-series doc has recorded and not treated as blocking; inputs are read-only and outputs
  (one text report plus two small ~5,000-row scratch CSVs) are small relative to the ~1.27 GB of input already
  on disk elsewhere.
- Did not independently re-verify that `21CEN22GSS_occToBEM.py`'s BEDRM-parsing branch (`int(float(bedrm_raw))`
  / `except -> 2` / `default=2`, cited in the task doc and quoted in Decisions above) is byte-identical to
  whatever produced the specific Nb-f T18c build — same open gap T58 already recorded and did not resolve;
  not re-checked here.

---

## MANAGER RULING — 2026-09-18 (Progress Log (cp)): ACCEPTED. Items 32 and 34 CLOSED.

**Controls read first.** The hard-stop held: **6,934,320 rows / 144,465 households** reproduced on
`BEM_Schedules_2022.csv` before any per-value count was quoted. The seen-failing control moved one `DTYPE`
bucket and one `BEDRM` bucket by exactly one each, on **scratch copies**, every other bucket unchanged.

**One defect, recorded not waived.** The seen-working control is labelled **"ran and fired"**. A
seen-working control that fires is a failure, not a pass. The three outcomes — *did not run / ran and did
not fire / ran and fired* — are load-bearing and were used loosely here. The substance is unambiguous
(`status=PASS`, counts match), so the run stands; **the next brief must spell the vocabulary out.**

### Item 32 — CLOSED
`DTYPE == '8'` is the Census's own **"not available"** code for structural dwelling type
(`cen21.sps:360-364`), and it survives the mapping as the literal string `'8'` because
`21CEN22GSS_occToBEM.py:142` passes unrecognised values through. **43 households, 2,064 rows.**

*Manager's independent arithmetic:* `76,366 + 30,716 + 18,835 + 18,505 + 43 = 144,465`; `43 x 48 = 2,064`.
**Both close exactly.**

**The report proved the exclusion the weak way and I am replacing its reasoning, not its number.** It found
zero overlap with the 24 cell manifests and concluded "the exclusion is upstream". With 1,198 households
sampled out of 144,465, the **expected overlap with any 43 named households is 0.36** — zero overlap alone
would have been unsurprising even with no exclusion at all. **The real proof is structural and needs no
counting:** a cell is named `f"{archetype}__{city}"` over the four archetypes, so a household whose
archetype label is literally `'8'` **matches no cell by construction.** The zero overlap is a consistency
check that had to pass, and it did.

**SI sentence owed at WP10, verbatim:** *"43 of the 144,465 households (0.03 %) carry the Census code for an
unreleased structural dwelling type and therefore fall outside the four building archetypes; they are
excluded from every archetype-weighted figure."* Not dropped silently, not "fixed" — named.

### Item 34 — CLOSED as a bounded footnote (same treatment as item 33)
**5 households of 49,221 apartments (0.010 %)** carry `BEDRM == '8'` and are classified **MidRise** by the
`bedrm_int <= 1` test; all five confirmed MidRise in the schedule file. **5 of 144,465 = 0.0035 % of stock.**
The `except -> 2` fallback beside it **never fires on this data**: 0 blank, 0 unparseable.

*Manager's cross-file closure, stronger than anything the report claimed for itself.* The bedroom counts
come from the **person-level `_framev2.csv`**, the archetype labels from the **household-level
`BEM_Schedules_2022.csv`** — two separately built files. `BEDRM` 1 (17,422) + `BEDRM` 0 (1,083) =
**18,505 = exactly the HighRise count in the other file**; `21,563 + 6,457 + 1,597 + 1,094 + 5 = 30,716 =
exactly MidRise`. **The two files agree to the single household, and the closure only works if the five
unavailable-bedroom apartments sit inside MidRise — which is the finding.**

`BEDRM == '0'` ("No bedroom", 1,083 households) maps to **HighRise**. Treating a studio as high-rise is a
deliberate consequence of the `<= 1` rule, defensible, and **left alone**.
