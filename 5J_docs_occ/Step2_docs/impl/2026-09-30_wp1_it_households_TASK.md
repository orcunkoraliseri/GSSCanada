# TASK (employee, Sonnet): 5J household inputs on Speed: Spain reproduction, Italy 60, average households (B0)

Written 2026-09-30 16:16 EDT (from `date`) by the 5J manager. Step 2 closure, part 1 of 2 (part 2 =
`2026-09-30_wp1_campaign_design_TASK.md`, runs in parallel; do not touch its Speed folder).
State file: create `Step2_docs/impl/2026-09-30_wp1_it_households.md` (Task doc / Status / Ledger / Verified /
Decisions / Next / WHAT I DID NOT VERIFY), write as you go; `date` before every stamp.
G = `C:\Users\o_iseri\Desktop\GSSCanada`. Read first: `Step2_docs/impl/2026-09-29_wp1_households_v2.md`,
`Step2_docs/impl/2026-09-29_wp1_corpus_guard.md` (the trigger commands, line 23 and 31), `tools/5thJ_pilot_build.py`
(how a household becomes presence/appliance files + n_members + design level), `tools/5thJ_idf_mz.py` lines 1-40
and 440-470 (the household dict build_mz takes).

## Hard rules
* 🔴 ALL compute on Speed (author). Locally ONLY: edit/write files, `ssh`/`scp`, `ls`, read small files. No local
  python. Speed login node: `sbatch`, `squeue`, `sacct`, `scancel`, `scp`, `ls`, single-file `cat`/`tail`/`wc -l`.
  Every job: `#SBATCH -p ps -t 7-00:00:00 --exclude=antenna1 -c 1 --mem=8G`, python
  `/speed-scratch/o_iseri/envs/step4/bin/python -u` (print python + numpy + pandas versions first). After `sbatch`: at
  most 6 checks, each ONE ssh call `sleep 30; sacct -j <id> -X --format=JobID,State,ExitCode,Elapsed,MaxRSS`; if not
  done, JobID in the Ledger with "manager to read" and stop.
* 🔴 UK licence: Spain and Italy only. The ONLY corpus is `G\_5J_data\surrogate\inputs\4J_step3_corpus_es_it.jsonl`
  (md5 1a5163445291b54114832e192b0d9a05); never the pooled `4J_step3_corpus.jsonl`, never any UK diary, episode,
  manifest, fold `uk` file, or anything built from UK diaries. No repo-wide or folder-wide search, no wildcard that
  could match a UK file: name every file in full. Before staging, list (from reading the trigger code) EVERY file
  the trigger opens for `--fold es` and `--fold it`; stage exactly those; if any is pooled or UK-derived (name has
  `uk`, or it holds rows of all three countries), stop: Status BLOCKED, say which file.
* Edit nothing under `4J_docs_occ\` or `OpenUBEM\`, nor any existing `tools/*.py`. New files only.
* Speed folder: `R=/speed-scratch/o_iseri/5J/households/` (create). Read-only: every other `5J/` folder.
* Past ~150k tokens: stop, write state, "handoff needed".

## Part A: Spain reproduction on Speed (gate before Italy)
Stage the trigger `tools/5thJ_step9_trigger_act2.py`, the 4J files it opens (keep the `4J_docs_occ/...` layout under
`R/repo/`), the ES+IT corpus, and `Step2_docs/outputs_step2/hids_es60.csv`. Run on Speed the es_60 command
(`--fold es --leg leg5 --year 2010 --seed 1 --households 100 --timestep 60 --shipped-suffix _cal2010 --hids
<hids_es60.csv> --out R/es_60`, default act2 rule; `--corpus` pointed at the staged ES+IT copy).
Gate A1: every output file of R/es_60 has the same md5 as `G\_5J_data\surrogate\wp1_hids\es_60\` (compute local
md5s with `certutil -hashfile <file> MD5` one file at a time, or stage the local folder and compare inside the job;
write which). Log lines `GUARD corpus OK`, `HIDS OK`, `PATCH act2 OK` PRESENT. If any md5 differs: Status BLOCKED,
first differing file and the first differing line (inside a job), no Italy run.
Seen failing: compare against a copy with one byte changed in one presence file (must print FAIL).

## Part B: Italy 60
Write `Step2_docs/outputs_step2/hids_it60.csv` (column `hid`, the 60 `it` hids of `households.csv` in `draw_order`,
same format as hids_es60.csv). Run `--fold it --leg leg5 --year 2014 --seed 1 --households 100 --timestep 60
--shipped-suffix _cal2014 --hids <hids_it60.csv> --out R/it_60`. Gates: 60 presence files; the hid set AND order of
`enduse_by_dwelling_it.csv` = hids_it60.csv; `GUARD`/`HIDS OK`/`PATCH act2 OK` lines PRESENT; stock mean
electricity per dwelling printed (compare with the `it_major` regression manifest value in
`Step2_docs/impl/2026-09-29_wp1_act2.md` if it gives one; INFO). Copy the small files (manifest json, log,
enduse_by_dwelling_it.csv) back to `G\_5J_data\surrogate\wp1_hids\it_60\`.

## Part C: household input folders for build_mz (Spain + Italy)
For every hid of both countries, write on Speed `R/inputs/<country>_<hid>/` with the files and numbers the pilot used
(`presence_HH_<hid>.csv`, `elec_HH_<hid>.csv`, `household.json` = {hid, country, n_members, appliance_peak_w,
md5 of each csv}), built exactly as `tools/5thJ_pilot_build.py` does (ported into a new Speed script
`tools/speed/hh_build.py`; the paths are the only change). Gate C1: for the 10 Spanish pilot hids, the files equal
(md5) those of `/speed-scratch/o_iseri/5J/pilot/inputs/es_B07__<hid>/` and n_members / design level equal the
pilot's `in.idf` People / ElectricEquipment values.

## Part D: average households (baseline B0), one per country
`R/inputs/<country>_avg/`: presence = hourly mean over the 60 households of the presence fraction; appliance
profile in W = hourly mean over the 60 of (fraction x design level); `appliance_peak_w` = max of that mean W
profile; `elec` fraction = mean W / appliance_peak_w; `n_members` = mean household size (a real number).
UNWEIGHTED mean (ASSUMED by the manager: the 60 were drawn with the survey weights, so their plain mean is the
stock estimate; write this in household.json). Gates: annual appliance kWh of avg = mean of the 60 annual kWh
(rel < 1e-9); presence in [0, 1]; 8,760 rows. Seen failing: scale one household's series by 1.01 before
averaging in a scratch copy (gate must FAIL).

## Report back (short)
A1 result (md5 equal y/n, count); Italy gates; C1; D gates; seen-failing lines; JobIDs; the Speed paths of
`R/inputs/`. Status DONE, Next = "manager verifies; campaign design (part 2) uses R/inputs".

## What the manager will re-derive
One Spanish file md5 Speed vs local; the Italian hid order; the avg annual appliance kWh against the 60.
