# Progress log — manifest union merge and round-3 re-run

Work dir: `4J_docs_occ/Step1_docs/outputs_step1/run_20260816-2140/`

## Task 1 — rename, then merge

- Backup `acquisition_manifest.json.bak_premerge_2026-08-16` already existed from
  the previous employee (104 lines, md5 `980f3991476b3f04bda5bf7f94769dcf`,
  byte-identical to the pre-merge `acquisition_manifest.json`). Verified
  non-empty; not overwritten.
- Copied the pre-merge `acquisition_manifest.json` to
  `acquisition_manifest_spain.json` (Spain's fragment, now correctly named).
- Wrote the merged root-keyed union to `acquisition_manifest.json`:
  `{"es": <Spain's entry, unchanged>, "it": <Italy's entry, unchanged>, "uk": <the UK's entry, unchanged>}`.
  No shape normalisation: Spain/Italy keep `files[]`; the UK keeps
  `outer_archive`/`inner_archive`/`delivered_files_md5`.
- The UK fragment's `_note` key was dropped in the merge, as instructed. Quoted
  in full:
  > "FRAGMENT ONLY. This is the 'uk' entry for acquisition_manifest.json,
  > written to a separate file per the work order so the parallel Italy
  > employee is not overwritten. The manager merges this into
  > acquisition_manifest.json under a top-level 'uk' key alongside the
  > existing 'es' entry. Shape copied from the existing Spanish entry; not
  > identical in every respect because the UK delivery arrived as a single
  > nested archive, not a set of separately-downloaded files -- see
  > 'shape_deviation_note'."

### Entry counts (fragment vs merged), computed programmatically

Counting rule: ES/IT = length of `files[]`; UK = `outer_archive`(1) +
`inner_archive`(1) + `delivered_files_md5[]`(N), since the UK has no `files[]`.

| country | fragment | merged | equal |
|---|---|---|---|
| es | 8 | 8 | yes |
| it | 4 | 4 | yes |
| uk | 19 (1 + 1 + 17) | 19 | yes |

### `local_path` / `local_root` verbatim comparison, programmatic

Two independent checks, both on the parsed JSON and on the raw file text
(regex-extracted `"local_path"`/`"local_root"` string values), comparing each
fragment file against its slice of the merged file:

- es: 9 local_path/local_root strings, all identical verbatim, 0 missing.
- it: 5 local_path/local_root strings, all identical verbatim, 0 missing.
- uk: 3 local_path/local_root strings (top-level `local_root`,
  `outer_archive.local_path`, `inner_archive.local_path` — the
  `delivered_files_md5[]` entries carry a `path` key, not `local_path`, so
  they are outside this check's scope by construction), all identical
  verbatim, 0 missing.

Result: no `local_path`/`local_root` string differs between any fragment and
the merged file.

Tooling: a local Python (`py`, 3.13.5) script was used for the merge and
verification, run on the local Windows workstation, not on the Speed login
node — the "no python on the login node" rule is cluster-specific and was
not violated.

## Task 2 — gate runner edits

Each edit is at the point where the manifest JSON is loaded (`json.load(fh)`),
immediately before it is stored into `ctx["manifest"]`. Nothing downstream of
the unwrapping (md5 logic, `resolve_manifest_path()`, the two problem
strings) was touched. The stale per-country `V1.a` print removed by the
previous employee was left untouched; `V1.b`/`V1.c`/`V1.d` untouched.

### `4thJ_gates_step1_spain.py`

Path unchanged (`acquisition_manifest.json` was already the correct filename
for Spain, only its shape changed). Before:
```python
    manifest = None
    if os.path.exists(inputs["manifest"]):
        with open(inputs["manifest"], encoding="utf-8") as fh:
            manifest = json.load(fh)
```
After:
```python
    manifest = None
    if os.path.exists(inputs["manifest"]):
        with open(inputs["manifest"], encoding="utf-8") as fh:
            manifest_root = json.load(fh)
        # M-6/round-3, 2026-08-16: acquisition_manifest.json is now the
        # root-keyed union of all three countries -- index into "es",
        # never fall back to reading the file flat.
        if "es" not in manifest_root:
            raise SystemExit(f"acquisition_manifest.json has no 'es' key -- "
                              f"cannot locate Spain's entry in the union "
                              f"manifest")
        manifest = manifest_root["es"]
```

### `4thJ_gates_step1_italy.py`

Path changed. Before:
```python
        "manifest fragment": os.path.join(out, "acquisition_manifest_italy.json"),
```
After:
```python
        "manifest fragment": os.path.join(out, "acquisition_manifest.json"),
```
And the load. Before:
```python
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest = json.load(fh)
```
After:
```python
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest_root = json.load(fh)
        # M-6/round-3, 2026-08-16: acquisition_manifest.json is now the
        # root-keyed union of all three countries -- index into "it",
        # never fall back to reading the file flat.
        if "it" not in manifest_root:
            raise SystemExit(f"acquisition_manifest.json has no 'it' key -- "
                              f"cannot locate Italy's entry in the union "
                              f"manifest")
        manifest = manifest_root["it"]
```

### `4thJ_gates_step1_uk.py`

This runner already unwraps a `"uk"` key downstream (`man.get("uk", {})`,
used in several places), so this was a path change plus a guard, not a
rewrite of the unwrapping itself. Path, before:
```python
        "manifest fragment": os.path.join(out, "acquisition_manifest_uk.json"),
```
After:
```python
        "manifest fragment": os.path.join(out, "acquisition_manifest.json"),
```
Load, before:
```python
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest = json.load(fh)
```
After:
```python
    manifest = None
    if os.path.exists(inputs["manifest fragment"]):
        with open(inputs["manifest fragment"], encoding="utf-8") as fh:
            manifest = json.load(fh)
        # M-6/round-3, 2026-08-16: acquisition_manifest.json is now the
        # root-keyed union of all three countries. This file already
        # unwraps a "uk" key downstream (man.get("uk", {})) -- just refuse
        # to proceed silently if that key is now absent, never fall back
        # to reading the file flat.
        if "uk" not in manifest:
            raise SystemExit(f"acquisition_manifest.json has no 'uk' key -- "
                              f"cannot locate the UK's entry in the union "
                              f"manifest")
```
Everything below this (the two `man = ctx["manifest"]; uk = man.get("uk", {})`
call sites, the perturbation blocks, `gate_g16a`/`gate_g16b`) is byte-for-byte
unchanged.

All three edited files were syntax-checked locally with
`py -m py_compile 4thJ_gates_step1_spain.py 4thJ_gates_step1_italy.py
4thJ_gates_step1_uk.py` — no errors.

`4thJ_vacuity_step1.py` was inspected and confirmed to contain no
`acquisition_manifest` reference at all; it was not edited, only re-deployed
(Task 3) so the cluster copy matches the workstation copy.

## Task 3 — deploy and round 3

- New run stamp: **`run_20260816-2210`** (current local time was
  2026-08-16 22:09 EDT / 2026-08-17 02:09 UTC at submission).
- Created `/speed-scratch/o_iseri/4J/outputs_step1/run_20260816-2210/` on the
  cluster.
- `scp`'d to `/speed-scratch/o_iseri/4J/tools/`:
  `4thJ_gates_step1_spain.py`, `4thJ_gates_step1_italy.py`,
  `4thJ_gates_step1_uk.py`, `4thJ_vacuity_step1.py`.
- `scp`'d to the cluster's flat `/speed-scratch/o_iseri/4J/outputs_step1/`:
  the new merged `acquisition_manifest.json` and `acquisition_manifest_spain.json`.
- Round 2's job scripts (`4J_gates16_{spain,italy,uk}_r2.sh`,
  `4J_vacuity_step1_r2.sh`, found on the cluster at
  `/speed-scratch/o_iseri/4J/tools/`) were used as the model for round-3
  equivalents (`..._r3.sh`), same `--raw` = COUNTRY ROOT convention
  (M-6, round 2) kept unchanged. The only content difference from round 2,
  besides the job name/output path/run stamp: the Italy and UK scripts now
  `cp` the flat `acquisition_manifest.json` (the union) into `$OUT` instead
  of their old per-country fragment filename, since their gate runners now
  read that filename. The Spain script's `cp` line was already
  `acquisition_manifest.json` and needed no change.
- Submitted four jobs, `-p ps -t 7-00:00:00` throughout:

| job | job ID |
|---|---|
| ES gates | 1252724 |
| IT gates | 1252726 |
| UK gates | 1252727 |
| vacuity (`--dependency=afterok:1252724:1252726:1252727`) | 1252728 |

Single `sacct -j 1252724,1252726,1252727,1252728` call, taken immediately
after submission (no polling):

```
JobID           JobName      State              Submit
------------ ---------- ---------- -------------------
1252724      4J_g16_es+    RUNNING 2026-08-16T22:10:58
1252726      4J_g16_it+    RUNNING 2026-08-16T22:11:00
1252727      4J_g16_uk+    RUNNING 2026-08-16T22:11:01
1252728       4J_vac_r3    PENDING 2026-08-16T22:11:03
```

ES, IT and UK were RUNNING; the vacuity job was PENDING on its dependency, as
expected.

## What the manager will check when the jobs land

- `G1.6a` must still PASS on all three countries, reading the merged
  manifest.
- `corrupt_archive_byte` must still fell `G1.6a` on all three.
- `strip_url_from_manifest` must still fell `G1.6b` on the UK.
- Italy's `G1.6b` baseline FAIL and the UK's `G1.4` `4276` baseline FAIL must
  both still be there. If either clears, the merge broke something and the
  round is rejected.
- `V1.a` must PASS 3 of 3 from the round-level `vacuity_report_step1.txt`,
  and the three per-country reports must now contain no `V1.a` verdict line
  at all.

## What was NOT independently verified

- The jobs were not waited on or polled after the single `sacct` call above;
  no gate report, no `out_*.txt`, and no `vacuity_report_step1.txt` from
  round 3 has been read. Every claim in "What the manager will check" above
  is a restatement of the requirement, not a confirmed round-3 result.
- The edited Python files were syntax-checked (`py_compile`) but never
  executed anywhere, locally or on the cluster, before submission — no
  local run of any gate logic against real data.
- The `md5` recorded in the merged `acquisition_manifest.json` for every
  archive was not independently recomputed against the files on disk in
  this task; Task 1's verification covers `local_path`/`local_root` string
  identity and entry counts only, not md5 correctness (that is `G1.6a`'s job
  and will only be confirmed once the round-3 gate reports are read).
  Note the `it`/`uk` per-country entry-count check above also assumes the
  counting rule stated (files[] for es/it; outer+inner+delivered_files_md5
  for uk) is what `G1.6a` itself iterates over for each country — this was
  read from the gate source at `4thJ_gates_step1_spain.py:471` and
  `4thJ_gates_step1_italy.py:321` (`for entry in man["files"]`) but the UK's
  own G1.6a loop body was not re-read line-by-line to confirm it iterates
  exactly `outer_archive` + `inner_archive` + `delivered_files_md5[]` and
  nothing else.
- No diff was taken between the round-3 `4thJ_gates_step1_*.py` files
  deployed to the cluster and the round-2 versions already there beyond the
  three sections edited in this task — i.e. no confirmation that round 2's
  cluster copies were otherwise identical to this workstation's pre-edit
  copies before the edits were layered on and re-deployed.
- The three round-3 job scripts were not diffed byte-for-byte against
  round 2's beyond the sections described above; whitespace/other
  incidental differences from the `sed`-stripped line endings were not
  checked beyond confirming the files parse as valid Bash scripts and
  `sbatch` accepted them without error.
