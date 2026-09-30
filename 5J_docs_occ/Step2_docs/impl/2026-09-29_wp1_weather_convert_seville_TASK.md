# TASK (employee, Sonnet): 5J weather batch 2a: convert, check and score Seville 2010

Written 2026-09-29 ~21:45 by the 5J manager. Same method as batch 1: read
`2026-09-29_wp1_weather_convert_TASK.md` (same folder) in full; this task is that one with ONE site,
**es_seville (2010)**, and the checker already written. Seville's 13 zips are complete; Manchester and Milan are
still downloading (PID 19328) and are NOT part of this task.
State file: append a new section `## Convert batch 2a: Seville (<date time>)` to `2026-09-29_wp1_weather.md`
(Ledger / Verified / Decisions / WHAT I DID NOT VERIFY). Do not edit sections above it.

## Hard rules
Same as the batch 1 task: local only, never touch PID 19328, never call CDS or start a download, never edit
OpenUBEM or `4J_docs_occ`, no diary files, never wait or poll. Do not edit `tools\5thJ_check_epw.py` or the
converter; if either fails, record verbatim and stop.

## Steps
1. Re-count `raw\era5_es_seville_2010\*.zip` = 13, else stop.
2. Convert: `<python> <tools>\convert_era5_5J_to_epw.py --site es_seville --all-years`, log to
   `logs\convert_batch2a_2026-09-29.log`. Expected `epw\es_seville_2010.epw`.
3. Checker: re-run only the row-count gate seen failing (copy in `%TEMP%`, delete the last data row → FAIL,
   record the line and exit code, delete the copy), then the checker on the real Seville EPW. Add Seville to a
   new `epw\epw_check_batch2.json` (same shape as batch 1).
4. Score like batch 1 (RMSE of monthly means vs TABULA `targets.es.theta_month`). Seville has no 4J TMYx
   station in `candidates.es`; if one named Sevilla exists, add the monthly difference; otherwise say "no TMYx
   reference" and give monthly means only. **Add** Seville to `epw\weather_score_5J.json` without changing the
   existing six entries (show the other entries' md5-relevant fields unchanged: before/after of their rmse).
5. md5 of `es_seville_2010.epw` into the state file. Next line: "batch 2b (uk_manchester, it_milan) when their
   13 zips each exist".

## Report back (short)
Converter result; gate line + exit code; real SUMMARY line; Seville RMSE and July/January means; md5.
