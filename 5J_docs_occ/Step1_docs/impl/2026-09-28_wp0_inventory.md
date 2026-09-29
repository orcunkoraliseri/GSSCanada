# WP0 inventory — implementation state
Task doc:   5J_docs_occ/Step1_docs/impl/2026-09-28_wp0_inventory_TASK.md
Status:     DONE (employee part). Manager re-derivation DONE 2026-09-28 night (see "Verified (manager)"). UK line: WAITING ON AUTHOR.

Deliverables (all under `5J_docs_occ/Step1_docs/`):
`outputs_step1/wp0_inventory.md`, `outputs_step1/wp0_inventory.json` (65 facts in sections A to F, each a dict with `value` and `source`, plus 13 findings rows and `_meta`), this file.

## Ledger
No cluster jobs were submitted. Speed was touched only by `ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca '<ls ...>'` (key login worked, no password prompt, no hang).
- 2026-09-28 · ssh ls of `/speed-scratch/o_iseri`, `4J`, `4J/raw/*`, `4J/outputs_step1`, `4J_madrid`, `4J_step10_nocore`, `envs`, `openubem` · done · exit 0 · facts F and A (Speed copies).
- 2026-09-28 · local md5sum, `stat -c %s`, `wc -l` of Spain and Italy raw files · done.
- 2026-09-28 · parquet metadata `num_rows` for Spain and Italy episode files only · done.
- 2026-09-28 · generator script (scratchpad, not in repo) wrote the md and json from one fact list, so the two cannot differ (gate 1.3).

## Verified
- Spain raw: five files hashed by 4J's parse report all equal the local md5s and byte sizes (DIARIO2 40d1f7c3..., 127810080 B; DIARIO1 ea2d068b...; MHOGAR a5762792...; CINDIV bfad9a24...; DHOGAR 427a0274...). Source: `4J_docs_occ/Step1_docs/outputs_step1/parse_report_spain.txt` INPUTS READ block against `md5sum` output.
- Spain line counts (`wc -l`): DIARIO2 2778480, DIARIO1 19295, MHOGAR 25895, CINDIV 19295, DHOGAR 9541 = INE's stated counts in the same parse report ("MATCH" lines).
- Italy: DiarioGiornaliero md5 f1d70e2d... 79746805 B, `wc -l` 1077658 = 1077657 rows + header; Individui md5 fd055250... `wc -l` 44867 = 44866 rows + header. Equal to `parse_report_italy.txt`.
- Episode parquets (metadata only): Spain 430754 rows, Italy 1077657 rows; equal to the "WROTE ... rows" lines in the two parse reports.
- Spain and Italy zip md5s equal `acquisition_manifest.json` and `acquisition_manifest_italy.json` (grep -n md5).
- Local EnergyPlus: `C:/EnergyPlusV23-1-0/energyplus.exe --version` printed `EnergyPlus, Version 23.1.0-87ed9199d4`.
- OpenUBEM local git HEAD `4c023cc66d46d4befffe36a9e520339608124979`.
- EPW headers (line 1) read for all seven ERA5 files in `OpenUBEM/openubem/data/weather`; md5 and sizes in section D.
- One Spain schedule opened: `presence_HH_es_00035.csv`, 8761 lines (header + 8760 values), one column, 60-minute step per its manifest.
- Step 8 archetype table: 88 rows (es 24, uk 32, it 32) by counting the TABULA archetype manifest; 88 archetype IDF files on disk.

## Decisions
- Row counts for text files are `wc -l` (newlines); for Italy that includes the header line, stated as such.
- Per-country run time: only Madrid (~79 s) and London (~53 s) per cell per worker are stated in 4J docs; Bologna has cells per hour only. Recorded as found, no invention. Step 2 pilot must measure.
- `4thJ_step8_idf.py` has no per-parameter function arguments (its only input is a dict derived from a TABULA row), so "arguments that set a building parameter" are listed as the dict keys it reads plus the hard-coded constants. Flagged in section C.
- The 4J findings list is limited to findings that the docs tie to a reused tool by name or by adjacent line; it is a starting list, not a full grep of all 270+ findings.
- Two EnergyPlus versions exist in 4J (24.2 for Step 8 boxes, 23.1.0 for Step 10 OpenUBEM). Both recorded; nothing chosen.
- Speed parquet copies were not hashed (ssh is ls only); their size difference from the local copies is recorded as a finding.

## Next
Manager: re-derive one number per item (validation doc section 6), run gates 1.3, 2.2, 3.1 (each seen failing), then tick the parent checklist Step 1 boxes. Author: run the one UK line from the spec and paste the result below.

## Verified (manager, 2026-09-28 night)
Status after this block: **DONE except the UK line** (WAITING ON AUTHOR).
- A: `wc -l DIARIO1.TXT` = 19295; md5 ea2d068b2c0a3de692e5196e03a3d581. Equal to the inventory.
- B: `presence_HH_es_00035.csv` (leg5 es, cal2010): 8761 lines = header + 8760 hours; md5 279be545... equal
  to the inventory. Day 1 sum = 20.67 h present; year sum 6106.8 h (mean presence 0.697).
- C: `es_AB_ES01.idf` opened: `Version, 24.2;` (line 10); window U-Factor 5.35 (line 98) = manifest
  column `u_win` 5.35 for ES.01; `Output:Meter` lines = 0. All equal to the inventory.
- D: `es_madrid_2009_2010_y2010.epw` line 1 = `LOCATION,Madrid,Madrid,ESP,ERA5,...`; first data row year
  2010; md5 110b3649... equal to the inventory.
- E: `eplusout.err` of `es__relation-12582232__caseA__f000` = `EnergyPlus, Version 23.1.0-87ed9199d4`.
  Equal to the inventory.
- Gate 1.3 (md vs json paths, `_meta` excluded): 67 = 67, 0 differences, PASS. Seen failing: one planted
  path in a scratch copy of the json gives FAIL. (First run counted the task-doc path in `_meta`; the
  gate compares facts only.)
- Gate 3.1 (UK compliance): the employee's full transcript (`subagents/agent-ae2dd9a2dfdd5ba4e.jsonl`,
  1.26 MB, grepped, not read) holds 0 commands that open, hash, count or parse a UK file; the only
  commands naming UK paths are two `ls -l` on `raw/uk` and `raw/uk/unpacked/UK-TUS`; 0 Read-tool paths
  on UK files. PASS. Seen failing: `head episodes_uk.parquet` planted in a scratch copy of this doc
  gives 1 hit.
- Gate 2.2 compared by the employee against the 4J parse reports (all MATCH); the manager re-derived A.
- `squeue -u o_iseri` (2026-09-28 night): 1J holds 5 CPUs running (`1400935_19`) and two 1-CPU scorers
  pending on it. Nothing else of the author's on Speed.

## UK line
WAITING ON AUTHOR. Files listed by name and size only: the UK zip in the raw folder (21465300 B), the UK-TUS unpacked folder (directory), and the UK parsed episodes file (3392774 B). The author's line is in the spec, section A.

## WHAT I DID NOT VERIFY
- Anything about UK rows, hashes or content (not read by design). The 4J UK parse and gate reports and manifest were not opened.
- Md5 of the Speed copies of the raw files and of the Speed episode parquets (ssh is ls only). Whether Speed and local parquets have the same content is unknown; sizes differ.
- Scratch fill level: quoted from the 1J handoff (9.3 T of 10 T on 2026-09-25; the same doc also says 9.7 T used), not re-measured.
- Where Step 10 Speed jobs read EPW files: the Speed OpenUBEM weather folder does not exist at the path I tried; not found.
- The commit of OpenUBEM used for each 4J campaign (4J pins engine file digests, not commits); only today's local HEAD is recorded.
- Speed EnergyPlus 24.2 trees mentioned in a 4J doc were not located.
- Total output size per run: one Spain run folder listed (ls total 4144 KB); not summed across runs, and no Speed run folder was listed.
- Physics, correctness of any 4J tool, and whether the open findings still hold (listed, not assessed).
- Bologna per-worker seconds per run; the ES/UK timings were read from a 4J handoff note, not from job logs.
