# T66 — generalize the A5 validator's per-unit correction to MidRise/HighRise and re-score the rebuild

Task doc: this file.
Upstream: `impl/2026-09-20_T65_A5_multiunit_regression_diagnosis.md` (the diagnosis — read `## Verified`
items 1-7 in full before starting), plan `00_REVISION_PLAN.md` Progress Log entry (cz) (the ruling).
Manager: Opus. Status: IN PROGRESS (fresh employee session started 2026-09-20; job `1340682`
submitted and running, awaiting completion for the next employee/manager to score).

## Why this task exists, and what NOT to re-litigate

T65 already found and evidenced the mechanism — **do not re-diagnose it.** Summary you can trust as given:
on 2026-07-13 `eSim_bem_utils_2J/integration.py` was changed, deliberately, to fix a "phantom-peak"
load-shape defect: instead of injecting a household's calibrated equipment/fridge load into only its own
zone, it now broadcasts that load into every dwelling-unit-equivalent zone in the building. This is
**physically correct** for a multi-unit building's whole-building meter. The published/frozen campaign ran
the old, pre-fix, single-zone version and is superseded anyway (author ruling (ay)(b): old campaign numbers
never appear in the manuscript). `step9_validate_full.py`'s SHEU energy gate (A5) was never updated to
match: it compares a whole-building meter reading against a per-dwelling target with **no unit-count
division**, except a hard-coded, OtherDwelling-only correction (`OD_N_UNITS = 7`). That is why every
MidRise/HighRise/OtherDwelling cell fails the gate on the rebuild by 500-8000%, in a ratio that matches each
building's own real unit-equivalent zone count almost exactly (T65 verified this arithmetically for one
exemplar city per archetype).

**Your job is narrower than T65's:** compute the real per-cell unit-equivalent count for every one of the
24 cells (T65 only checked Montreal for HighRise and MidRise), generalize the correction, and re-score.

## What to do

1. **Read `T65`'s `## Verified` items 1, 6 and 7 in full first** — they define exactly what a "dwelling-unit-
   equivalent zone" is (a zone that legitimately carries a baseline `ElectricEquipment` object before the
   injection code neutralizes it, weighted by its own zone multiplier from `eplusout.eio` "Zone
   Information") and how the ratio check is done. Reuse that definition; do not invent a different one.
2. **For each of the 24 cells (4 archetypes x 6 cities), compute its real unit-equivalent count.** The
   cheapest, most direct way: for each cell's `eplusout.eio` (one household's is representative — the
   building geometry is shared across the household sample within a cell), read the "Zone Information"
   rows and sum `Multiplier` over every zone that appears in the pre-neutralization `ElectricEquipment`
   list (same test T65 used). Do this **inside an sbatch job** if it requires reading many `eio` files
   programmatically (24 cells x one file each is small, but parsing `eio` format robustly is easier in
   Python than in shell) — do not attempt a `for` loop over directories on the login node.
3. **Write the corrected validator as a NEW FILE, never edit `step9_validate_full.py` in place**:
   `T66/scripts/step9_validate_full_corrected.py`, a copy with one change — replace the hard-coded
   `OD_N_UNITS`-only correction with a per-archetype, per-city unit-equivalent divisor (from step 2) applied
   to `ac_equip_kwh` and `ac_light_kwh` (and their baseline counterparts, if the baseline carrier is also
   broadcast the same way — check this, do not assume symmetry with the activity/equipment carrier; T65's
   `## WHAT I DID NOT VERIFY` flags that lighting's exact code path was not independently confirmed to
   follow the same broadcast, only inferred from a matching object count). SingleD keeps a divisor of 1
   (no change to its passing rows).
4. **Re-score A5 on the rebuild's staged tree only** (`T48/t21_stage/`, the same tree T48 already built —
   reuse it, do not re-stage). **Two required controls, both against the SAME rebuild data:**
   - **Seen-failing control**: run the ORIGINAL, uncorrected `step9_validate_full.py` on this same staged
     tree and confirm it still reproduces T48's 36/48 FAIL (or close to it — T48's own run is the ground
     truth to reproduce). If you cannot reproduce that FAIL, something about the tree changed since T48 ran
     and you must stop and report, not proceed.
   - **Corrected run**: run `step9_validate_full_corrected.py` on the same tree and report the new pass/fail
     count per cell. Do not report a bare pass count — print each cell's corrected `sheu_pct_equip`/
     `sheu_pct_light` value next to its old (uncorrected) value and the unit-equivalent divisor used, so a
     reader can see exactly what changed and why.
5. **Do not touch the published tree, T21's staged tree contents, T48's original outputs, or
   `step9_validate_full.py` itself.** Read-only on all of those; your new file and your new results are the
   only things you write, under `T66/`.

## What you do NOT do

- Do not re-diagnose the mechanism (T65 already did this — cite it, don't repeat it).
- Do not apply any fix to `integration.py` or re-run any simulation campaign. This task only touches the
  **validator's own arithmetic**, on data that already exists.
- Do not try to make the corrected validator agree with the published tree — the published tree used the
  old, pre-fix single-zone injection and is not a target to match (ruling (ay)(b)).
- If the corrected gate still fails for some cells after the unit-equivalent correction, **report that
  honestly** — do not adjust the divisor to force a PASS. A remaining discrepancy after an evidenced,
  physically-motivated correction is a real finding, not something to tune away.

## Rules (absolute)

- Login node allowed commands only: `sbatch`, `squeue`, `sacct`, `scancel`, `scontrol`, `cd`, `ls`, `scp`,
  `module load`, `mkdir`, single-file `tail`/`head`/`grep`/`wc -l`/`cat`. Any multi-file parse (the 24
  `eio` files, or the full rescoring) goes inside an `sbatch` job.
- tcsh login shell: no `2>&1`, no `2>/dev/null`.
- Interpreter: `/speed-scratch/o_iseri/envs/step4/bin/python`.
- CPU ceiling: 2J stays at or under 32 running CPUs; nothing else is running for 2J right now. `-c 1
  --mem=8G -t 7-00:00:00` is enough.
- Submit and end the turn. Do not poll. Write the JobID and everything found into this doc's Ledger as you
  go — this is the same project where a previous employee lost a turn's findings by not writing to disk
  before pausing; do not repeat that.

## Output

`/speed-scratch/o_iseri/2J_revision/T66/logs/t66_report.txt`: (1) the 24 unit-equivalent counts with how
each was derived, (2) the seen-failing control's reproduction of T48's original FAIL count, (3) the
corrected per-cell equip/light percentages next to the originals and the divisor used, (4) the new pass/
fail tally.

## Ledger

- No job yet. Preparatory read-only checks done on the login node (all single-file
  `cat`/`grep -n`/`head`/`tail`, no restricted commands): read `step9_validate_full.py` in full (335
  lines); confirmed `step9_manifest.csv` layout (`idx,cell,treatment,hh_id,year,idf_path,epw_path`,
  4800 data rows, both `baseline` and `activity` treatments each with their own IDF directory);
  confirmed baseline IDF for `HighRise__Montreal_6A` sample_001/HH106602 has 26 `ElectricEquipment,`
  objects (one per non-corridor zone incl. Office) and 50 `Lights,` objects (i.e. NOT the same
  object-count as equip — flagged for the divisor computation to check zone-set equality itself,
  not assume it); confirmed `eplusout.eio` "Zone Information" field layout (index 1 = zone name,
  index 10 = Zone Multiplier, index 11 = Zone List Multiplier) and manually reproduced T65's 80
  unit-equivalent count for `HighRise__Montreal_6A` from the raw eio rows (G floor 7 apartments x1
  + M floor 8 apartments x8 + T floor 8 apartments x1 + Office x1 = 80). Confirmed `bl_equip_kwh`/
  `bl_light_kwh` in the validator read a single `Zone Electric Equipment/Lights Electricity Energy`
  column (not the whole-building facility meter) — each `hourly_meters.csv` header has exactly one
  such column, so baseline is NOT subject to the broadcast bug and needs no correction (this
  answers the task doc's "check this, do not assume symmetry" instruction: verified, not assumed).
  Confirmed exact T48 invocation from `T48/t48_a5a6.sh` (`step9_validate_full.py --root
  T48/t21_stage --out T48/t21_a5_results.csv`) to replicate for the seen-failing control. Confirmed
  the `OD_N_UNITS = 7` marker and both correction code blocks appear byte-for-byte exactly once in
  `step9_validate_full.py` (verified via `grep -n` + `head`/`tail` extraction, not assumed) before
  writing string-replace logic against them.
- Wrote `T66/scripts/t66_driver.py` locally (scratchpad), scp'd to
  `/speed-scratch/o_iseri/2J_revision/T66/scripts/t66_driver.py`. No local Python available to
  `py_compile` it (checked; not installed) — verified by manual re-read instead of execution.
- **Job submitted: JobID `1340682`** (`sbatch -p ps -c 1 --mem=8G -t 7-00:00:00 --wrap
  "/speed-scratch/o_iseri/envs/step4/bin/python /speed-scratch/o_iseri/2J_revision/T66/scripts/t66_driver.py
  > /speed-scratch/o_iseri/2J_revision/T66/logs/t66_driver_stdout.out"`). Single `squeue -j 1340682`
  check immediately after submission showed state `R` (running) on node `antenna1`, 0:04 elapsed —
  not polled further, per the no-parking rule. Output paths once it finishes:
  `T66/logs/t66_report.txt` (structured report), `T66/logs/t66_driver_stdout.out` (raw stdout/
  traceback if it fails), `T66/logs/t66_control_original.out` and
  `T66/logs/t66_corrected_run.out` (each sub-script's own stdout),
  `T66/t21_a5_results_control.csv` and `T66/t21_a5_results_corrected.csv` (raw per-cell CSVs),
  `T66/scripts/step9_validate_full_corrected.py` (the new corrected script itself).

## Verified

1. `step9_validate_full.py` (335 lines) streams each `hourly_meters.csv`, sums columns per
   `(cell, year, treatment)`, divides by `n_hh`. `ac_equip_col`/`ac_light_col` (activity treatment)
   match the whole-building facility meters `InteriorEquipment:Electricity`/
   `InteriorLights:Electricity`; the OtherDwelling-only correction subtracts
   `(OD_N_UNITS-1)*FRIDGE_KWH_IDF` from `ac_equip_kwh` only, never touches `ac_light_kwh`, and no
   other archetype gets any correction. `bl_equip_col`/`bl_light_col` (baseline treatment) match a
   single `Zone Electric Equipment/Lights Electricity Energy` column, one per file — a per-zone
   quantity, not the facility meter, confirmed via each `hourly_meters.csv` header having exactly
   one such column.
2. `step9_manifest.csv` (T48's staged tree, 4800 rows) has one row per
   `(cell, treatment, hh_id, year)`; `idf_path` points to a real, distinct `Scenario_<year>.idf`
   per household per treatment, with `eplusout.eio` alongside it in the same directory.
3. For `HighRise__Montreal_6A` (sample_001/HH106602, baseline, 2022): 26 `ElectricEquipment,`
   objects across 27 total zones (only one corridor-type zone lacks equipment — object count is 26
   but this maps to 24 UNIQUE target zones per T65's own ratio breakdown, confirming the divisor
   must be computed from the unique zone SET, not the raw object count); 50 `Lights,` objects (a
   different count from equip's 26 — the driver computes equip and light zone sets independently
   and reports whether they match per cell, it does not assume they do). `eplusout.eio` "Zone
   Information" rows read directly: G-floor zones (incl. Office) all Zone List Multiplier=1, M-floor
   zones all =8, T-floor zones all =1 — manual arithmetic from these raw rows reproduces T65's
   reported 80 unit-equivalents for this cell exactly (7 + 64 + 8 + 1 = 80), confirming the
   multiplier field indices used in the parser (1, 10, 11) are correct.
4. `T48/t48_a5a6.sh` step 4 shows the exact original invocation to reproduce for the seen-failing
   control: `step9_validate_full.py --root $T48/t21_stage --out $T48/t21_a5_results.csv`. The driver
   reuses `--root T48/t21_stage` but writes to a NEW path (`T66/t21_a5_results_control.csv`) so
   T48's own output file is never touched.
5. Both `old_equip_block` and `old_light_block` string constants in the driver were checked
   byte-for-byte against the live file via `grep -n` (lines 142-147 and 155-156) plus `head`/`tail`
   extraction — exact match, no whitespace drift, before being used as replace targets.

## Decisions

- Divisor is computed and applied as a genuine per-cell (archetype x city) value from that cell's
  own IDF/eio geometry, not a per-archetype constant — as the task doc asks ("for every one of the
  24 cells"), even though T65 only spot-checked Montreal for two archetypes.
- The corrected script fully replaces the OD-only *subtraction* correction with a general
  *division* by the unit-equivalent count for `ac_equip_kwh`, applied uniformly to all four
  archetypes (SingleD's own computed divisor will be 1.0 since it has a single equipment zone, so
  its passing rows are numerically unaffected — this is arithmetic, not a special case written into
  the code). This is a deliberate departure from the OD block's old subtract-a-fixed-kWh approach:
  T65's own ratio check (Verified item 7 in the T65 doc) shows the current rebuild broadcasts the
  ENTIRE household equipment carrier (not just fridges) into every unit-equivalent zone for
  OtherDwelling too, so a pure division is the physically correct generalization, not just a
  syntactic one. Reasoning recorded here in case the corrected OD numbers look different from the
  old validator's OD numbers even before considering the bug — this is expected and intentional.
- Lights get their OWN computed divisor (`T66_CELL_LIGHT_DIVISOR`), independently derived from the
  `Lights,` object zone set — not assumed equal to the equipment divisor, per the task doc's explicit
  instruction not to assume symmetry. `Verified` item 3 already shows the raw object counts differ
  (26 equip vs 50 light for the one cell spot-checked pre-job), so treating them separately is not
  optional caution, it is required by what was already observed.
- `OD_N_UNITS` and `FRIDGE_KWH_IDF` constants are left defined but unused in the corrected script's
  equip block (not deleted) — smallest-diff principle; they remain harmless dead constants rather
  than being ripped out, since the task doc only asks to replace the correction logic.
- No local `py_compile` available; substituted a manual line-by-line re-read of the driver script
  plus exact byte-for-byte verification of both replace-target blocks against the live cluster file
  before scp'ing it. Documented here as a limitation since the syntax-check skill this project
  normally uses for artifact scripts does not apply to a cluster Python job the same way.

## Next

- **Job `1340682` is running — next agent should check `sacct -j 1340682` and, once COMPLETED,
  read `T66/logs/t66_report.txt`.** Do not resubmit; do not poll repeatedly (check once, and only
  after a reasonable wait — this project's rule is a manager poll, not a live employee wait).
- After the job completes: read `T66/logs/t66_report.txt` (single-file `cat`, allowed on login
  node) for (1) the 24 divisors, (2) whether the control reproduced T48's 12/48 PASS exactly, (3)
  the corrected pass/fail tally and per-cell before/after table. If the control did NOT reproduce
  12/48, stop and report — do not trust the corrected numbers (per the task doc and the driver's own
  built-in warning).
- If the job fails (non-zero exit, or `t66_report.txt` never appears), read
  `T66/logs/t66_driver_stdout.out` for the Python traceback — most likely failure points are the
  two `assert ... count(...) == 1` guards (would mean the live file changed since this read) or a
  missing/malformed `eplusout.eio`/IDF for some cell.

## WHAT I DID NOT VERIFY

- Whether the `Lights,` object zone SET for `HighRise__Montreal_6A` actually differs from the
  `ElectricEquipment,` zone set, or just has a different raw object count for the same zones (e.g.
  2 light objects per zone vs 1 equip object per zone) — the driver computes and logs
  `same_zone_set` per cell but this had not been read from the job's output as of writing this
  entry (job not yet submitted).
- Whether any of the other 23 cells' baseline IDFs/`eplusout.eio` follow the exact same one-field-
  per-line text layout the parser assumes — only `HighRise__Montreal_6A` was hand-verified before
  writing the parser; the driver will report `MISSING_MULT_EQUIP`/`MISSING_MULT_LIGHT` per cell if a
  zone name fails to match between the IDF and the eio, which is the built-in check for this, but
  its output had not been read as of writing this entry.
- Whether `step9_validate_full_corrected.py` actually runs cleanly end to end on the full 4800-row
  manifest (only the string-patch logic and the byte-exact match of the two target blocks were
  verified before submission, not an actual execution).
