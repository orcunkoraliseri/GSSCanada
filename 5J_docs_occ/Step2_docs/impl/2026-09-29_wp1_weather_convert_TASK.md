# TASK (employee, Sonnet): 5J weather — convert the finished ERA5 sites to EPW, check them, score them

Written 2026-09-29 afternoon by the 5J manager. Parent task: `2026-09-29_wp1_weather_TASK.md` (same folder).
State file you append to: `2026-09-29_wp1_weather.md` (same folder). Add a new section
`## Convert batch 1 (<date time>)` with Ledger / Verified / Decisions / WHAT I DID NOT VERIFY. Do not edit the
sections above it.

## Scope (this batch)
The three sites whose 13 zips are complete: **es_valencia (2010), uk_birmingham (2014), it_turin (2014)**.
Seville, Manchester, Milan are still downloading (PID 19328). **Do not touch PID 19328, do not start any
download, do not call CDS.** Before converting, re-count: each of the three `raw\era5_<site>_<year>\` folders
must hold exactly 13 zips (`<site>_<year-1>-12-31` + 12 months). If one does not, skip that site and say so.

## Hard rules
* Local only. Python: `C:\Users\o_iseri\AppData\Local\Programs\Python\Python313\python.exe` (not on bash PATH).
* Never edit `C:\Users\o_iseri\Desktop\OpenUBEM\` or anything under `4J_docs_occ\`. Read only.
* Weather is not diary data; no licence issue. Do not open any diary file.
* You never wait or poll. Create only the files named here.

## Paths
* Tools: `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main\5J_docs_occ\tools\`
* Data root: `C:\Users\o_iseri\Desktop\GSSCanada\_5J_data\surrogate\weather\` (`raw\`, `epw\`, `logs\`, registry)
* 4J scoring reference (read only): `GSSCanada-main\4J_docs_occ\tools\4thJ_step8_weather.py` (functions
  `read_epw`, `measure`, `rmse`) and `GSSCanada-main\4J_docs_occ\Step8_docs\outputs_step8\weather_selection_report.json`
  (`targets.<fold>.theta_month` = TABULA theta_e months; `candidates.<fold>[*]` = TMYx station measures).
* Existing ERA5 EPWs (score only, never copy or edit):
  `C:\Users\o_iseri\Desktop\OpenUBEM\openubem\data\weather\es_madrid_2009_2010_y2010.epw`,
  `...\uk_london_2014_2015_y2014.epw`, `...\it_bologna_2013_2014_y2014.epw`.

## Steps
1. **Convert.** Run from the data root, one call:
   `<python> <tools>\convert_era5_5J_to_epw.py --site es_valencia --site uk_birmingham --site it_turin --all-years`
   Log stdout+stderr to `logs\convert_batch1_2026-09-29.log`. Expected outputs:
   `epw\es_valencia_2010.epw`, `epw\uk_birmingham_2014.epw`, `epw\it_turin_2014.epw`. If the converter
   raises, record the error verbatim and stop (no code edits to the converter without the manager).
2. **Write the checker** `tools\5thJ_check_epw.py` (new file). Import nothing from 4J; copy the needed
   logic (`read_epw`, `measure`, `rmse`, same column indices) with a comment citing
   `4thJ_step8_weather.py` and its md5. For each EPW given on the command line (plus `--registry` path and
   `--site` per file, or a `--manifest` CSV of `site,path`), check and print one line per check:
   * exactly 8 header lines, then **exactly 8,760 data rows**, 365 days, 24 hours each;
   * LOCATION line: latitude, longitude, time zone, elevation equal to the registry entry (lat/lon to
     0.01°, elevation to 0.5 m, time zone = `local_standard_utc_offset`);
   * year column = registry year in every row except the boundary rule the converter uses (read the
     converter to see what the first hours carry; record what you find, do not guess);
   * no missing sentinels (dry bulb 99.9, RH 999, GHI 9999) and physical ranges: dry bulb −40..50 °C,
     RH 0..100, GHI ≥ 0 and 0 at local midnight hours;
   * monthly mean dry bulb (12 values), annual mean, annual GHI kWh/m².
   Outcomes per file: PASS / FAIL (with the failing check named) / NOT_EVALUABLE (file missing or
   unreadable). SUMMARY line at the end with the three counts; **exit code 0 = all PASS, 1 = any FAIL,
   2 = any NOT_EVALUABLE and no FAIL**. Write the exit-code meaning in the module docstring.
   Also write `epw\epw_check_batch1.json` (per site: checks, monthly means, annual GHI, md5).
3. **Gate seen failing (before trusting a PASS).** In a scratch folder
   (`C:\Users\o_iseri\AppData\Local\Temp\claude\` or `%TEMP%`, never under `_5J_data` or `5J_docs_occ`):
   (a) copy `es_valencia_2010.epw` and delete its last data row (8,759 rows) → must FAIL on row count;
   (b) copy it and change the LOCATION latitude by +1° → must FAIL on location;
   (c) a path that does not exist → must be NOT_EVALUABLE with exit code 2.
   Record the three printed lines and exit codes. Then run the checker on the three real EPWs.
4. **Score like 4J.** For each of the three new EPWs **and** the three existing OpenUBEM ERA5 EPWs
   (Madrid 2010, London 2014, Bologna 2014): RMSE of the 12 monthly means against TABULA
   `targets.<fold>.theta_month` (es → ES.ME, uk → England-Temperate, it → IT.MidClim). Also, for the
   three new cities, the monthly difference against the same city's TMYx station measure in
   `candidates.<fold>` (Valencia.Viveros 082850, Birmingham.AP 035340, Torino.Venaria 16…; match on `epw`
   name): print the 12 differences and the largest absolute one. Flag any month where |ERA5 − TMYx| > 3 °C
   (ERA5 is one 0.25° grid cell for one real year, TMYx a typical year, so a few tenths to ~2 °C is
   expected; >3 °C means check the grid point).
   Write `epw\weather_score_5J.json` (per site: fold, year, source ERA5, rmse_theta_month, theta_month,
   ghi_year_kwh, tmyx_diff_month where available, md5) and a small table in the state file.
5. **md5** every EPW you produced (and the three OpenUBEM ones you scored) into the state file.
6. State file `## Next`: "batch 2 (es_seville, uk_manchester, it_milan) when their 13 zips each exist:
   same command with those three `--site`, same checker, add to `weather_score_5J.json`".

## Report back (short)
Converter result per site; the checker's three gate lines with exit codes; the real-run SUMMARY line;
the RMSE table (six cities); any month flagged >3 °C; md5s; anything you had to decide.
