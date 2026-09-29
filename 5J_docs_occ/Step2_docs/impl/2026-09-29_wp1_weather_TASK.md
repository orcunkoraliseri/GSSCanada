# TASK (employee, Sonnet): 5J weather download — copy the OpenUBEM ERA5 scripts, write the 5J registry, start the download

Written 2026-09-29 by the 5J manager. Ruling: D2-1 = (a), six cities (Step 2 doc
`../5thJ_02_campaignDesignPilot.md`, section 2F, "RULED 2026-09-29").
State file you keep current: `2026-09-29_wp1_weather.md` (same folder; create it first, CLAUDE.md
template: Task doc / Status / Ledger / Verified / Decisions / Next / WHAT I DID NOT VERIFY).

## Hard rules
* **Never edit anything under `C:\Users\o_iseri\Desktop\OpenUBEM\`** (closed project). Read and copy only.
* All runs are **local** on this Windows machine (weather is not diary data; nothing goes to Speed).
  Python: `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe` (same as `py`).
* **One CDS job at a time** (concurrent jobs were rejected before). Before starting, confirm no other
  python process is running an ERA5 script (`Get-CimInstance Win32_Process -Filter "Name like 'python%'"`).
* **You never wait.** Start the download detached, write its PID and log paths to the state file, end
  your turn. No sleep, no polling loops beyond the one check in step 6.
* Never pass or print the CDS key; cdsapi reads `~/.cdsapirc` itself.
* Do not touch any UK diary file (licence). Weather files are fine.
* Create only the files named here.

## Paths
* Tools: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\tools\`
  → `acquire_era5_5J.py`, `convert_era5_5J_to_epw.py` (copies of OpenUBEM
  `scripts/acquire_era5_eu_folds.py` md5 `666da02ebbf27351e2ad4f29f73b46ae`, 275 lines, and
  `scripts/convert_era5_eu_folds_to_epw.py` md5 `75e24d724a14d81d383039e04e89b5dd`, 351 lines;
  re-check both md5s before copying and record them).
* Data root: `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\weather\`
  → `weather_registry_5J.json`, `raw\era5_<site>_<year>\` (zips + `jobs\`), `epw\` (later), `logs\`.

## Steps
1. Copy the two scripts. Change **only**:
   a. Paths: `REGISTRY_PATH`, `RAW_ROOT`/raw dir, `OUTPUT_ROOT` → the absolute 5J paths above.
   b. **Keying per site, not per country:** targets keyed by a new registry field `site`
      (e.g. `es_valencia`); `fold` stays the country code (es/uk/it) and is used only for `ISO3`.
      `--fold` filters still work; add `--site` (repeatable) filter to both scripts.
   c. **Elevation per site:** read `elevation_m` from the registry entry; remove `ELEVATIONS_M`; a
      missing or null elevation is an error.
   d. **One year:** registry `raw_era5_window` is `YYYY-01-01/YYYY-12-31`; in `acquire` `_jobs` loop
      over the distinct years only (`sorted({start_year, end_year})`), so months are not requested
      twice. Keep the boundary day (prior year 12-31) exactly as now.
   e. Status filter: read entries with `status == "RULED_5J"` (instead of `RULED_NOT_PINNED`).
   Keep every other line (variables, grid crop, submit/poll/download loop, pvlib conversion, header
   format). Update the module docstrings to say what changed and cite the source md5. Put a
   `# 5J change:` comment on each changed line block.
2. Write `weather_registry_5J.json`: `{"schema": "5J weather registry v1", "created": "2026-09-29",
   "source_scripts": {...md5s...}, "targets": [...]}`, six entries **in this order** (download order):

   | site | fold | city | station | lat | lon | elev m | year | UTC offset |
   |---|---|---|---|---|---|---|---|---|
   | es_valencia | es | Valencia | Valencia.Viveros | 39.483 | -0.383 | 11 | 2010 | 1 |
   | uk_birmingham | uk | Birmingham | Birmingham.AP | 52.454 | -1.748 | 99.7 | 2014 | 0 |
   | it_turin | it | Turin | Torino.Venaria | 45.131 | 7.618 | 278 | 2014 | 1 |
   | es_seville | es | Seville | see below | | | | 2010 | 1 |
   | uk_manchester | uk | Manchester | Manchester.AP | 53.354 | -2.275 | 78.3 | 2014 | 0 |
   | it_milan | it | Milan | Milano-Linate | 45.449 | 9.278 | 103 | 2014 | 1 |

   Each entry also has `status: "RULED_5J"`, `raw_era5_window`, `local_standard_utc_offset`,
   `output_filename` (`<site>_<year>.epw`), `coord_source` (the 4J OneBuilding EPW header in
   `4J_docs_occ/Step8_docs/outputs_step8/weather/_cache/`; open the header line only and confirm the
   numbers), `tabula_region` (`ES.ME`, `GB.ENG`, `IT.MidClim`).
   **Seville:** take latitude, longitude, elevation from the OneBuilding station record for
   Sevilla San Pablo airport (WMO 083910), `climate.onebuilding.org` Spain index or the station's
   EPW/STAT header (WebFetch is fine; read only). Write the URL in `coord_source`. If it cannot be
   found, use DR08's 37.38 N, 5.98 W (`C:\Users\o_iseri\Desktop\OpenUBEM\docs\docs_ACTIVE\
   europeanLocations\DeepResearch\DR08_actual_year_weather_sources_and_licences.md`) and mark the
   elevation `null` → then **stop before step 5 for Seville only**: move it last is not enough;
   remove `status` RULED_5J from it (set `PENDING_ELEVATION`) and say so in the state file.
3. Dry check (no CDS call): a python one-liner that imports the acquire copy and prints, per target,
   the site, the grid crop and the number of jobs. **Expected 13 jobs per site** and a crop around one
   0.25° point. Paste the output into the state file (Verified).
4. Gate seen failing (converter, no download needed): run the converter's target loader against a
   throwaway copy of the registry in the scratchpad `C:\Users\o_iseri\AppData\Local\Temp\claude\` (or
   `%TEMP%`) with one entry's `elevation_m` removed → it must raise; with two entries sharing a `site`
   → it must raise (add that duplicate check in step 1b). Record both errors. Delete nothing in the
   5J folders.
5. Start the download detached:
   `Start-Process -FilePath <python> -ArgumentList '<tools>\acquire_era5_5J.py','--run-sequential','--interval','30' -WorkingDirectory <data root> -WindowStyle Hidden -RedirectStandardOutput <data root>\logs\acquire_2026-09-29.out -RedirectStandardError <data root>\logs\acquire_2026-09-29.err -PassThru`
   Record PID, start time (UTC and local), exact command in the Ledger.
6. One check about 60 s later (a single `Start-Sleep 60` is allowed here, once): the process is alive,
   `.err` has no traceback, `.out` shows `SUBMITTED es_valencia 2009-12-31 ...` or the first job
   manifest exists under `raw\era5_es_valencia_2010\jobs\`. If it failed, record the error and stop
   (do not retry more than once).
7. State file: Status `IN PROGRESS (download running)`; Next = "when 78 zips (6 × 13) exist: convert
   with `convert_era5_5J_to_epw.py --all --all-years`, then check 8,760 rows + header + monthly means,
   planted 8,759-row EPW must be refused, 4J score per city, md5 every EPW".
   Also note: the PC must stay on and logged in; if the process dies, rerunning the same command
   resumes (the script skips zips on disk and reuses submitted job manifests).

## Report back (short)
PID, log paths, first SUBMITTED line, the two gate errors, Seville's coordinates and source, the md5s
of the two copies, and anything in step 1 you had to change beyond (a)–(e).
