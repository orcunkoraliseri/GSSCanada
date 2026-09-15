# T14 — WP12.1 follow-up: activity codes observed in the diaries vs codebook rows — implementation state

Task doc:   this file (section "Task")
Parent:     `2026-09-15_T08_wp12_crosswalk_counts.md` (read its Verified and Next first)
Status:     DONE

## Task

**Why.** The paper states 182 / 264 / 64 / 121 activity codes (2005 / 2010 / 2015 / 2022). The
crosswalk sheets the pipeline reads give 183 / 266 / 64 / 123 rows, with a stray code `2` row in
2005 and 2010. Test one explanation: the paper counted codes that **occur in the diary episodes**.
Expected if true: 2005 = 182, 2010 = 264, 2015 = 64, 2022 = 121. **Counts only; no edits.**

**All compute on Speed via `sbatch`** (`-p ps -c 2 --mem=8G -t 7-00:00:00`), python
`/speed-scratch/o_iseri/envs/step4/bin/python`, work dir `/speed-scratch/o_iseri/2J_revision/T14/`.
Login node: only `sbatch squeue sacct scancel scontrol cd ls scp` and single-file `tail head grep wc -l cat`.
**Never `find`, `du`, or python on the login node.** tcsh: no `2>&1` or `2>/dev/null` in ssh strings;
`ssh -o BatchMode=yes -o ConnectTimeout=60`, retry once.

**Inputs** (local, under `2J_docs_occ_nTemp/`; scp to `T14/input/`, record byte sizes):
`outputs_step1/episode_{2005,2010,2015,2022}.csv` (~80 MB total) and
`references_activityCodes/Data Harmonization_activityCategories - execution.xlsx`. Check openpyxl is
importable in the job; if not, write NOT FOUND in the log and stop (no installs).

**Script `T14_scripts/t14_codes.py`.** Load crosswalks with a verbatim copy of
`build_activity_crosswalks` (`02_harmonizeGSS.py:369-391`, cite lines). Raw column `ACTCODE` for
2005/2010, `TUI_01` for 2015/2022 (`02_harmonizeGSS.py:398`); parse with `pd.to_numeric` as
`:405-417` does (2010 float then int fallback). Per cycle report:
- R1 codebook rows read; R2 distinct keys in the lookup (2010: count float keys and int keys separately);
- R3 distinct non-null raw codes observed in episodes;
- R4 observed codes that are in the codebook; R5 codebook codes never observed (list them);
- R6 observed codes not in the codebook, with episode counts (list them; note the special codes
  995 / 95 / 9999 handled at `:419-424`);
- R7 whether code `2` occurs in 2005/2010 episodes, with count.

Output `T14_out/t14_code_counts.csv` (cycle, measure, value, detail) + slurm log; scp back to `impl/T14_out/`.

**Employee rules.** One job. Compile-check locally (`py -3 -m py_compile`), scp, submit, write JobID in
Ledger, **end the turn**. No waiting, polling, or sleep. Write NOT FOUND rather than guess.

**Collector (later, fresh agent).** `sacct`, scp, fill Verified with R1–R7 per cycle, state whether
R4 matches 182/264/64/121 exactly. No manuscript edits.

## Ledger
- JobID 1328274 · `sbatch -p ps -c 2 --mem=8G -t 7-00:00:00` on `speed-submit2`, wrapped command
  `cd /speed-scratch/o_iseri/2J_revision/T14 && /speed-scratch/o_iseri/envs/step4/bin/python
  T14_scripts/t14_codes.py > T14_out/t14_codes.slurm.log` · submitted 2026-09-15 · state at
  submission time: PENDING/RUNNING (not polled further, per no-waiting rule) · output paths:
  `/speed-scratch/o_iseri/2J_revision/T14/T14_out/t14_code_counts.csv`,
  `/speed-scratch/o_iseri/2J_revision/T14/T14_out/t14_codes.slurm.log` (or
  `T14_out/NOT_FOUND.txt` if openpyxl import fails in-job — checked inside the script per task doc,
  not pre-checked on the login node).

## Verified
**Inputs scp'd to Speed, byte sizes match local source exactly (`ls -la` on login node vs local):**
| file | bytes |
|---|---|
| `episode_2005.csv` | 29,947,570 |
| `episode_2010.csv` | 16,570,338 |
| `episode_2015.csv` | 17,116,899 |
| `episode_2022.csv` | 15,690,093 |
| `Data Harmonization_activityCategories - execution.xlsx` | 28,956 |

Script `T14_scripts/t14_codes.py` (6,950 bytes) scp'd to
`/speed-scratch/o_iseri/2J_revision/T14/T14_scripts/`. All five inputs total ~79.3 MB (matches
task doc's "~80 MB" estimate for the episode files).

`py -3 -m py_compile T14_scripts/t14_codes.py` — compiled clean, locally, before scp.

Episode CSV headers confirmed by local `head` before writing the script: 2005/2010 carry
`ACTCODE` (float in 2005, e.g. `450.0`; plain numeric in 2010, e.g. `450.0`/`430.0`, occasional
decimals like `940.1`); 2015/2022 carry `TUI_01`. This matches the task doc's column spec
(`02_harmonizeGSS.py:398`).

**Collected by manager, 2026-09-15.** `sacct -j 1328274`: COMPLETED, exit 0:0, 00:00:10. Outputs
scp'd to `impl/T14_out/` (`t14_code_counts.csv` 1,517 B, `t14_codes.slurm.log` 1,694 B); slurm-1328274.out empty.

- 2005: R1 183 rows, R2 183 keys, R3 182 observed, R4 182, R6 0, R5 1 (995, the sentinel, 0 episodes). Code `2` occurs in 387 episodes.
- 2010: R1 266 rows, R2 266 float + 42 int keys, R3 264 observed, R4 264, R6 0. Code `2` occurs in 309 episodes.
- 2015: R1 64, R3 64, R4 64, R6 0, R5 0. Sentinel 95 in 635 episodes.
- 2022: R1 123, R3 121, R4 121, R6 0, R5 2 (507, 1003). Code `2` absent. Sentinel 9999 in 136 episodes.

**Result: R4 (= R3) matches the paper's 182 / 264 / 64 / 121 exactly in all four cycles.** The paper's
counts are distinct activity codes observed in the diary episodes; the sheets hold 1 / 2 / 0 / 2 extra
codebook rows never observed. Code `2` in 2005/2010 is a real observed code, not a stray row.

**Unreconciled (manager):** 2010 R5 lists 50 codebook codes never observed, but R1 − R4 = 266 − 264 = 2.
Most likely the R5 set difference compares float keys against int-parsed observed codes (42 int
duplicates). It does not affect R4 (bounded by R3 = 264 with R6 = 0), so the headline stands; the 2010
never-observed list is not to be quoted.

## Decisions
- Script mirrors `build_activity_crosswalks` (`02_harmonizeGSS.py:372-391`) verbatim for the
  dict-building loop, and additionally returns a `rows_kept` counter per cycle for R1 — the
  original function does not expose a row count, only the final dict, so this is a script-only
  addition (noted in the script's docstring), not a change to pipeline logic.
- R3/R4/R6 group by the parsed raw code (not by row), then check `any_matched` per code group —
  interpreted "observed codes" as distinct values, with episode counts attached to R6 (unmatched)
  rows only, per the task doc's explicit ask ("list them; note episode counts" for R6, no count
  requested for R4/R5).
- R7 (`code 2` occurrence) computed for all four cycles, not only 2005/2010 as the task doc's
  prose implies — harmless extra rows in the CSV, not a deviation from what was asked for
  2005/2010.
- Sentinel codes 995/95/9999 (`02_harmonizeGSS.py:420-425`) are only *noted* (episode count for
  that literal code value) — the script does not apply the override into the matched/unmatched
  classification, since the task doc asks to "note" them, not fold them into R4/R6.
- openpyxl importability check happens **inside the submitted job** (try/except around `import
  openpyxl`, writes `T14_out/NOT_FOUND.txt` and exits if it fails) — not pre-checked on the login
  node, since bare `python` is forbidden there.

## Next
DONE (manager collected; see Verified). Manuscript wording for WP12: "activity codes observed in the
diaries" (182/264/64/121), codebook rows 183/266/64/123. No further compute.

Superseded: Collector (fresh agent, after job finishes): `sacct -j 1328274` for exit state; scp
`T14_out/t14_code_counts.csv` and `T14_out/t14_codes.slurm.log` (or `NOT_FOUND.txt`) back to
`impl/T14_out/`; fill Verified with R1-R7 per cycle; state whether R4 matches 182/264/64/121
exactly for each cycle. No manuscript edits.

## WHAT I DID NOT VERIFY
- Job was not polled after submission (no-waiting rule) — exit code, wall time, and whether the
  script actually produced `t14_code_counts.csv` are unknown at submission time.
- Did not independently re-derive R1-R7 by hand; only compiled the script, did not execute it
  locally (per "all compute on Speed" instruction) or on the cluster before ending the turn.
- Did not confirm `openpyxl` is importable in `/speed-scratch/o_iseri/envs/step4/bin/python` — the
  job itself checks this and will write `NOT_FOUND.txt` if not, per task doc instruction (no
  installs, no login-node python to pre-check).
