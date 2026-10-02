# 9n: a second employee ran the same task at the same time (note from the later-started employee, 2026-10-01 ~20:44 EDT)
Two agents were given the same task doc. Both wrote to `tools/speed/a9_store.py`, the state file, the shared scratchpad file `campaign_block.py` and `wp9n/`.
The other employee's version is far ahead (a9_store.py 1,506 lines, `build_campaign` / `campaign_test`, test logs `campaign_test_run*.log` in this folder), so this employee STOPPED and left
`a9_store.py` and the state file to it. Nothing of this employee's code was installed in `a9_store.py`. Kept only: `employee_B_unused_test_block.py.txt` (a test plan with controls, not wired to the other version).
What this employee did that is still in place: copied the 36 smoke results to `smoke_copy/` (results json, npz of the 21 clean runs, placement / series.tar.gz / eplusout.end of the clean runs, b0 series, EPW, zone map),
wrote the "Step 1 inputs" table at the top of the state file, saved `tools/speed/a9_store_pre9n.py` (md5 ff9ab2f32d5beb47c8ae358d2f2b21c2 = the 9k version).
Manager: read the other employee's state file and logs, not this note, for results; a9_store.py was being edited at 20:43:37, check it is quiescent before you copy it to Speed.
Findings this employee had reached independently (same as the state file): 13 runs must be stored out of 36 (21 clean, 8 test-pool / test-building runs among them... see state file), series csv paths in placement.csv are dead
(series folder deleted; read from series.tar.gz or the b0 folder), the same hid has a different series in every run (run seed), so household rows must be per (run, hid), which raises hh file size above the 9g number.
