## Round 2, Step 1 sixteen-gate re-run (2026-08-16, employee)

**What was changed.** Ported M-6 and M-7 from the UK reference implementation
(`4thJ_gates_step1_uk.py`, already carrying both, untested until now) into
`4thJ_gates_step1_spain.py` and `4thJ_gates_step1_italy.py`. M-6:
`resolve_manifest_path()` added to both files; `G1.6a` now resolves every
manifest entry's `local_path` relative to the manifest's own `local_root`,
under `--raw` at invocation time, never taking `local_path` literally; two
distinct problem strings verbatim from the UK file (`md5 mismatch` /
`recorded location not resolvable under --raw`); `local_path`/`local_root`
are read only, never rewritten, in any of the three manifest fragments. M-7:
`Result.subclauses`, per-field `codes_outside_list` returned from `G1.4`,
`SUBCLAUSE_FIELD_FOR_PERTURBATION` mapping, and the additive sub-clause
fallback in the perturbation loop -- ported for shape parity with the UK
file; not expected to engage for Spain or Italy this round because neither
country's `G1.4` FAILs at baseline (confirmed below), so there is no masked
arm for it to recover there.

One addition beyond the literal task list, discovered during TASK 5's local
dry run, not from any doc read: Spain's and Italy's raw trees keep their
unpacked files under an `unpacked/` sub-directory of the country root, not
at the country root directly (same layout the UK already has). Because M-6
needs `--raw` to be the country root (to match the manifest's
`local_root`), while the gate runners' own raw-file re-reads (`DIARIO2.TXT`
etc. for Spain, `MICRODATI`/`METADATI` for Italy) need the `unpacked/`
sub-directory, both gate runners now split `--raw` the same way the UK file
already did: `--raw` is the country root, and `unpacked_dir =
os.path.join(args.raw, "unpacked")` is derived internally for the raw
re-reads only. This changes the sbatch invocation convention for Spain and
Italy's gate runners (round 1 passed the `unpacked/` dir as `--raw`; round 2
passes the country root) -- the same class of bug the UK file's M-6 exists
to fix, just not yet triggered for Spain/Italy in round 1 because neither
had M-6 code to be wrong about `--raw` yet.

Wrote `tools/4thJ_vacuity_step1.py`: scores `V1.a` once per round from the
run-stamped `--out` dir (FAIL below 3 of 3 countries with an
`episodes_<country>.parquet` present), writes `vacuity_report_step1.txt`.
`V1.b`/`V1.c`/`V1.d` were NOT moved -- they stay inside each country's own
gate runner, per the manager's 2026-08-16 decision that moving them would
make them unfalsifiable.

Chose run stamp `run_20260816-2140`, `Step1_docs/outputs_step1/run_20260816-2140/`
(cluster path `/speed-scratch/o_iseri/4J/outputs_step1/run_20260816-2140/`),
passed explicitly into all four job scripts. Static reference inputs
(crosswalks, manifest fragments, codebook facts, the Spain population
reference) are copied read-only from the flat `outputs_step1/` into the run
dir by each job script before the reader/gate runner run; nothing is copied
back into the flat directory and nothing already there was overwritten.

**Acceptance tests -- all five checked by a LOCAL dry run of the patched
tools (Windows box, `--raw` pointed at `_local_runs/4J/raw/<country>/`),
BEFORE the code was deployed to the cluster and the round-2 Speed jobs were
submitted:**

1. `corrupt_archive_byte` newly failed `G1.6a` on all three countries in the
   local dry run (Spain: `failed ['G1.6a'] -> as pre-registered`; Italy:
   `newly-failed ['G1.6a'] -> as pre-registered`; UK: `failed ['G1.4',
   'G1.6a'] ... -> as pre-registered`, `G1.6a` itself PASS at baseline on
   all three). MET, locally.
2. `null` moved nothing on Spain locally: `failed [] -> as pre-registered`.
   MET, locally.
3. M-7 recovered all four UK arms masked by the deliberate `G1.4` 4276 FAIL
   in the local dry run: `act_to_outside_list`, `act2_to_outside_list`,
   `act2_extra_2_to_outside_list` and `loc_undeclared_sentinel` each printed
   `FIRED (sub-clause level, M-7): G1.4.<field> went [...] -> [...].
   Overall gate status unchanged (FAIL both times)`. MET, locally.
4. Every `NOT CHECKED` in the local dry run reports carried its one-line
   reason (`G1.7b` all three countries, `G1.7c`/`G1.8` Italy, `G1.7b`/`G1.8`
   UK) -- none printed a bare `NOT CHECKED` with no detail. MET, locally.
5. `loc_undeclared_sentinel` felled `G1.4` and `weight_blank_on_productive_row`
   felled `G1.7a`, as pre-registered, on all three countries in the local
   dry run -- neither reports `DID NOT FIRE`; M-1 and M-3 are NOT reversed.
   MET, locally.

**What was NOT independently verified.** The round-2 Speed jobs
(`1252522` ES, `1252523` IT, `1252524` UK, `1252525` vacuity,
`--dependency=afterok:1252522:1252523:1252524`) were RUNNING (per one
`sacct` call, `0:0`, under 15s elapsed) at the time this fragment was
written; per instruction, the cluster run was not waited on. Everything
above is a local-dry-run result on the same code now deployed to
`/speed-scratch/o_iseri/4J/tools/`, not a reading of the cluster's own
`gate_report_step1_<country>.txt` or `vacuity_report_step1.txt` for this
round. Also not independently verified: byte-identity between the scp'd
cluster copies of the three gate runners / `4thJ_vacuity_step1.py` and the
local repo copies (no md5 check was run -- not an allowed login-node
command this round); that the static reference files already sitting in
the cluster's flat `outputs_step1/` (crosswalks, manifests, codebook facts,
the ES population reference) are byte-identical to the ones the local dry
run used; Italy's `G1.6b` baseline FAIL and the UK's `G1.4` `4276` FAIL are
both UNTOUCHED BY DESIGN and were only re-observed locally, not re-derived
from a fresh cluster run.
