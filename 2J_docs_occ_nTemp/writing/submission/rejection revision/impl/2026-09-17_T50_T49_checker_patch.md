# T50 — patch the T49 checker before it runs: log integrity (B3b) and a parse echo for B4

Task doc:   this file.
Upstream:   `2026-09-17_T49_T22_collector.md` (the checker, job **1329278**, PENDING on
            `afterany:1328310`), `2026-09-15_T22_wp3_static_arm_full_run.md` (the run being scored).
Status:     DONE

## Why this task exists

The T49 employee built the checker, submitted it as job **1329278**, and disclosed two real gaps in its own
`## WHAT I DID NOT VERIFY`. The manager has read them and agrees both are genuine holes that would let a
wrong answer look like a right one. They must be closed **before** the job runs, and they can be, because
`1329278` is still `PENDING (Dependency)` — manager-verified by `squeue -j 1329278` — and SLURM only copied
the `.sh` wrapper at submit time. The python file `t49_check.py` is read fresh from disk when the job
starts, so replacing it now changes what the pending job will do, with no resubmission.

**Gap 1 — GATE_B3 can pass on a log that does not exist as a real log.** B3 greps 24 task logs for
`schedule.json not found` and passes when the count is zero. A zero-byte, missing, or truncated `.out` file
also greps to zero. "No evidence of the bug" and "no evidence at all" would be reported identically, and the
second one is not a PASS.

**Gap 2 — the B4 control does not exercise the T22-side parse.** The control's un-mutated baseline is built
from the published manifest's own IDs (a sound choice, accepted — see the T49 Decisions), so it proves the
set-comparison logic works, but both sides of that comparison come from the published file. If the checker
read T22's `cell_manifest.csv` wrongly — wrong column, empty set, a type mismatch — the control would still
fire and the real B4 would report a large mismatch that is a parsing bug wearing the costume of a finding.
The T49 employee already spot-checked one real mismatch by hand (T22 `32815` vs published `33298` for
`SingleD__Toronto_5A` sample_001), so a real difference probably exists; that is exactly why the checker must
prove it read real values before the manager is allowed to believe the number.

## Design (manager, fixed — do not redesign, do not refactor anything else)

Two additions to `t49_check.py`. Nothing else in the file changes: not the gate definitions, not the three
existing controls, not the report labels already in the T49 Ledger, not the B4 reference file choice
(`/speed-scratch/o_iseri/step9_run/step9_manifest.csv` stays). Do not reformat, rename, or tidy.

### Addition 1 — GATE_B3b, log integrity, scored before B3 is believed

For each of the 24 expected `t22_1328310_<i>.out` files, `i = 0..23`, record: exists yes/no, byte size, line
count. Print:

- `GATE_B3b: logs_present=<n>/24 logs_nonempty=<n>/24`
- one `B3b_OFFENDER: <filename> missing|zero_bytes|<size> bytes` line per offender
- `VERDICT_B3b: PASS|FAIL` — PASS only when all 24 exist and all 24 are non-empty.

And make B3 honest about it: if B3b fails, print
`GATE_B3: NOT_EVALUABLE for <k> task(s) — <list>` alongside the occurrence count for the tasks that do have
a real log, and set `VERDICT_B3: NOT_EVALUABLE` rather than PASS. A clean grep over a log that is not there
is not evidence. Do **not** invent a completion-marker check — nobody has established what the wrapper
prints at the end, and a guessed marker would create a false FAIL. Existence and non-emptiness only.

The `.err` files are **not** part of B3b. An empty `.err` is the normal, good outcome and failing on it
would be a false alarm.

### Addition 2 — B4_PARSE_ECHO, so a parse bug cannot pose as a finding

Before scoring GATE_B4 on the real tree, for **every** cell print one line:

`B4_PARSE_ECHO: <cell> t22_n=<len of T22 ID set> pub_n=<len of published ID set> t22_first5=<5 sorted IDs> pub_first5=<5 sorted IDs>`

and add a parse guard that is separate from the mismatch verdict:

- if either side's set size is not 50 for a cell, that cell is a `B4_PARSE_OFFENDER: <cell> t22_n=<n> pub_n=<n>`
  and is counted as `NOT_EVALUABLE`, **not** as a mismatch;
- `GATE_B4: cells_matching=<n>/24 cells_mismatching=<n>/24 cells_not_evaluable=<n>/24`;
- `VERDICT_B4: PASS|FAIL|NOT_EVALUABLE` — `NOT_EVALUABLE` if any cell hit the parse guard.

The point of the echo is that the manager can read five real five-digit household IDs from each side and see
with their own eyes that both sides were read, before reading any mismatch count. A mismatch reported with
`t22_n=0` is a bug; a mismatch reported with `t22_n=50, pub_n=50` and two different-looking ID lists is a
finding.

## Rules you must follow (read all of this, it is not boilerplate)

**Login node.** The only commands allowed on the Speed login node are: `sbatch`, `squeue`, `sacct`,
`scancel`, `scontrol`, `cd`, `ls`, `scp`, `module load`, `mkdir`, and single-file `tail` / `head` / `grep` /
`wc -l` / `cat`. **Nothing else.** `python`, `python3`, `find`, `du`, `md5sum`, `wc -l` over a glob, and
shell loops over directories are all **forbidden** there — `find` explicitly included. This account has been
flagged three times; one more flag suspends it and loses every running job.

**Shell.** The login shell is **tcsh**. Never put `2>&1` or `2>/dev/null` inside an `ssh` command string —
it fails with `Ambiguous output redirect`. ssh with `-o BatchMode=yes -o ConnectTimeout=60`.

**Do not submit any job.** This task submits nothing and cancels nothing. `1329278` stays exactly as it is.
Never `scancel` it. If you find it is no longer `PENDING`, stop — see step 4.

**Keep the original.** Before replacing the remote file, keep the un-patched version beside it as
`t49_check_v1.py` (local and remote). The ledger is append-only and so is the evidence trail.

**Local checks only:** `py -3 -m py_compile` and `bash -n`. Local python is `py -3` on this machine. No
local execution of the checker — there is no local copy of the T22 tree to run it against.

**Submit nothing, wait for nothing, end your turn** once the patched file is in place and this doc is
filled in. No background polling, no `sleep`.

## Brief (employee, Sonnet)

1. **Find the checker.** Locate the local `t49_check.py` and `t49_check.sh` (the T49 employee wrote them
   under a `T49_scripts/` directory — use Glob, do not guess). If no local copy survives, `scp` the remote
   copy back from `/speed-scratch/o_iseri/2J_revision/T49/` and say so in `## Decisions`. Read the whole
   file before changing a line of it.
2. **Confirm the job is still pending, and that this patch is therefore still safe:**
   `squeue -j 1329278 -o '%.12i %.9T %.20R'`. It must read `PENDING (Dependency)`. Record the output.
3. **Make the two additions** exactly as the Design section specifies. Preserve every existing report label
   character-for-character — the T49 Ledger already promises them to the manager. Then
   `py -3 -m py_compile t49_check.py` and `bash -n t49_check.sh`.
4. **Re-check `squeue -j 1329278` immediately before copying**, then `scp` the original aside as
   `t49_check_v1.py` and `scp` the patched `t49_check.py` into
   `/speed-scratch/o_iseri/2J_revision/T49/`, then **re-check `squeue -j 1329278` once more**. Record all
   three reads. If at any point the job is no longer PENDING, **stop, change nothing further, and write in
   the Ledger that the patch was abandoned because the job had started** — a half-replaced python file under
   a running job is the one outcome worth avoiding. In that case leave the patched file only locally and say
   so; the manager decides whether to rerun.
5. `ls -l` the remote `T49/` directory (allowed) to prove both files landed with plausible sizes, and record
   it. Fill in `## Ledger`, `## Verified`, `## Decisions`, `## Next`, `## WHAT I DID NOT VERIFY`, set Status
   to DONE, and end your turn.

## Acceptance (what the manager will check)

- `t49_check.py` on Speed contains B3b and B4_PARSE_ECHO, and nothing else moved.
- `1329278` was PENDING before, between and after the copy, with all three reads quoted.
- The un-patched version is preserved as `t49_check_v1.py`, locally and remotely.
- No job was submitted, cancelled or held. No forbidden login-node command was run.

## Ledger
(append-only; one line per cluster job or remote change: what, when, what was read)

- **No local copy of `t49_check.py`/`t49_check.sh` survived** in this working tree (Glob for
  `T49_scripts/**` and `t49_check*` found nothing). Per Brief step 1, pulled both files back from
  `/speed-scratch/o_iseri/2J_revision/T49/` via `scp` into the local scratchpad
  (`.../scratchpad/T49_scripts/`) before touching anything. Recorded here and in Decisions.
- **squeue read #1** (before any edit), `squeue -j 1329278 -o '%.12i %.9T %.20R'`:
  `1329278   PENDING         (Dependency)`.
- Read the whole checker (`t49_check.py`, 339 lines) and its wrapper (`t49_check.sh`) before changing
  a line. Confirmed the wrapper invokes the python file with `> .../t49_check_report.txt 2>&1`, so
  stdout ordering in the patched file is exactly what lands in the report.
- Made the two Design-section additions in the local copy (details in Verified/Decisions below), then
  ran `py -3 -m py_compile t49_check.py` -> `PY_COMPILE_OK` and `bash -n t49_check.sh` -> `BASH_N_OK`
  (the `.sh` wrapper itself was not touched, this was a pure syntax check of the unmodified file).
- **squeue read #2** (immediately before scp), same command: `1329278   PENDING         (Dependency)`.
- Reconstructed the pre-edit file byte-for-byte from the first `Read` (before any `Edit` call touched
  it) and wrote it locally as `t49_check_v1.py`; verified it is IDENTICAL by re-`scp`-ing the
  still-untouched remote original to a throwaway file and running `diff` (`diff` exit 0, printed
  `IDENTICAL`) before trusting it as the preserved copy. Deleted the throwaway file afterward.
  (One extra, harmless `squeue -j 1329278` check was also run at this point while verifying network
  reachability — also `PENDING (Dependency)` — in addition to the three formally required reads.)
- `scp`'d the verified-identical original up to
  `/speed-scratch/o_iseri/2J_revision/T49/t49_check_v1.py` (preserve remotely), then `scp`'d the
  patched local `t49_check.py` over
  `/speed-scratch/o_iseri/2J_revision/T49/t49_check.py` (the file the pending job will read).
- **squeue read #3** (immediately after the scp), same command: `1329278   PENDING         (Dependency)`.
  Job never left PENDING across all three reads — patch is safe, nothing was submitted, cancelled, or
  held.
- `ls -l /speed-scratch/o_iseri/2J_revision/T49/`:
  `t49_check.py` 17119 bytes (patched, matches local patched file size), `t49_check_v1.py` 13416 bytes
  (matches the size first seen when the original was pulled back, and matches the local reconstructed
  copy's size), `t49_check.sh` 1092 bytes (untouched), plus a pre-existing `T49_scripts/` leftover
  directory from the original T49 employee's `scp -r` (not touched — the job's own wrapper already
  `rm -rf`s it at runtime; login node forbids `rm` anyway and it is out of scope for this task).

## Verified
(numbers actually read, and where each was read from)

- Original `t49_check.py` = 13416 bytes, `t49_check.sh` = 1092 bytes, read via the first `scp` +
  local `ls -la`.
- `squeue -j 1329278` read three times as required: PENDING (Dependency) before edit, immediately
  before the scp, and immediately after — all three identical, quoted above in the Ledger.
- Patched `t49_check.py` compiles clean: `py -3 -m py_compile` produced no output/errors (printed
  `PY_COMPILE_OK` sentinel after it). `bash -n t49_check.sh` likewise clean.
- Post-copy `ls -l` on `/speed-scratch/o_iseri/2J_revision/T49/`: `t49_check.py` 17119 bytes,
  `t49_check_v1.py` 13416 bytes, `t49_check.sh` 1092 bytes — all plausible (patched file grew by
  ~3.7 KB for the two additions; preserved original is byte-identical in size to the pre-edit file).

## Decisions
(anything this doc did not decide, and what you assumed)

- **No local copy survived** — per Brief step 1's fallback, `scp`'d both `t49_check.py` and
  `t49_check.sh` back from `/speed-scratch/o_iseri/2J_revision/T49/` into a local scratchpad
  `T49_scripts/` directory before reading or editing. This is disclosure per the Brief's own
  instruction, not a deviation.
- **Existing print labels were kept literally where they already exist; new Design-section labels
  were added exactly as spelled in the Design section, even though the Design section's own prose
  uses an underscore-colon convention (`VERDICT_B3:`, `VERDICT_B4:`) that does not match the code's
  actual existing convention (`VERDICT: B3=`, `VERDICT: B4=`).** I read the Design section's
  `VERDICT_B3`/`VERDICT_B4` mentions as descriptive shorthand for "the B3/B4 verdict," not as a
  literal new print string, because (a) rule 6 says every existing label must survive
  character-for-character and (b) the Design section uses that same shorthand for the *existing* B3
  verdict, which the code has never printed that way. So: `VERDICT: B3=` and `VERDICT: B4=` keep
  their exact original text, and their *value* can now be `NOT_EVALUABLE` in addition to `PASS`/
  `FAIL`. `GATE_B3b`/`VERDICT_B3b`/`B3b_OFFENDER`/`B4_PARSE_ECHO`/`B4_PARSE_OFFENDER` are brand-new
  labels with no prior collision, so those are printed exactly as the Design section spells them.
  `GATE_B4: cells_matching=<n>/24 ...` keeps its original prefix and simply has
  `cells_mismatching=`/`cells_not_evaluable=` appended to the same line, per the Design section's
  literal extended format.
- **B3 verdict logic when B3b fails**: the Design section says "no evidence of the bug" and "no
  evidence at all" must not be reported identically, and says to set the B3 verdict to
  `NOT_EVALUABLE` "rather than PASS" when B3b fails. I read "rather than PASS" as scoped to the case
  where the grep genuinely found zero occurrences among the logs that DO exist — if a real
  occurrence of `schedule.json not found` is found in a log that does exist, that is real evidence
  and the verdict stays `FAIL` regardless of B3b, since downgrading a real FAIL to NOT_EVALUABLE
  would hide a genuine finding. This is not spelled out verbatim in the Design section but follows
  directly from its own stated reasoning ("no evidence of the bug" vs "no evidence at all" — a real
  hit is evidence, not an absence of it).
- **`B3b_OFFENDER` reason text**: the Design section's format is
  `<filename> missing|zero_bytes|<size> bytes`, which reads as three pipe-separated alternatives but
  the only two failure states B3b can actually detect are "missing" and "size == 0." I printed
  `missing` for the missing case and `zero_bytes (0 bytes)` for the empty case, so the literal text
  `zero_bytes` and the literal `<size> bytes` pattern (`0 bytes`) both appear and are both greppable,
  rather than guessing which of the three alternatives the manager meant to be exclusive.
- **B4 parse-guard interaction with the pre-existing "manifest entirely missing" case**: that case
  already existed in the real B4 loop (`reason=t22_manifest_missing`) and was not something the
  Design section asked me to change. A missing T22 manifest naturally yields a T22 ID set of size 0,
  which is `!= 50`, so it now also falls into the new parse guard and is counted as
  `cells_not_evaluable` (not as a mismatch) — this is the literal, unforced consequence of the stated
  rule ("if either side's set size is not 50 for a cell"), not a redesign of the missing-manifest
  case. Both the old `B4_OFFENDER: ... reason=t22_manifest_missing` line and the new
  `B4_PARSE_OFFENDER` line print for that cell.
- **`B4_PARSE_ECHO` is printed for all 24 cells**, including ones where the T22 manifest is entirely
  missing (using `t22_n=0`, `t22_first5=[]`), since the Design section says "for every cell" without
  carving out an exception, and printing `t22_n=0` for that case is itself informative (matches the
  brief's own example: "a mismatch reported with `t22_n=0` is a bug").
- Did not rename, reformat, or touch `check_b4_cell`, `build_b2_control`, `build_b3_control`,
  `build_b4_control`, the three controls, or any `CONTROL_B*` line — all untouched, verified by
  reading the full diff mentally against the preserved `t49_check_v1.py`.
- `t49_check.sh` was read for `bash -n` but not modified — the Design section's two additions are
  both inside `t49_check.py` only.

## Next
(the exact next action, written so a cold agent can start there)

- Nothing further for this task. When job 1329278 eventually runs (after 1328310's last two tasks
  finish and the checker's own controls fire), its report at
  `/speed-scratch/o_iseri/2J_revision/T49/logs/t49_check_report.txt` will now also contain
  `GATE_B3b`/`VERDICT_B3b`/`B3b_OFFENDER` lines before the `GATE_B3` section, and
  `B4_PARSE_ECHO`/`B4_PARSE_OFFENDER` lines plus an extended `GATE_B4:` line before the B4 verdict.
  A cold agent reading that report should grep for `VERDICT_B3b` and the `B4_PARSE_OFFENDER` lines
  first — if `VERDICT_B3b: FAIL` or any `B4_PARSE_OFFENDER` line appears, treat `VERDICT: B3=` /
  `VERDICT: B4=` as `NOT_EVALUABLE` evidence-quality caveats before quoting any PASS/FAIL number to
  the manager, exactly as this patch's `VERDICT:` line values now already encode.
- The preserved pre-patch behavior (`t49_check_v1.py`, both locations) is available if the manager
  ever wants to diff or revert.

## WHAT I DID NOT VERIFY

- **I did not run the patched checker anywhere**, locally or remotely, per the rules (no local T22
  tree or published manifest exists to run it against, and the remote job must not be triggered
  early). `py -3 -m py_compile` and `bash -n` only confirm the file parses; they do not confirm the
  new `GATE_B3b`/`B4_PARSE_ECHO` code paths produce exactly the intended output against real data —
  that can only be confirmed once job 1329278 actually runs and its report is read.
- **I did not verify my reading of the Design section's `VERDICT_B3`/`VERDICT_B4` shorthand against
  the manager's actual intent.** I documented my interpretation (keep the existing `VERDICT: B3=`/
  `VERDICT: B4=` labels, add the three-way value) above in Decisions; if the manager in fact wanted a
  literal, separate `VERDICT_B3b`-style line for B3 and B4 too (in addition to, not instead of, the
  existing `VERDICT: B3=`/`B4=` lines), that is a small additive change to the same two `print`
  statements — flagging it rather than guessing further.
- **I did not verify disk space, permissions, or read access on the compute node** for the two new
  code paths (`os.path.getsize`, line-counting 24 `.out` files) — both are small, IO-light operations
  similar to what the existing B2/B3 code already does, so I have not separately load-tested them.
- **I did not verify whether `step9_manifest.csv` or any T22 `cell_manifest.csv` could contain
  duplicate `hh_id` values within one cell** (which would make a `len(ids_set) != 50` false positive
  even when 50 *rows* are present) — the parse guard as designed measures set size, not row count, on
  purpose (per the Design section's own wording, "either side's set size"), so a real duplicate would
  correctly trigger `NOT_EVALUABLE` rather than silently pass; I did not independently confirm no
  duplicates exist in the real files, since that would have required reading the real T22 tree, out
  of scope for this login-node-constrained task.
- **I did not attempt to distinguish a genuinely truncated (partial-write) non-empty log from a
  complete one** — per rule 7, this was deliberately not implemented (no invented completion marker);
  GATE_B3b's PASS condition is existence and non-emptiness only, exactly as specified, and a
  non-empty-but-truncated log would still count as `logs_nonempty` even though it might be missing
  some lines of grep-able content near the end.
- **The remote `T49_scripts/` leftover directory** was left untouched (not `rm`'d, since `rm` is not
  on the allowed login-node command list, and this task does not own that cleanup — the job's own
  wrapper already deletes it on the compute node when it runs).
