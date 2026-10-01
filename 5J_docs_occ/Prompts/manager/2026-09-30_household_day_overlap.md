# Do 5J development and test households share diary days? (read-only review)
Stamp: Wed 2026-09-30 21:26 EDT. Spain and Italy only. No UK file opened. No data file opened; only code/docs and `ls`/`grep -m` of Speed names.

## Short answer
YES, they share. A 5J household-year is NOT built from the household's own diary days. Every person-day is drawn, with replacement, from ONE shared pool of 5,200 GENERATED days per country (4J model output, not real HETUS rows). The pool is the same for dev, val and test households.

## (1) How a household-year is built (file:line)
- Households = real HETUS households, but only for COMPOSITION (hid, member strata): `4thJ_step7_schedules.py:440-482` (docstring: "composition is DATA ... only the DAYS are generated"). 5J selects the 60 hids with `--hids`: `5thJ_step9_trigger_act2.py:745-747`.
- Pool = `generated_leg5_<es|it>_constrained.jsonl`, loaded once: `5thJ_step9_trigger_act2.py:721-726`; manifest says `n_days 5200`, `pool_file generated_leg5_es_constrained.jsonl` (es_60/step9_manifest_es.json). `wp1_wrapper.md:38` confirms 5200.
- Pool is bucketed by (age band, sex, household type, economic status, day type) with back-off: `4thJ_step7_schedules.py:198-199, 245-263`.
- Each person, each calendar day: `rng.choice(bucket)` (replacement), rule "independent": `4thJ_step7_schedules.py:266-304`; called per household, per member, with ONE `random.Random(seed)` running across all households in list order: `5thJ_step9_trigger_act2.py:737-751`.
- Household presence = sum over members of those days: `4thJ_step7_schedules.py:321`.
- Split (40 dev / 10 val / 10 test) is a label on households only: `campaign_design.md` section 2 (`splits_households.csv`). The pool is not split-aware (no split argument anywhere in the build path).
- Appliance loads (the `elec_HH_*` files) come from the same pool days (eligible minutes, `step9_trigger_act2.py:221-312`), so they inherit the overlap.

## (2) Verdict
- Two households sharing a day: YES (365 draws per person from buckets holding a few to a few hundred days; same bucket = same day reused, even inside one person).
- Different splits drawing from the same pool: YES, one pool per country, shared by all splits.
- What is NOT shown: a test household's own surveyed diary is not used at all, so there is no leak of the household's own real day. The leak is of the shared generated days (same strata -> same days).
- UNCLEAR (not checked): whether the 5,200 generated days were produced by a model that saw the test households' real diaries. That is a 4J LOCO question (`4thJ_07_constrainedGeneration.md`, LOCO notes at lines ~516, 596); `provenance` is null in the manifest.

## (3) Concrete check (sbatch, Spain and Italy only, no UK path)
Aim: count pool days used by BOTH a dev and a test (and val) household, per country.
Inputs (named files only):
- `/speed-scratch/o_iseri/5J/households/repo/generated_leg5_{es,it}_constrained.jsonl` (the pool; day id = position of the day in `pools[0]` bucket order, or its json line number).
- `/speed-scratch/o_iseri/5J/households/repo/4J_step3_corpus_es_it.jsonl` (fields hid, pid, country, text prefix; es/it only, copy already UK-free).
- `.../repo/5J_docs_occ/Step2_docs/outputs_step2/hids_es60.csv` and the `it` twin (hid order = draw order); `splits_households.csv` (same folder) for hid -> split (column names to be read by the job, not verified here).
Method: sbatch -p ps -t 7-00:00:00 on `5thJ_step9_trigger_act2.py`'s functions: replay `build_dwellings` with the same seed and `--hids` list, and wrap `s7.draw` so each call logs (hid, pid, day_of_year, pool_day_id, depth). Check first that the replay reproduces `es_60/presence/presence_HH_es_<hid>.csv` for 3 hids (md5), otherwise the ids are not the shipped ones.
Outputs: per country (a) number of distinct pool days used by dev, val, test; (b) size of the intersection dev vs test and dev vs val; (c) share of test household-days whose pool day was also used by some dev household; (d) the same for the 40 dev hids split in half as a null reference.
Cheaper bound without replay: for every test person, count pool days in its stratum bucket that dev persons can also reach (bucket sizes from the pool file alone); if buckets are small, overlap is certain.
Note: replay needs python, so it is an sbatch only. Nothing was run here.

## (4) Files opened
Local: `5J_docs_occ/Step2_docs/impl/2026-09-29_wp1_households_v2.md`, `.../2026-09-29_wp1_wrapper.md`, `.../outputs_step2/campaign_design.md` (grep only), `5J_docs_occ/tools/5thJ_step9_trigger_act2.py` (lines 575-860, grep), `4J_docs_occ/tools/4thJ_step7_schedules.py` (lines 95-305, 440-483), `4thJ_07_constrainedGeneration.md` (grep). Speed: `ls` of households/ and tools/, `ls` of repo, `grep -m` of es_60/step9_manifest_es.json, `grep -n` of tools/hh_build.py (not about days), `grep -c` hids_es60.csv. 4J Step 9/10 docs only listed, not read.
