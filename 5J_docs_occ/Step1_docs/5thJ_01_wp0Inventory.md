# Step 1 — WP0: inventory of what 4J already built

### 5J occupancy-aware surrogate. Implementation specification.
#### Parent: `../5thJ_00_Occupancy_Surrogate_Pipeline.md` Step 1. Validation: `5thJ_01_wp0Inventory_val.md`

Written 2026-09-28. Edit in place; never fork a copy. Per-task state goes in `impl/<YYYY-MM-DD>_<task>.md`.

---

## STATUS

✅ DONE 2026-09-28 night except the UK line (WAITING ON AUTHOR); see the Progress Log below.
(Original line:) ⬜ NOT STARTED at the time of writing. Read-only step: it creates no data, runs nothing on Speed, and
changes no 4J file. It produces one inventory (`outputs_step1/wp0_inventory.md` and `.json`) that
Steps 2 to 7 cite instead of re-searching 4J.

## AIM

Know exactly which 4J inputs and tools 5J can reuse, where they are, what state they are in, and what
each one costs to run, before the campaign is designed (Step 2). The answer is a list of paths, counts,
checksums and function signatures, each one read from disk, never recalled.

## WHAT IS ALREADY DECIDED — DO NOT RELITIGATE

| Decision | Where |
|---|---|
| Form B4 surrogate, sole author, HETUS Spain 2009-10, UK 2014-15, Italy 2013-14 | Parent, Step 0 |
| All three countries stay in (UK after the author's ruling) | Parent O-1, 2026-09-28 |
| Only the author's own material: 4J tools, TABULA, ERA5, OpenUBEM; no 2J generator, no 1J to 3J runs, no CENTUS model | Parent, Step 0 |
| Novelty check closed on Li 2021's abstract; full-text re-check at Step 8 | Parent O-2, 2026-09-28 |
| EnergyPlus 23.1 through OpenUBEM, on Speed, `sbatch` only | Overview, scope table |

## 🔴 THE UK RULE (UKDS End User Licence v16.00, clause 5)

No online or generative AI tool may be used "in connection with" the UK data without written UKDS
permission. So for this step and every later one:

* The assistant (manager or employee) **never opens** a UK data file: the raw UK-TUS files, the 4J
  parsed UK episodes (`episodes_uk.parquet`), the UK acquisition manifest, UK crosswalk value files,
  any 4J output that pools UK rows with other countries, and any schedule, IDF, EnergyPlus output or
  model weight built from UK diaries.
* It may read **code**, **documentation text** (markdown, codebooks published by UKDS, papers), **file
  names and sizes** (`ls -l`), UK **weather** files and UK **TABULA** parameters (neither is UKDS data).
* UK row counts and checksums are produced by the **author**, running a line this doc gives, and pasted
  into the impl doc by the author.

When unsure whether a file carries UK rows, treat it as UK and list it by name and size only.

## INPUTS TO LOCATE (the five inventory items)

### A. HETUS diary files (Spain, Italy by the employee; UK by the author)

Known locations (listed 2026-09-28, names only):
* Spain: `GSSCanada\_local_runs\4J\raw\spain\` (`datos_emptiem0910.zip`, `unpacked\DIARIO1.TXT`,
  `DIARIO2.TXT`, `CINDIV.TXT`, `DHOGAR.TXT`, `MHOGAR.TXT`, `HTR1.TXT`, `HTR2.TXT`, record layouts).
* Italy: `GSSCanada\_local_runs\4J\raw\italy\unpacked\` (`MICRODATI\`, `METADATI\`, `!Leggimi.html`).
* UK: `GSSCanada\_local_runs\4J\raw\uk\` (zip and `unpacked\UK-TUS\`): **names and sizes only.**
* 4J parsed episodes: `4J_docs_occ/Step1_docs/outputs_step1/episodes_{spain,italy}.parquet` (and
  `episodes_uk.parquet`: name and size only).
* The copies on Speed that 4J used (`/speed-scratch/o_iseri/...`): located by `ls` over ssh only.

Record per file: path, size in bytes, md5, row count (lines for text, rows for parquet read on Speed
or from the 4J gate report, whichever the 4J Step 1 doc names as the reference), and the matching
value in the 4J record (`4J_docs_occ/Step1_docs/4thJ_01_corpusAcquisition.md`, gate reports).
A mismatch with 4J is a finding, not a fix.

**Author, locally, for the UK** (one line, Git Bash; the output stays with the author and is pasted into
the impl doc by the author, never read by the assistant from the data):
`cd "/c/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J/raw/uk" ; md5sum *.zip > uk_md5_5J.txt ; ls -l unpacked/UK-TUS >> uk_md5_5J.txt`

### B. Diary to schedule (4J Steps 7 and 9)

* `4J_docs_occ/tools/4thJ_step7_schedules.py`: `rotate_to_midnight` (line 120), `year_day_types`,
  `assemble_person_year`, `household_year` (line 321), `idf_objects`, `load_households`, `build` (line
  484). Record each signature, the time step it writes, and the diary origin hour constant per country.
* `4thJ_step7_chaining.py` and `4thJ_step8_chaining.py`: the day-to-year chaining rule as ruled in 4J
  (quote the 4J doc line that rules it).
* `4thJ_step9_mapping.py` (activity to appliance, lighting and hot water) and `4thJ_step9_trigger.py`:
  which activity codes drive which load, and whether secondary activity is used (lesson 13).
* `4thJ_step7_indoor.py`: what it produces and whether 5J needs it.
* Which 4J schedule outputs exist on disk for Spain and Italy (names, sizes, one opened for Spain to
  read its column set and length).

### C. Buildings (4J Step 8)

* `4thJ_step8_tabula.py` and `4thJ_step8_tabula_reference.py`: archetypes per country (es, uk, it),
  and for each the parameters held (U-values, window share, air change rate, floor area, storeys).
* `4thJ_step8_idf.py`: how an archetype IDF is built, which parameters are function arguments (and so
  can be varied by a Latin hypercube in Step 2) and which are hard-coded; the output meters and
  variables it requests.
* The 4J record "88 built, 0 severe": re-read from its source line.

### D. Weather (4J Steps 8 and 10)

* `4thJ_step8_weather.py`, `4thJ_step10_weather_year.py`: which cities and years exist as EPW files,
  where, and whether they are ERA5 actual years; the diary-year weather used in 4J per country.

### E. Campaign runner (4J Step 10, OpenUBEM)

* `4thJ_step10_paired.py`, `4thJ_step10_nocore_campaign.py`, `4thJ_step10_nocore_preflight.py`,
  `4thJ_step8_scenario.py` (cache key), `4thJ_step10_eu08_driver.py`, `4thJ_run_madrid_stock_campaign.sh`:
  the entry point, the arguments, the EnergyPlus binary path and version it records, the build hash, one
  working directory per run or not (lesson 8), what it writes per run and how big.
* Measured time per annual run in 4J, quoted with its source line (4J Step 8 or 10 docs, job logs).
* The OpenUBEM repository location and the commit or version 4J pinned.

### F. Cluster facts needed by Step 2 (listing only)

* Paths on Speed where 4J assets sit (`ls`), the EnergyPlus install used there, the Python environment
  4J jobs activated. No `quota`, `du` or `python` on the login node; the scratch fill level is taken
  from the last 1J record (9.3 T of 10 T on 2026-09-25, `1J_docs_occ/Prompts/1J_manager_prompt_RESUME.md`),
  marked as not re-measured.

## OUTPUTS

| File | What |
|---|---|
| `outputs_step1/wp0_inventory.md` | One section per item A to F: paths, sizes, md5s, counts, signatures, each with the command or file line it was read from |
| `outputs_step1/wp0_inventory.json` | The same facts, machine-readable, for Step 2 scripts |
| `impl/2026-09-28_wp0_inventory.md` | Task state (ledger, verified, decisions, next, not verified) |

Nothing is written under `GSSCanada\_5J_data\` in this step.

## DONE WHEN

All five inventory items have an entry read from disk; the UK entry is either the author's pasted
line or marked `WAITING ON AUTHOR`; the manager has re-derived one number per item (validation doc,
section 6); the parent checklist Step 1 boxes are ticked from the inventory, not from the employee's
word.

## PROGRESS LOG (append-only)
- 2026-09-28 (manager): doc written; O-2 closed by the author the same evening. Next: employee run
  (task doc `impl/2026-09-28_wp0_inventory_TASK.md`).
- 2026-09-28 night (manager): employee run DONE (65 facts, 13 findings, 9 flags for Step 2); manager
  re-derivation DONE (A to E equal; gates 1.3 and 3.1 PASS, each seen failing). UK line WAITING ON AUTHOR.
  Step 1 closed except the UK line. Next: Step 2 design points (Step 2 doc, 2F).
