# T72 — fix T30/T55/T61's V3 checker indexing bug and re-run V3 on the full 48-cell grid

Task doc:   this file
Status:     IN PROGRESS — job submitted, not yet collected

## Background (read this first, do not re-derive it — it is already proven)

T61 (job `1329796`, `impl/2026-09-18_T61_V3_rerun_idd.md`) re-ran V3 (`t30_check.py::v3_one_profile_per_cell`)
after fixing T55's IDD-path crash. It came back `V3=FAIL`, 0/48 cells passing `pass_v3_one_profile`
(every household showed as a DISTINCT occupancy schedule). All four of T61's controls fired correctly
(A and B seen-failing on a shadow copy, C seen-working/unmodified on the real tree, D crash-vs-verdict),
so the checker itself did not crash — it ran cleanly and produced this FAIL on every one of the 48 cells.

**The manager has already found the almost-certain cause by hand, and confirmed it against two real
households in the real tree — you are NOT diagnosing from scratch, you are fixing a known bug and
proving the fix on the full grid.**

The bug is in `t30_check.py:248`:
```python
fields = tuple(occ[0].obj[1:])  # drop Name (index 0)
```
This comment is wrong about which index the Name is at. `integration.py:1448` builds the eppy object as:
```python
occ_obj.obj = ["Schedule:Compact"] + create_compact_schedule(occ_sch_name, "Fraction", occ_dict)
```
and `create_compact_schedule()` (`integration.py:550`) returns `fields = [name, type_limit, "Through: 12/31", ...]`
as its FIRST element. So `occ_obj.obj[0]` is the literal eppy object-type keyword string `"Schedule:Compact"`
(constant, contributes nothing), and `occ_obj.obj[1]` is the actual per-household Name
(`Occ_Sch_HH_<hh_id>`, which necessarily differs by design — IDF requires unique object names). The checker's
`obj[1:]` slice drops only the constant type keyword and KEEPS the unique Name string inside the hashed
tuple, so every household hashes to a different value regardless of whether the real VALUE fields (the
24 weekday + 24 weekend fractions) are actually identical. **The correct slice is `obj[2:]`.**

**Manager's own hand-check, already done, already conclusive:** pulled the real injected IDFs for two
different households in the same real cell (`T30/out/SingleD__Toronto_5A__2022/sample_001_HH32811/avg_2022/Scenario_avg_2022.idf`
and `.../sample_002_HH18326/avg_2022/Scenario_avg_2022.idf`) and diffed their `Occ_Sch_HH_*` blocks by
eye. Every field after the Name line — schedule type limit, `Through: 12/31`, every `For:`/`Until:`/value
line for all 24 weekday hours and the weekend hours read — is byte-identical between the two households.
Only the Name line differs (`Occ_Sch_HH_32811` vs `Occ_Sch_HH_18326`). **This means T30's actual averaging
design worked correctly; the checker's index bug is what produced the false FAIL, not a real defect in the
average-profile arm.** Your job is to make this rigorous and complete across the whole grid, not just 2
households in 1 cell.

## What to do

1. **Read `t30_check.py::v3_one_profile_per_cell` yourself** (`T30/T30_scripts/t30_check.py:227-260`) and
   confirm in your own words that `obj[1:]` vs `obj[2:]` is the only change needed — do not change
   `pass_design_levels_differ`'s logic, it already passes (48/48) and is untouched by this bug.
2. **Do not modify `T30/out/` or any real run data.** This is a checker-only fix.
3. Copy `t30_check.py` to a new script (do not overwrite the original — keep it as the historical record
   of the bug), e.g. `T72/T72_scripts/t72_v3_fixed.py`, with the one-line fix `obj[1:]` → `obj[2:]`.
4. **Controls, all required, all three-outcome labelled (RAN AND FIRED / RAN, DID NOT FIRE / DID NOT RUN):**
   - **Control OLD-BUG (seen-failing, reproduces T61):** run the UNFIXED `obj[1:]` logic against the real,
     untouched `T30/out/` tree and confirm it still gives 0/48 `pass_v3_one_profile` — this proves your
     fixed script and T61's script are looking at the same underlying data, not a different tree.
   - **Control NEW-FIX (the actual task):** run the FIXED `obj[2:]` logic against the same real, untouched
     `T30/out/` tree, full 48-cell grid (24 cells x 2 years).
   - **Control BROKEN-SHADOW (seen-failing for the fix itself):** reuse T61's shadow-tree approach (or build
     your own small shadow copy of 1-2 cells with a household's occupancy VALUE fields deliberately altered,
     not just the Name) to prove the FIXED checker still correctly detects a real violation when one exists
     — i.e. the fix must not have become a checker that always passes no matter what.
   - **Design-levels control:** confirm `pass_design_levels_differ` is unchanged and still 48/48 PASS (it
     never used the buggy slice, so this should be identical to T61's result — state that, don't just assume it).
5. Hand-verify at least 2 more (cell, household-pair) combinations by direct field-by-field comparison
   printed into the report (not just the hash), the same way the manager did for `SingleD__Toronto_5A__2022`
   — pick 2 different cells (e.g. one MidRise, one HighRise, since those have the most zones/complexity).
6. Write `T72/logs/t72_v3_fixed_report.txt` with: the bug explanation in your own words, all controls with
   their three-outcome labels, the full 48-row V3 result table (both criteria), the hand-verified field
   comparisons, and a final `VERDICT: V3=<PASS|FAIL>` line plus an inner exit-code table (crashed vs ran).
7. **Submit via `sbatch`, do not wait, do not poll.** Write the JobID into this file's Ledger section below,
   then end your turn. The manager collects when `sacct` shows COMPLETED.

## Ledger

- **JobID `1341254`** — `sbatch -p ps -t 7-00:00:00 -c 1 --mem=16G`, submitted 2026-09-21, confirmed `squeue` state `R` (running) immediately after submit. Script: `/speed-scratch/o_iseri/2J_revision/T72/T72_scripts/t72_v3_fixed.sh`, which runs `t72_report.py` with `ENERGYPLUS_DIR`/`IDD_FILE` exported (same values T61 confirmed correct: `/speed-scratch/o_iseri/ep_wrappers/Energy+.idd`). State/exit code: **not yet known — not polled, per NO PARKING.** Manager collects via `sacct -j 1341254` and by reading the report file below.
- Load-bearing output (read THIS for the verdict, not the job's own `.out`/`.err`): `/speed-scratch/o_iseri/2J_revision/T72/logs/t72_v3_fixed_report.txt`.
- Diagnostic only: `/speed-scratch/o_iseri/2J_revision/T72/logs/t72_v3_1341254.out` / `.err`.

## Verified

Nothing from this run yet — job not collected. What was verified **before submission** (read-only, login-node-safe commands and local file reads, no python run):

- Confirmed the bug at `T30/T30_scripts/t30_check.py:242` matches the brief exactly (read the file). `pass_design_levels_differ` (lines 244-253) never reads `occ[0].obj` — it reads `ELECTRICEQUIPMENT.Design_Level` / `LIGHTS.Lighting_Level` directly — so it is untouched by this bug; confirmed by reading the code, not assumed.
- Pulled T61's own report (`T61/logs/t61_v3_report.txt`, job `1329796`) by `scp` and read it in full: real-tree OLD-BUG result was `pass_v3_one_profile: 0/48`, `pass_design_levels_differ: 48/48`, all four of T61's controls RAN AND FIRED. This is the exact number my own CONTROL OLD-BUG is built to reproduce.
- Confirmed real household IDFs exist at the two hand-verify cells I picked (`MidRise__Toronto_5A__2022/sample_001_HH126086` and `sample_002_HH94459`; `HighRise__Vancouver_5C__2030/sample_001_HH82981` and `sample_002_HH5149`) via `ls` on the login node and their `cell_manifest.csv` rows.
- `py_compile`-clean locally for both `t72_v3_fixed.py` and `t72_report.py` before upload (no cluster python run needed for this check).

## Decisions

- **Reused T61's real, unmodified `T30/T30_scripts/t30_check.py` directly as the OLD-BUG control's source**, rather than hand-copying the old logic into a second new file — this guarantees CONTROL OLD-BUG and T61 are running the literal same code, not a transcription of it, which is the strongest form of "same underlying data" proof the brief asks for.
- `t72_v3_fixed.py` is a **full copy** of `t30_check.py` (all of V0-V5, not just V3) with only the one line changed, per the brief's instruction "copy `t30_check.py` to a new script... with the one-line fix" — kept the whole file rather than trimming it to just V3, so it stays a faithful historical-style copy and is directly diffable against the original.
- **BROKEN-SHADOW control** uses a single cell (`SingleD__Toronto_5A__2022`, 3 households) rather than 2, since the brief allows "1-2 cells" and one deliberately-broken VALUE field is enough to prove the fixed checker still detects a real violation while also exercising all 47 other (symlinked) grid entries under the fixed logic in the same run.
- **Hand-verify pairs**: chose `MidRise__Toronto_5A__2022` and `HighRise__Vancouver_5C__2030` (one MidRise, one HighRise, one 2022 one 2030 for extra coverage) — picked the first two households in each cell's manifest for simplicity; not cherry-picked for any other reason.
- Job requests `-c 1 --mem=16G`, matching T61's own resource request for the same class of work (V3-only, no full V0-V5 sweep, no heavy sim data read beyond IDF text parsing).

## Next

Manager: run `sacct -j 1341254 --format=JobID,State,ExitCode,Elapsed` and, once `COMPLETED`, read `/speed-scratch/o_iseri/2J_revision/T72/logs/t72_v3_fixed_report.txt` in full for: the VERDICT line, all four controls' three-outcome labels (OLD-BUG, NEW-FIX, BROKEN-SHADOW, design-levels), the full 48-row table, and the two hand-verified field comparisons. If `NEW-FIX` comes back `RAN AND DID NOT FIRE` (i.e. `pass_v3_one_profile` 48/48) and both hand-verified pairs show zero mismatches, that closes V3 on the T30 averaged arm per the manager's already-stated hand-check hypothesis — but that closure call is the manager's to make from the report, not asserted here.

## WHAT I DID NOT VERIFY

- Did not wait for or poll job `1341254` — do not know its actual exit code, whether it crashed, or what `pass_v3_one_profile`/`pass_design_levels_differ` counts it measured. Everything about the ACTUAL result is unverified by me; only the setup (code correctness, IDD provenance pattern reused from T61, file existence for hand-verify targets) was checked before submission.
- Did not independently re-derive T61's 0/48 / 48/48 numbers by running anything myself — took them from reading T61's own report file, which I copied and read in full (not summarized secondhand).
- Did not check whether `code_step8/repo` or `T21/sched_activity` changed since T61 ran (2026-09-18) in any way that could affect `_import_step8` or IDD resolution — reused the same resolution path T61 already proved correct, but did not re-confirm the IDD file's byte size/hash myself this time (T61 already did: 4,448,311 bytes, first line `!IDD_Version 24.2.0`; my script re-prints the first line as its own provenance check, which will surface any drift).
- Did not test the BROKEN-SHADOW or hand-verify code paths against real data before submitting (no python execution allowed on the login node) — correctness rests on `py_compile` (syntax only) plus close structural reuse of T61's already-proven shadow-grid/break-field functions, not an actual dry run.
