# Task: 5J Step 1 (WP0) inventory — employee prompt

Written 2026-09-28 by the 5J manager. One task, one turn. Read-only.

## Read first
1. `GSSCanada-main/5J_docs_occ/Step1_docs/5thJ_01_wp0Inventory.md` (the spec: items A to F).
2. `GSSCanada-main/5J_docs_occ/Step1_docs/5thJ_01_wp0Inventory_val.md` (what will be checked).

## 🔴 Hard rules
* **UK data is off limits** (UKDS licence clause 5). Never open, hash, count, head, grep or parse any
  UK data file: anything under `_local_runs/4J/raw/uk/`, `episodes_uk.parquet`,
  `acquisition_manifest_uk.json`, UK crosswalk files, any 4J output that pools UK with other countries,
  any schedule, IDF or EnergyPlus output built from UK diaries. You may `ls -l` them (names and sizes).
  If unsure whether a file has UK rows, list it by name and size only and say so. Code, markdown docs,
  UK weather files and UK TABULA parameters may be read.
* Read-only: change no file outside `5J_docs_occ/Step1_docs/outputs_step1/` and the impl doc
  `5J_docs_occ/Step1_docs/impl/2026-09-28_wp0_inventory.md`.
* Speed: `ssh o_iseri@speed.encs.concordia.ca` for `ls` only (login shell is tcsh). No python, no
  `du`, no `quota`, no `srun`, no `sbatch` in this task. If ssh asks for a password or hangs, stop and
  write that down.
* Locally: `wc -l`, `md5sum`, `ls -l`, `grep -n` are fine. For parquet row counts use only the file
  metadata: `PYTHONIOENCODING=utf-8 py -c "import pyarrow.parquet as p;print(p.ParquetFile(r'<path>').metadata.num_rows)"`
  (Spain and Italy only). `python` is not on the bash path; use `py`.
* Never read a multi-MB file into context: counts, heads of at most 5 lines (non-UK), greps.
* Quote every fact with its source: the command and its output, or `file:line`.
* Do not wait or poll. Write state to the impl doc as you go.

## Deliver
1. `5J_docs_occ/Step1_docs/outputs_step1/wp0_inventory.md`: sections A to F as in the spec.
2. `5J_docs_occ/Step1_docs/outputs_step1/wp0_inventory.json`: same facts (keys `A_hetus`, `B_schedules`,
   `C_buildings`, `D_weather`, `E_runner`, `F_cluster`; each fact a dict with `value` and `source`).
3. `5J_docs_occ/Step1_docs/impl/2026-09-28_wp0_inventory.md` with the headings: Status, Ledger,
   Verified, Decisions, Next, WHAT I DID NOT VERIFY. UK line = `WAITING ON AUTHOR`.

Extras the Step 2 design needs (put them in the relevant section):
* From 4J docs: the measured seconds (or minutes) per annual EnergyPlus run, per country, with source
  line; output size per run; the EnergyPlus version and install path on Speed; the Python env path
  used by 4J Speed jobs.
* From `4thJ_step8_idf.py`: every function argument that sets a building parameter, and the list of
  `Output:Meter` / `Output:Variable` objects written, and the timestep.
* From `4thJ_step7_schedules.py`: `DIARY_ORIGIN_HOUR` value(s) and the time step of written schedules.
* From `4thJ_step9_mapping.py`: whether secondary activity feeds electricity schedules (quote).
* From the 4J weather tools: list of EPW files (city, year, source) that exist locally or on Speed.
* Open 4J findings that touch reused tools (grep the 4J pipeline doc and Step 7 to 10 docs for
  "FINDING" near the tool names); list them with `file:line`, do not assess them.

End your turn with one line: "inventory written to <path>; N facts; UK waiting on author".
