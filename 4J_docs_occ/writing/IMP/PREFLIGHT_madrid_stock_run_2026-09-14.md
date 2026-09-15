# Preflight: Madrid (ES-MAD-BERRUGUETE) stock-scale run, from scratch, current fixed driver

Prepared 2026-09-14. Read-only investigation plus one syntax dry-run of the runner script this
report accompanies (`tools/4thJ_run_madrid_stock_campaign.sh`). **Nothing was simulated. No
EnergyPlus was run. No Step 10 or Step 11 tool was invoked for real, not even on one cell.** Every
claim below carries a `path:line` this report's writer opened directly. Where something could not
be pinned down it is marked **NOT FOUND**, with where was looked, rather than guessed. Root:
`4J_docs_occ/`; `GSS_ROOT` = `C:/Users/o_iseri/Desktop/GSSCanada`.

This report answers each of the eight preflight questions asked, in order.

---

## 1. The exact command line, working directory, environment variables and worker count the UK/IT
   campaigns ran with under the fixed driver

**Working directory / environment variables**: the launcher script sets none explicitly - no
`OPENUBEM_ROOT` override, no other env var. `4thJ_step10_nocore_campaign.py` defaults
`OPENUBEM_ROOT` from `os.environ.get("OPENUBEM_ROOT", r"C:/Users/o_iseri/Desktop/OpenUBEM")`
(`tools/4thJ_step10_nocore_campaign.py:125`) - so the UK/IT runs used the DEFAULT, unset, pointing at
`C:/Users/o_iseri/Desktop/OpenUBEM`. Confirmed on disk: that path exists and `py -3 -c "import
openubem"` resolves to `C:\Users\o_iseri\Desktop\OpenUBEM\openubem\__init__.py` (checked this
session). Working directory is not pinned to any particular cwd - the launcher script uses absolute
paths throughout, so cwd is irrelevant.

**The literal, final launcher script**, read verbatim (`GSS_ROOT/_local_runs/rerun_both_fixes.sh`,
whole file, 11 lines):

```sh
set -e
TOOL="C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py"
py -3 "$TOOL" --district GB-LDN-STDUNSTANS --shakedown --resume --workers 4 \
  --out "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_UK_local/out/GB-LDN-STDUNSTANS" \
  --run-root "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_UK_local/runs/GB-LDN-STDUNSTANS" \
  > "..._local_runs/4J_UK_local/logs/rerun_bothfixes_stdout.log" \
  2> "..._local_runs/4J_UK_local/logs/rerun_bothfixes_stderr.log"
py -3 "$TOOL" --district IT-BOL-GALVANI2 --shakedown --resume --workers 4 \
  --out "..._local_runs/4J_IT_local/out/IT-BOL-GALVANI2" \
  --run-root "..._local_runs/4J_IT_local/runs/IT-BOL-GALVANI2" \
  > "..._local_runs/4J_IT_local/logs/rerun_bothfixes_stdout.log" \
  2> "..._local_runs/4J_IT_local/logs/rerun_bothfixes_stderr.log"
```

This is the invocation the closing record (`Prompts/RESUME.md:2346-2352`, last+203) names as the
launch that produced the FINAL, clean-closed numbers (`Prompts/RESUME.md:1313-1318`, last+230):
London 12,070/12,070 completed, 0 failures; Bologna 11,680/11,710 completed, 30 cells failed across
3 accepted courtyard buildings; Madrid untouched throughout.

**Worker count: 4**, both cities, every launch on record (`Prompts/RESUME.md:2350`; also the earlier
supervisor launch at `Prompts/RESUME.md:3310`: `--shakedown --resume --workers 4`). The one deviation
seen is a single-cell repair re-run at `--workers 1` (`Prompts/RESUME.md:1289`, last+230's own fix) -
not the population-scale convention.

**Memory-watchdog wrapper actually used in production**: a `supervisor.ps1` per city launches the
python process via `Start-Process`, hands its PID to a `watchdog.ps1` that polls
`Win32_OperatingSystem` free/total memory every `PollSeconds` and `taskkill /PID <pid> /T /F`s the
tree if used memory crosses a threshold, then the supervisor loop relaunches with `--resume` until
`campaign_results.json` exists. Read directly: `_local_runs/4J_IT_local/logs/supervisor.ps1` (43
lines, `$Workers = "4"`, `$ThresholdPercent = 75`) and `_local_runs/4J_UK_local/logs/watchdog.ps1`
(37 lines, default `$ThresholdPercent = 80` - the two cities' scripts disagree on the default; the
supervisor's own explicit `-ThresholdPercent $ThresholdPercent` pass-through means 75% is what
actually governed IT, 80% is what governed UK if launched without the supervisor wrapper). The
runner script this report accompanies standardises on **75%** (IT's more conservative value) for
Madrid.

---

## 2. The Step 10 no-core driver script, and the vertex-snap fix

**Driver**: `tools/4thJ_step10_nocore_campaign.py` (1,818 lines). Confirmed by reading it directly -
not assumed from any prior note.

**The fix is present, unconditional, in the code as it stands today.** `build_idf_for_cell`
(`tools/4thJ_step10_nocore_campaign.py:1099-1239`):
- Imports `_stabilize_ring_coords` and `RING_STABILIZATION_GRID_M` from
  `openubem.geometry.european_residential` (line 1107-1108) and applies the 1 mm grid snap to every
  zone's `coords_m` before extrusion (lines 1163-1167), unconditionally, not gated on any `mode` key.
- Inlines `_snap_shared_interzone_vertices`'s clustering body (lines 1169-1187), also unconditional,
  run over every zone right before `extrude_geometry(idf, zones, [])` (line 1195).
- After extrusion, keeps the post-extrude `find_mismatched_interzone_pairs` /
  `_has_near_duplicate_vertex_surfaces` check as a disclosed backstop (lines 1196-1239): a genuine
  vertex-count mismatch raises `interzone_vertex_mismatch_unresolved` and the cell is excluded at
  build time (never reaches EnergyPlus, recorded `HARNESS_ERROR`); a near-duplicate-only residual is
  tolerated and disclosed via `fallback_reason: "near_duplicate_vertex_tolerated_box"`.

This matches the record's own description of the fix (`Prompts/RESUME.md:3097-3105`, last+164) and
its later completion (`Prompts/RESUME.md:2323-2335`, last+203, the construction-block companion fix
also confirmed present at the file's `construction()` assignment block). **This fix was applied to
`build_idf_for_cell`, the SAME driver Madrid's Speed campaign ran under the OLD code**
(`Prompts/RESUME.md:3129-3130`) - running Madrid through this driver now is exactly what gives it
provenance parity with London/Bologna.

---

## 3. Where Madrid's inputs live, and confirmation each one exists

All four checked directly this session (`ls -l`, sizes pasted verbatim):

**Weather file** (`FOLD_EPW["es"]`, `tools/4thJ_step10_nocore_campaign.py:202`):
```
-rw-r--r-- 1 o_iseri 197121 882333 Aug 26 11:34  C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/weather/es_madrid_2009_2010_y2010.epw
```
EXISTS, 882,333 bytes. Weather registry beside it also exists: `.../weather/weather_registry.json`,
13,674 bytes.

**Archetype file** (`DISTRICTS["ES-MAD-BERRUGUETE"]["archetypes"]`,
`tools/4thJ_step10_nocore_campaign.py:210-211`):
```
-rw-r--r-- 1 o_iseri 197121 81802 Aug 23 16:46  C:/Users/o_iseri/Desktop/OpenUBEM/openubem/data/construction/tabula_archetypes_es.json
```
EXISTS, 81,802 bytes.

**Footprint/geometry inputs / the `C2` building list**: there is no separate "building list" file -
the population is read live by `payload_rows()` (`tools/4thJ_step10_nocore_campaign.py:526-536`)
scanning `LAYOUT_ROOT / "eu_ES-MAD-BERRUGUETE_data" / "layouts"`, which is
`C:/Users/o_iseri/Desktop/OpenUBEM/openubem/outputs/3D/eu_ES-MAD-BERRUGUETE_data/layouts/`, nested
under two subdirectories exactly as the record describes (`Step10_docs/4thJ_10_nocoreRealStock.md:178-181`,
"nested under `layouts/relation/` and `layouts/way/`"). Confirmed on disk this session:
```
relation/  129 files, 3.1 MB
way/      1045 files, 15 MB
```
1,174 files total - consistent with the record's "1,175" figure (`Step10_docs/4thJ_10_nocoreRealStock.md:172`)
to within rounding/one file. EXISTS, non-empty, both subdirectories present (the historical bug that
made this guard walk one directory level only and read Madrid as zero files,
`Step10_docs/4thJ_10_nocoreRealStock.md:178-181`, is fixed - confirmed by this same section stating
the fix and by the fact the guard is what the Speed-era Madrid run itself passed, 11,510/11,510 cells
enumerated, `Prompts/RESUME.md:4663`).

**NOT FOUND / flagged, not guessed**: the exact eligible-building count for a run TODAY. Three
different numbers exist in the record for the same guard at different times: the Speed campaign's own
`1,151` buildings / `11,510` cells (`Prompts/RESUME.md:5107-5108`, measured from
`preflight_report.json` directly); the corrected-guard figure `1,100 of 1,175`
(`Step10_docs/4thJ_10_nocoreRealStock.md:172`, dated after two guard bugfixes); and whatever the guard
prints when actually run today. These are NOT the same measurement - the guard changed between them.
The real number is whatever `--dry-run` prints on the day the campaign is actually launched; this
report does not run it (out of scope) and does not assert a figure.

---

## 4. Where the existing Speed-era Madrid outputs live, and proof the new run will not overwrite them

**Speed-era Madrid output location** (`Prompts/RESUME.md:5596-5597`, read directly):
```
runs  /speed-scratch/o_iseri/4J_step10_nocore/runs/ES-MAD-BERRUGUETE/es__<building>__caseA__f000
out   /speed-scratch/o_iseri/4J_step10_nocore/out/ES-MAD-BERRUGUETE
```
This is on the Speed cluster filesystem (job `1315013`, node `salus`, 31 cpu,
`Prompts/RESUME.md:6874`), not on this local machine, and Speed is read-only/fetch-only for 4J per
the standing project rule. Nothing under `/speed-scratch/...` is reachable or touchable by a local
script, so it cannot be overwritten by construction.

**Checked this session that no local copy of it exists either**, so as not to assume the Speed path
is the only place a collision could happen:
- `Step10_docs/outputs_step10_nocore/` (the driver's own `DEFAULT_OUT`,
  `tools/4thJ_step10_nocore_campaign.py:190`): 1,427 cell files, **all prefixed `it__`, zero prefixed
  `es__`**. Confirmed by listing and grep-counting the prefixes directly.
- `Step11_docs/outputs_step11/`: only `c2_it/` and `c2_uk/` subdirectories exist; **no `c2_es/`**.
- `GSS_ROOT/_local_runs/`: no directory named `4J_ES_local` exists (checked with `ls`, returns "No
  such file or directory").
- **One thing found and flagged, not touched**: `GSS_ROOT/_local_runs/step10_nocore/` (the driver's
  own `DEFAULT_RUN_ROOT`, `tools/4thJ_step10_nocore_campaign.py:191`) contains **45** `es__`-prefixed
  subdirectories dated 2026-09-09 07:48, each holding a built `.idf` and its gain CSVs but **no
  EnergyPlus result file** (no `.eso`/`.audit`/result JSON) - this is leftover scratch from an early
  local IDF-build-only pass (45 of an eventual 11,510+ cells; far too small to be the real campaign),
  not a simulated result. It sits under the driver's DEFAULT run-root/out paths, which is exactly why
  the runner script does **not** use the defaults and instead names its own directory tree
  (`_local_runs/4J_ES_local/{out,runs}/ES-MAD-BERRUGUETE`, mirroring `4J_UK_local`/`4J_IT_local`'s own
  naming), so the new run cannot collide with this leftover or be mistaken for it.

**Proof the target directory is empty/does not exist** (this session, dry-run of the runner script
itself - see section 8): `ls -la "GSS_ROOT/_local_runs/4J_ES_local"` returns "No such file or
directory". The dry run creates nothing (verified: the directory still does not exist after running
`--dry-run`).

---

## 5. EnergyPlus binary/version, and whether it is installed now

**Pinned in code**: `DEFAULT_EPLUS = Path(r"C:/EnergyPlusV23-1-0/energyplus.exe")`
(`tools/4thJ_step10_nocore_campaign.py:197`); `REQUIRED_EP_VERSION = "23.1"`
(`tools/4thJ_step10_nocore_campaign.py:317`), checked at preflight against the measured version
string (`tools/4thJ_step10_nocore_campaign.py:805-809`).

**Checked, not assumed, this session**:
```
$ ls -l C:/EnergyPlusV23-1-0/energyplus.exe
-rwxr-xr-x 1 o_iseri 197121 14336 Mar 28 2023 C:/EnergyPlusV23-1-0/energyplus.exe
$ C:/EnergyPlusV23-1-0/energyplus.exe --version
EnergyPlus, Version 23.1.0-87ed9199d4, YMD=2026.09.14 16:56
```
INSTALLED, correct major/minor version, and it is the SAME binary path London and Bologna's local
runs used (their own commands never override `--energyplus`, so they used this default too) - so a
from-scratch Madrid run on this machine gets the same engine build without any extra step.

Python resolves the same way both runs used: `py -3` and the supervisor's hard-coded
`C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe`
(`_local_runs/4J_IT_local/logs/supervisor.ps1`) are the SAME interpreter - confirmed this session
with `py -3 -c "import sys; print(sys.executable)"` -> identical path. `openubem` imports cleanly from
it (`import openubem` -> `C:\Users\o_iseri\Desktop\OpenUBEM\openubem\__init__.py`), and all four
driver/tool files parse clean (`ast.parse`, this session): `4thJ_step10_nocore_campaign.py`,
`4thJ_step11_trigger_campaign.py`, `4thJ_step11_aggregate.py`, `4thJ_step11_stockboard.py`.

---

## 6. The three Step 11 commands, in order, filled in for `es`

All three tools' argparse blocks read directly (`tools/4thJ_step11_trigger_campaign.py:579-599`,
`tools/4thJ_step11_aggregate.py:71-85`, `tools/4thJ_step11_stockboard.py:78-94`). `--diary-diversity`
has no default and the author's ruling is `reseed` (`Prompts/RESUME.md:1148`, `S9`/`S9b`, cited
repeatedly). Output paths below mirror the IT/UK convention exactly as found on disk
(`Step11_docs/outputs_step11/c2_it/step11_11-3_it_reseed.json`,
`Step11_docs/outputs_step11/g11_6_18/c2_it/step11_stockboard_it.json`, etc.):

```
# 11.3 -- trigger campaign
"$PYTHON_EXE" tools/4thJ_step11_trigger_campaign.py \
    --root "4J_docs_occ" --c2-out "<Step10 out dir for ES-MAD-BERRUGUETE>" \
    --diary-diversity reseed \
    --out "Step11_docs/outputs_step11/c2_es/step11_11-3_es_reseed.json"

# 11.5 -- stock-scale aggregation (G11.12)
"$PYTHON_EXE" tools/4thJ_step11_aggregate.py \
    --root "4J_docs_occ" --c2-out "<same Step10 out dir>" \
    --diary-diversity reseed \
    --out "Step11_docs/outputs_step11/c2_es/step11_11-5_es_reseed.json"

# 11.6 -- gate-board stock inputs (G11.6 / G11.8 / G11.18)
"$PYTHON_EXE" tools/4thJ_step11_stockboard.py \
    --root "4J_docs_occ" --c2-out "<same Step10 out dir>" \
    --diary-diversity reseed \
    --out-dir "Step11_docs/outputs_step11/g11_6_18/c2_es"
```

No `--limit`, no `--scored` (the tools score nothing by design; `--scored` on the Step 10 driver is
refused by `R8` regardless of district, `AUTHORISED[...]["scores"] = False` for all three cities,
`tools/4thJ_step10_nocore_campaign.py:268-282`).

**Flagged, not resolved by this report**: the UK/IT launch of these same three tools found 49
buildings (42 Bologna + 7 London) carrying synthetic *floor-averaged* diaries rather than real
per-flat Step 7 diaries, and hand-built a filtered copy of `out/cells/` excluding them before pointing
`--c2-out` at the copy (`Prompts/RESUME.md:1136-1144`, last+236). Whether Madrid's fresh Step 10
output will contain any such buildings is **NOT FOUND** - it did not exist under the current driver
before today, so nothing on disk answers this. The runner script's own `--dry-run` output states this
explicitly as a manual check to make before Stage 2 runs for real.

---

## 7. What would make the run fail in the first five minutes

**No hard-coded UK/IT-only district list excludes `es`.** Checked directly:
- `DISTRICTS` (`tools/4thJ_step10_nocore_campaign.py:209-218`) includes `"ES-MAD-BERRUGUETE"` on
  equal footing with `GB-LDN-STDUNSTANS` and `IT-BOL-GALVANI2`.
- `AUTHORISED` (`tools/4thJ_step10_nocore_campaign.py:227-283`, the `D-EU-55`/`R2` gate) carries a
  Madrid entry, `"mode": "campaign", "scores": False`, quoting the author's own sentence dated
  2026-09-08 - **Madrid IS authorised**, on the same footing as London and Bologna. `R2` will not
  refuse it.
- `FOLD_EPW` (`tools/4thJ_step10_nocore_campaign.py:184-188`) carries `"es"`.
- `STEP11_FOLDS = ("es", "uk", "it")` (`tools/4thJ_step11_trigger_campaign.py:165`) - `es` is
  included; no city-name string literal anywhere in the three Step 11 tools singles out `it`/`uk`
  only (checked by grep across all three files, only hit was this `STEP11_FOLDS` tuple, which already
  includes `es`).

**Genuine risk items found, in order of likelihood**:
1. **`R3` refuses France unconditionally, `R2` refuses anything not in `AUTHORISED`** - neither
   applies to `ES-MAD-BERRUGUETE`, but if the district string is mistyped (e.g. missing the
   `-BERRUGUETE` suffix) argparse's own `choices=sorted(DISTRICTS)` refuses before any other check
   runs (`tools/4thJ_step10_nocore_campaign.py:1646`).
2. **Digest pins** (`ENGINE_DIGEST_PIN`, `NOCORE_DIGEST_PIN`) are checked by `R4` against the live
   OpenUBEM tree regardless of district - if the OpenUBEM checkout has drifted since the pin was last
   taken, `R4` fires for Madrid exactly as it would for anyone. **NOT FOUND / not checked by this
   report**: the current live digest vs the pinned one - this needs the preflight to actually run,
   which is out of scope here.
3. **`R7`, the gain-CSV-file-name / drawn-flat-count refusal**, historically refused BOTH Madrid and
   Bologna at one point (`Prompts/RESUME.md:1702-1710`, last+49, "A corrected `R7` refuses Madrid and
   Bologna at preflight, by design"). This was from an earlier, since-superseded guard state - Madrid's
   own Speed campaign later completed 11,510/11,510 cells enumerated under a working `R7`
   (`Prompts/RESUME.md:4663`), so `R7` is known to pass for Madrid's population as of that run. Since
   then the driver changed only inside `build_idf_for_cell` (the vertex-snap fix, section 2), not in
   `R7`'s own logic - so this is very unlikely to reappear, but it is not re-verified today.
4. **The 45 leftover `es__` scratch directories** under the driver's DEFAULT run-root (section 4) are
   harmless to a run that uses its OWN `--run-root`/`--out` (as the runner script does), but would be
   a real collision risk if anyone ever ran the driver with no `--out`/`--run-root` override for
   Madrid.
5. **Disk space** for ~11,000+ cells' worth of `.idf`+gain-CSV+result JSON: **NOT FOUND** - not
   measured this session (no instruction to check free disk space, and London/Bologna's own runs are
   the only precedent for the per-cell footprint, not separately totalled in the record).

Nothing else was found that would abort inside the first five minutes.

---

## 8. Runner script and dry-run output

Written to `tools/4thJ_run_madrid_stock_campaign.sh` (POSIX sh for Git Bash - the pipeline itself
is NOT Windows-only in principle, but its precedent memory-watchdog mechanism
(`Win32_OperatingSystem`/`taskkill /T /F`) is Windows-specific, so the script shells out to
`powershell.exe` for exactly that part, matching the UK/IT precedent's own design rather than
reinventing a cross-platform one).

It: uses `set -eu -o pipefail`; runs Step 10 (`--shakedown --resume --workers 4`, mem-kill threshold
75%, matching IT's supervisor) then the three Step 11 passes in order, each gated on the previous
stage's output-marker file existing; writes a timestamped master log plus per-stage stdout/stderr
logs under `_local_runs/4J_ES_local/logs/` (the same directory shape as `4J_UK_local`/`4J_IT_local`);
prints a start/end timestamp per stage; is resumable for Step 10 via the driver's own `--resume` flag
(same mechanism as the precedent) with a bash-level relaunch loop (max 40 attempts) standing in for
`supervisor.ps1`; and is **honestly not resumable at the sub-stage level for the three Step 11
passes**, because none of the three tools exposes a `--resume`/skip-completed flag (confirmed by
reading all three argparse blocks) - a kill mid-Step-11-stage restarts that whole stage from scratch,
stated plainly in both this report and the script's own `--dry-run` output.

**Only execution performed this session**: `bash tools/4thJ_run_madrid_stock_campaign.sh --dry-run`.
Full output (verbatim):

```
==========================================================================
DRY RUN -- Madrid (ES-MAD-BERRUGUETE) stock campaign, Step 10 C2 + Step 11
Nothing below this line is executed. No directory is created. No process
is launched. Exit code will be 0.
==========================================================================

Would create directories:
  mkdir -p "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs"
  mkdir -p "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE"
  mkdir -p "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/runs/ES-MAD-BERRUGUETE"
  mkdir -p "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/c2_es"
  mkdir -p "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/g11_6_18/c2_es"

Would write watchdog helper: C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/watchdog.ps1
  (ported from _local_runs/4J_UK_local/logs/watchdog.ps1, threshold 75% committed memory, poll 20s, taskkill /T /F on breach)

Master log: C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/madrid_stock_campaign_20260914_170213.log

-------------------------------------------------------------------------
STAGE 1/4 -- Step 10 campaign C2, district ES-MAD-BERRUGUETE, fold es
  marker (stage complete when this file exists): C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE/campaign_results.json
  resumable: YES, via the tool's own --resume flag (skips cells already
  written under C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE/cells/ -- same mechanism the UK/IT local runs used)
  command, relaunched with the same flags after every watchdog kill until
  the marker file exists (max 40 attempts, 15s between):
    "C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe" "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/tools/4thJ_step10_nocore_campaign.py" \
        --district ES-MAD-BERRUGUETE --shakedown --resume --workers 4 \
        --out "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE" --run-root "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/runs/ES-MAD-BERRUGUETE"
  stdout/stderr: C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/step10_c2_es_stdout.log / _stderr.log
  watched by: powershell.exe -File "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/watchdog.ps1" -CampaignPid <pid> -ThresholdPercent 75 -PollSeconds 20

-------------------------------------------------------------------------
STAGE 2/4 -- Step 11 work item 11.3, per-dwelling trigger campaign
  marker: C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/c2_es/step11_11-3_es_reseed.json
  resumable: NO -- 4thJ_step11_trigger_campaign.py has no --resume/skip
  flag (confirmed by reading its argparse block). A kill mid-stage means
  a full restart of this stage on relaunch.
  gated on: STAGE 1's marker existing (Step 10 must have finished first)
  command:
    "C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe" "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/tools/4thJ_step11_trigger_campaign.py" \
        --root "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ" --c2-out "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE" \
        --diary-diversity reseed --out "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/c2_es/step11_11-3_es_reseed.json"
  stdout/stderr: C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/step11_11-3_es_stdout.log / _stderr.log

-------------------------------------------------------------------------
STAGE 3/4 -- Step 11 work item 11.5, stock-scale aggregation (G11.12)
  marker: C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/c2_es/step11_11-5_es_reseed.json
  resumable: NO (same as stage 2, confirmed by reading its argparse block)
  gated on: STAGE 2's marker existing
  command:
    "C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe" "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/tools/4thJ_step11_aggregate.py" \
        --root "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ" --c2-out "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE" \
        --diary-diversity reseed --out "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/c2_es/step11_11-5_es_reseed.json"
  stdout/stderr: C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/step11_11-5_es_stdout.log / _stderr.log

-------------------------------------------------------------------------
STAGE 4/4 -- Step 11 work item 11.6, gate-board stock inputs (G11.6/8/18)
  marker: C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/g11_6_18/c2_es/step11_stockboard_es.json
  resumable: NO (same as stage 2, confirmed by reading its argparse block)
  gated on: STAGE 3's marker existing
  command:
    "C:/Users/o_iseri/AppData/Local/Programs/Python/Python313/python.exe" "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/tools/4thJ_step11_stockboard.py" \
        --root "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ" --c2-out "C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE" \
        --diary-diversity reseed --out-dir "C:/Users/o_iseri/Desktop/GSSCanada/GSSCanada-main/4J_docs_occ/Step11_docs/outputs_step11/g11_6_18/c2_es"
  stdout/stderr: C:/Users/o_iseri/Desktop/GSSCanada/_local_runs/4J_ES_local/logs/step11_11-6_es_stdout.log / _stderr.log

-------------------------------------------------------------------------
NOTE (not automated by this script -- see preflight report section 6/8):
  the UK/IT Step 11 launch found 49 buildings (both cities combined)
  carrying SYNTHETIC floor-averaged diaries rather than real per-flat
  Step 7 diaries, and excluded them via a hand-built filtered COPY of
  out/cells/ before pointing 11.3/11.5/11.6 at it. Whether Madrid's
  fresh Step 10 output contains any such buildings is NOT established by
  this script and was NOT FOUND in the record -- check
  <out>/cells/*.json for a non-real diary_origin marker (the same way
  the UK/IT seam was found) before STAGE 2 runs for real, and if any
  exist, build a filtered '_step11input' copy the same way and point
  --c2-out at that copy instead of the raw out directory.

DRY RUN complete. Exiting 0. Nothing was created or executed.
```

**Exit code: 0.** Confirmed after the run that `GSS_ROOT/_local_runs/4J_ES_local` still does not
exist (`ls -la` returns "No such file or directory") - the dry run created nothing, as required.
`bash -n tools/4thJ_run_madrid_stock_campaign.sh` also checked clean before this run.

---

## Summary for the launching session

Nothing found blocks a from-scratch Madrid run under the current driver: `es` is fully wired into the
distict list, the authorisation table, the fold table, and the Step 11 fold tuple; the weather,
archetype and layout inputs all exist and were sized; EnergyPlus 23.1.0 is installed at the pinned
path; the vertex-snap fix is present and unconditional in `build_idf_for_cell`; the target output
directory (`_local_runs/4J_ES_local/`) does not exist yet, so nothing can be overwritten, and the
existing Speed-era Madrid output sits on the Speed cluster, untouched and unreachable by this script.
The two open items that are NOT resolved by this report, and should be read before launching for
real: (1) the exact eligible-building count under today's guard is unmeasured (three different
historical numbers exist for three different guard states); (2) whether Madrid's own Step 10 output
will carry any synthetic floor-averaged-diary buildings needing the same exclusion UK/IT needed is
unknowable before Step 10 actually runs.
