# T57 — why the reversion-side scenarios exclude a household reproducibly (plan §5 item 33) — implementation state

Task doc:   this file.
Opened by:  manager, 2026-09-18, plan §5 item 33 (Progress Log (ce)).
Status:     IN PROGRESS 2026-09-18 (employee). Job 1329673 submitted, not yet collected.
Scope:      **Diagnosis only.** Not a gate, not a fix, not a re-run. You name the cause and stop.

## The finding you are explaining (established, do not re-derive)
- T29's λ=0.0 arm delivered **1,198 of 1,200** runs. Both absences were written down by the campaign itself in
  `out/lambda_0.0/<cell>/undelivered.csv`, with the reason string naming **`not in scenario pool`** and
  `integration.py:432-438`.
- T53 then found that **T32's S-Revert-std campaign drops the same household**: `OtherDwelling__Vancouver_5C`,
  `sample 9`, `sim_hh_id 129937`, reason string identical to the character — in a campaign built and launched
  separately, weeks apart.
- **T29's λ=0.5 arm delivers that same household fine**, with a full 8,760-row file.
- Both affected arms are **reversion-style** (λ=0.0 "none of the jump survives", S-Revert-std). The half-way arm
  is not affected. So the reversion-side schedule construction excludes this household **reproducibly**, which
  makes it a WP2 question, not a run-time accident.
- The second λ=0.0 absence was in `HighRise__Kelowna_5B`. Treat it the same way.

## The mechanism, already located in the code (your starting point, not your answer)
`2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py`:
- `load_schedules()` ends by dropping every household for which `validate_household_schedule(hh_data)` is
  False (the `invalid_ids` block, around lines 432-438), printing `Dropped N households (failed schedule
  sanity check)`. **The sampling pool is therefore whatever survives that filter on the file actually loaded**,
  which is why the pool depends on schedule CONTENT and not only on the household list.
- `validate_household_schedule()` (from line 219) rejects a household when, for Weekday **or** Weekend:
  any hour is outside [0, 1]; the 24 hours are all exactly 0; total daily presence-hours fall outside
  **[2, 24]**; more than 4 isolated one-hour spikes; or all 24 hours are exactly 1 without the retiree tag.

**Pre-registered hypothesis, written before you measure:** the reversion arms move at-home time *down*, so the
most likely rule to fire is the **lower end of the [2, 24] presence-hours band**. **Write down whether it fires
or not before you look**, and report the rule that actually fires even if it is a different one. Do not adjust
the hypothesis after the fact — say plainly that it was wrong if it was.

## What to measure, in this order
1. **Confirm the two households and cells** from the two `undelivered.csv` files themselves, quoting the reason
   strings verbatim (T29 λ=0.0: `OtherDwelling__Vancouver_5C` and `HighRise__Kelowna_5B`; T32 S-Revert-std:
   `OtherDwelling__Vancouver_5C`). Do not take them from this doc.
2. **For `sim_hh_id 129937`, print its 24 weekday and 24 weekend hourly values** from each of the three
   schedule files: the λ=0.0 file, the S-Revert-std file, and the λ=0.5 file. Print the presence-hour total for
   each day type in each file, to 4 decimals.
3. **Name which of the five rules in `validate_household_schedule` fires**, in which file, for which day type.
   Show the comparison that decides it (the value against the threshold), not just the verdict.
4. **Count how many households fail validation in each whole file**, and break the count down by which rule
   fired. This is the number that says whether the exclusion is two households or a systematic population.
   Report it for λ=0.0, S-Revert-std, λ=0.5 and the unmodified 2030 main file, so the reversion arms can be
   compared against an arm that is known to be fine.
5. **Say whether the excluded households share anything** — archetype, province, household size, at-home
   stratum, match tier — using only columns already in the schedule file's metadata. If nothing is shared,
   say that; a null result here is a real answer.

## Controls — no number of yours is quotable without them
- **Seen-working control:** re-run your own validation implementation over a household that is known to be
  delivered in all three arms and show it passes in all three. If you call `validate_household_schedule`
  itself, say so — reusing the real function is preferred to re-implementing it.
- **Seen-failing control:** take a copy of one passing household's row, drive its presence-hours below 2.0 by
  hand, and show your code reports exactly the `[2, 24]` rule firing. If you re-implement any rule, this
  control must exercise the re-implementation, not the original.
- Both controls must fire inside **one** invocation and be written into **one** file under `T57/logs/`, with
  "did not run", "ran and did not fire" and "ran and fired" kept as three distinct outcomes.

## Hard rules
- **Login node `speed-submit2` is for submission only.** Allowed there: `sbatch squeue sacct scancel scontrol
  cd ls scp module load` plus **single-file** `tail head grep wc -l cat`. **Forbidden there, by name:
  `python` (any form, including one-liners), `find`, `mkdir`, `du`, `md5sum`, `cp`, and any blocking `srun`.**
  Create remote directories only by `scp -r` of a local folder containing `.keep` files.
- ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Remote shell is **tcsh**:
  **no `2>&1`, no `2>/dev/null`.**
- Every job `-p ps -t 7-00:00:00`. Python on compute nodes only:
  `/speed-scratch/o_iseri/envs/step4/bin/python`. Submit this at **`-c 1 --mem=16G`; do not raise it** — 2J
  stays at or under 32 CPUs in flight whatever the association limit says.
- The schedule CSVs are about 667 MB each. **Never read one into your context.** Your job streams them; you
  read only its report.
- **Read-only on every input.** Change no schedule file, no campaign output, and no pipeline code. If you
  believe a code change is warranted, write the recommendation in Decisions; the manager rules on it.
- **You never wait.** Submit, write the JobID into the Ledger below, end the turn.

## Report
`/speed-scratch/o_iseri/2J_revision/T57/logs/t57_pool_exclusion.txt`, `==== CONTROLS ====` first, then
`==== FINDINGS ====` answering items 1-5 in order. If the wrapping job exits 0 whatever the inner steps
return, say so here and write each inner exit code into the report by name.

## Ledger
- Read `CLAUDE.md`, this task doc, `integration.py:219-266` (`validate_household_schedule`) and
  `integration.py:323-440` (`load_schedules`), and the Ledger/Verified sections of `2026-09-15_T29_wp2_scenario_step8_runs.md`
  / `2026-09-15_T32_wp2_srevert_std_build.md` before writing anything, as instructed.
- Located the 4 input files from `T26_scripts/t26_job.sh:52,59` and `2026-09-15_T32...md` Ledger: λ=0.0 =
  `T26/out/lambda_0.0/BEM_Setup/BEM_Schedules_2030.csv`, λ=0.5 = `T26/out/lambda_0.5/BEM_Setup/BEM_Schedules_2030.csv`,
  S-Revert-std = `T32/out/std/BEM_Setup/BEM_Schedules_2030.csv`, unmodified 2030 main = `T20/out/main/BEM_Setup/BEM_Schedules_2030.csv`
  (`t26_job.sh:27` labels this last one "SC0 reference"). All 4 confirmed present on Speed by remote `ls -la` (login node, allowed).
- Remote `cat` (single-file, allowed) of the three `undelivered.csv` files confirmed item 1 verbatim: T29 λ=0.0
  `OtherDwelling__Vancouver_5C` sample 9 sim_hh_id **129937**; T29 λ=0.0 `HighRise__Kelowna_5B` sample 40 sim_hh_id
  **48609** (second household, not previously id'd by number in this doc); T32 S-Revert-std `OtherDwelling__Vancouver_5C`
  sample 9 sim_hh_id 129937. All three reason strings identical: "not in scenario pool (absent from schedule file, or
  dropped by validate_household_schedule -- integration.py:432-438; ...)".
- Remote `grep '^129937,'` / `grep '^48609,'` (single-file, allowed) on all 4 schedule CSVs, hand-read the 48-row output
  directly (never loaded a full CSV into context) — see Verified below; this let me confirm the pre-registered hypothesis
  by hand before the job even ran.
- Wrote `T57/T57_scripts/t57_diagnose.py` (streams each CSV one household at a time, O(1) memory per household since the
  files are SIM_HH_ID-contiguous — confirmed via remote `head`; calls the REAL `integration.validate_household_schedule`
  for every household as the authoritative verdict, cross-checked against a re-implementation `diagnose_household()` that
  additionally names which rule fired; runs both controls in the same invocation) and `T57/T57_scripts/t57_job.sh`
  (sbatch wrapper, `-p ps -t 7-00:00:00 -c 1 --mem=16G`, captures the inner python's real exit code via `set +e`/`set -e`
  around that one command so the wrapping job's exit code is never swallowed). Syntax-checked locally: `py -3 -m py_compile`
  (OK) and `bash -n` (OK).
- Staged via `scp -r` of a local folder (`T57/logs/.keep`, `T57/T57_scripts/{t57_diagnose.py,t57_job.sh}`) to
  `/speed-scratch/o_iseri/2J_revision/T57/` — remote `ls -la` confirmed both scripts landed (22,930 B / 2,227 B).
- **JobID 1329673** — `sbatch t57_job.sh` from `/speed-scratch/o_iseri/2J_revision/T57/T57_scripts`, submitted
  2026-09-18. State at handoff: PENDING/RUNNING, not yet collected by this employee (rule: never wait). Report will land
  at `T57/logs/t57_pool_exclusion.txt`; slurm log at `T57/logs/slurm_1329673.out`.

## Verified
- **Pre-registered hypothesis (written before measuring, per task doc): the reversion arms push at-home time down, so
  the rule most likely to fire is the LOWER end of the [2, 24] presence-hours band.**
- **Hand-verified from the raw CSVs directly (before job 1329673 even ran), by `grep`-ing sim_hh_id 129937's 48 rows out
  of each file and summing the `Occupancy_Schedule` column by hand:**
  - λ=0.0 (S-Revert, T26): **Weekday total = 1.5** (only hour 19 = 1.0, hour 20 = 0.5, all other 22 hours = 0.0) — below
    2.0, **hypothesis CONFIRMED, rule = lower end of [2,24]**. Weekend total = 18.0 (fine).
  - S-Revert-std (T32): **Weekday total = 1.0** (hour 19 = 0.5, hour 20 = 0.5, rest 0.0) — further below 2.0, same rule.
    Weekend total = 16.5 (fine).
  - λ=0.5 (S-Partial, T26): **Weekday total = 2.0 exactly** (same as λ=0.0 plus hour 11 = 0.5) — lands exactly ON the
    inclusive lower boundary (`2.0 <= total <= 24.0` is `True` at 2.0) and so **passes**. This is why the half-way arm
    delivers this household and the two reversion arms do not: the extra midday presence the λ=0.5 blend keeps is just
    enough to cross the boundary, nothing more.
  - Confirms it is `validate_household_schedule` REJECTING the household on content, not "absent from schedule file" —
    all 48 rows are present in the raw CSV in all three files (`grep -c` = 48 in each).
  - Evidence: raw `grep` output captured in this session's tool transcript (not re-quoted in full here to keep this
    doc short); re-derivable any time with `grep '^129937,' <file>` (single-file grep, allowed on login node).
- Also spot-checked sim_hh_id 48609 (HighRise__Kelowna_5B) in λ=0.0 by hand: **Weekday total = 0.5** (only hour 3 = 0.5,
  all else 0.0) — same rule, more severely below the band. Its Weekend profile is all 24 hours = 1.0 exactly (total =
  24.0, at the upper edge, passes) — noted below as a separate finding, not the cause of exclusion.
- **Job 1329673 will independently re-derive all of the above via the real `validate_household_schedule` function (not
  a re-implementation) plus population-wide counts (item 4) and the two controls — its report is the authoritative
  source once collected; the hand-checks above are a redundant pre-check, not a substitute.**

## Decisions
- **Finding, not yet ruled on: `integration.py`'s `validate_household_schedule` docstring (lines 220-227) lists 5
  rejection rules including "all 24 hours exactly 1 AND not tagged Retiree", but the executable code (lines 231-266)
  implements only 4 — that 5th rule is documented but never checked.** This surfaced because sim_hh_id 48609's Weekend
  profile is all-1.0 for all 24 hours (would have hit that undocumented-but-missing rule if it existed) yet passes,
  because only R1-R4 run. It did not change this diagnosis (Weekday's [2,24]-band failure excludes the household
  regardless), so I did not treat it as in scope to fix — flagging it here for the manager to rule on (doc fix vs. code
  fix vs. leave alone).
- Assumed the schedule CSVs remain SIM_HH_ID-contiguous (48 rows/household, Weekday(24)+Weekend(24), no interleaving)
  for all 4 files, based on confirming this via `head` on one file before writing the streaming script. `t57_diagnose.py`
  self-checks this assumption per file (a "reopened SIM_HH_ID groups" counter, expected 0) and reports it rather than
  silently trusting it.
- Used sample_001 / HH130228 (SingleD__Montreal_6A) as the seen-working control household, reusing the household T29's
  own smoke test already confirmed PASS/delivered under λ=0.0 (`2026-09-15_T29...md` Verified section) rather than
  picking an unverified one.

## Next
Collect job 1329673 (not before it completes — do not poll from here). A fresh employee (or the manager) should:
1. `sacct -j 1329673` for state/exit code.
2. `tail`/`cat` (single-file) `T57/logs/t57_pool_exclusion.txt` — read `==== CONTROLS ====` first; both controls must
   show "ran and fired" / "ran and did NOT fire" as expected before trusting anything under `==== FINDINGS ====`.
3. Compare item 4's population-wide counts (all 4 files) against the hand-derived single-household finding above — if
   the population count for the reversion arms is small (order of the 2 known households) this stays a WP2 edge-case
   question; if it is large, it is a systematic population issue and changes the manager's ruling.
4. Read the code-vs-docstring gap noted under Decisions and rule on it.
5. Fold results into plan §5 item 33 in `project_2j_improvements_master_log.md` / MEMORY.md per the usual closure ritual.

## Manager interim ruling, 2026-09-18 (plan log entry (ck)) — NOT a closure

**The task is not closed. Job `1329673` is unread.** Everything below treats the employee's hand-`grep`
derivation as a *strong prediction*, which is what its own WHAT I DID NOT VERIFY correctly calls it. **No
number in this section may be quoted anywhere until the job's `==== CONTROLS ====` block is read and both
controls are seen in the right state.** Recorded now because the mechanism is worth acting on early, not
because it is confirmed.

**The pre-registered hypothesis was confirmed, and confirmed honestly.** It was written into the brief before
dispatch, the employee wrote it into Verified before measuring, and the measurement agrees: the weekday
presence-hour total for `129937` is **1.5 h** under λ=0.0 and **1.0 h** under S-Revert-std, both below the
`[2, 24]` band's lower edge, while under λ=0.5 it is **exactly 2.0 h** and the band is inclusive, so it
passes. `48609` under λ=0.0 is **0.5 h**. That is the whole explanation of item 33: **the two reversion arms
do not "lose" a household, they compute a schedule that the engine's own sanity check then refuses.**

**The consequence that matters is not the missing household — it is the direction of the filter.** The
reversion arms are the arms in which at-home time *falls*. The filter removes households whose at-home time
has fallen the furthest. So the households that survive into a reversion arm are, by construction, the ones
that reverted least, and **the delivered reversion arm is biased upward in at-home time relative to the
scenario that was designed.** The bias is in the same direction as the effect being measured, which is the
worst case. **Its size is entirely unknown until item 4's per-file, per-rule counts are read**: two
households is a footnote; a population is a WP2 finding that changes what the reversion scenarios may be
said to represent. **Standing rule, unchanged: no reversion-scenario number may be described as covering the
sampled households until item 4 is read.**

**λ=0.5 passing at exactly 2.0 is not reassurance, it is a warning.** The half-way arm clears the band by
nothing at all. Any future change to the blend, the smoothing, or the rounding moves households across that
edge in either direction and silently changes the pool. **Record it; do not "fix" it by widening the band —
that would be relaxing a band to pass, which this project does not do.**

**Ruling on the code-versus-docstring gap the employee found (`integration.py` documents five rejection
rules, implements four; the all-ones-without-retiree rule is never executed): DO NOT TOUCH THE FILE.** Every
campaign in this revision has been run against the code as it stands; editing it now — even the docstring —
puts a modification date on a pipeline file mid-revision for no gain, and editing the *code* would change the
sampling pool and invalidate every run already delivered. It is recorded as a documented deviation. **What it
does bind is prose: no manuscript or SI sentence may claim the pipeline rejects always-occupied schedules.**
It does not. `48609`'s weekend profile is all 24 hours at exactly 1.0 and passes.

**A prose correction is now owed, and it is a correctness fix, not a style one.**
`manuscript/draft_SI_schedule_completion.md:121-127` describes the filter as dropping "a household that is
never home at all". **That is not the rule.** The rule drops a household with **fewer than two presence-hours
in a day type**, and `129937` at λ=0.0 is home for 1.5 hours — it is home, just barely, and it is dropped.
The current wording would let a reader conclude the filter cannot touch a plausible household, which is the
opposite of what item 33 shows. **Held deliberately until `1329673` lands**, so the wording fix and item 4's
count are written in one sitting rather than two. WP10 owns it; it is not optional.

**Not ruled on, listed so it is not mistaken for settled:** a weekday profile of 1.5 presence-hours with 22
of 24 hours at exactly 0.0 is a strange schedule for a "return to the office" scenario in its own right,
regardless of the filter. Whether that is a correct consequence of the reversion blend or an artefact of it
is a WP2 question, and item 4's counts are what decides whether it is worth asking.

## Manager ruling, 2026-09-18 (plan log entry (cn)) — job `1329673` ACCEPTED; item 33 is a FOOTNOTE, with two carries

**Controls read first, as required. Both are right.** Seen-working: `HH130228` validates `True` in all four
files, real function and re-implementation agreeing — "ran and did NOT fire". Seen-failing: a hand-built
household driven to 1.0 weekday presence-hours — "ran and FIRED", `fail_rule=R3_presence_bounds`,
`weekday_total=1.0000`, and the **real** `validate_household_schedule` agrees. The three outcomes are kept
distinct. **The numbers below are quotable.**

**The hand-derivation in Verified above is confirmed by the job, using the real function.** `129937`:
weekday 1.5 h (λ=0.0), 1.0 h (S-Revert-std), 2.0 h (λ=0.5, passes). `48609`: 0.5 h (λ=0.0).
`real-vs-diag mismatches = 0` in all four files, and `reopened SIM_HH_ID groups = 0`, so the contiguity
assumption the streamer rests on was checked rather than trusted. **The pre-registered hypothesis is
CONFIRMED and was reported as such, not reshaped.**

### Item 4 is the answer, and it is neither "two households" nor "a systematic population"

Households dropped, of 144,465:

| File | Dropped | Share | Excess over unmodified |
|---|---|---|---|
| main (T20, unmodified 2030) | 983 | 0.680 % | — |
| λ=0.5 (S-Partial) | 1,010 | 0.699 % | **+27** |
| λ=0.0 (S-Revert) | 1,053 | 0.729 % | **+70** |
| S-Revert-std (T32) | 1,144 | 0.792 % | **+161** |

**The ordering is monotone in reversion strength**, and the weekday presence-bound rule carries it:
`R3_presence_bounds` on Weekday goes **142 → 167 → 202 → 244** across the same four files. That is the
predicted mechanism appearing at population scale, not just in two households.

**I re-derived the arithmetic independently and it closes on all three arms.** Taking S-Revert-std against
main: weekday `R2_all_zero` +51, weekday `R3` +102, weekend `R2` +18, weekend `R3` −10, total **+161**,
matching `1144 − 983`. λ=0.0: +7, +60, +18, −15 = **+70** = `1053 − 983`. λ=0.5: 0, +25, +18, −16 = **+27**
= `1010 − 983`. **Three independent closures. The per-rule breakdown is not decorative — it reconciles.**

### The ruling

**Item 33 is a footnote and an SI sentence, not a manuscript-blocking finding.** The decision rule was fixed
before dispatch ("two households is a footnote, a systematic population reaches the manuscript"), and the
honest reading is that this lands in between and closer to the first. **The bound settles it:** the worst
arm excludes **161 more households than the unmodified file, 0.111 % of the stock**, and since a household
can contribute at most its full 24 hours, **the largest arithmetically possible shift in the weekday at-home
share from this exclusion is 0.111 percentage points** — an upper bound, with the realistic value a fraction
of it. That is inside the 0.5 pp design band. **It is not, however, negligible against everything**: it is
several times T26's measured design-attainment differences of 0.0045–0.0216 pp, so **it may never be waved
away as rounding.** The SI states the mechanism, the direction and the count.

**The direction ruling from the interim entry stands unchanged and is now evidenced**: the filter removes the
households whose at-home time fell furthest, so a delivered reversion arm leans toward households that
reverted least. **Bounded, but real, and in the same direction as the effect being measured.**

**The band is not widened.** λ=0.5 clearing at exactly 2.0 remains a warning about fragility, not licence.

### Carry 1 — this extends (cd)'s common-household rule to all four arms

(cd) established that λ=0.0 and λ=0.5 do not share a household set (1,200 vs 1,198 delivered). **Item 4 shows
the problem is wider: all four files have four different pools** — 983, 1,010, 1,053 and 1,144 dropped — and
the two reversion arms are **not even nested** (`48609` fails under λ=0.0 at 0.5 h but **passes** under
S-Revert-std at 3.0 h). **So no cross-arm comparison may assume a shared household set from the design.
Manifest equality is established from the manifests, arm by arm, or it is not established.** T54 and T55 both
already check manifest equality; this is why that check is load-bearing and not a formality.

### Carry 2 — a new question the job surfaced without being asked

**Weekend `R2_all_zero` is 288 in the unmodified 2030 file and exactly 306 in all three scenario files**, for
λ=0.0, λ=0.5 and S-Revert-std alike. **A constant +18, independent of λ.** A work-from-home reversion blend
that varies with λ cannot produce a λ-independent constant, so **something in the scenario build step, not
the blend, zeroes eighteen households' weekends.** It changes no number here (those households are dropped in
every scenario arm equally, so they cannot bias a cross-arm comparison), but it is unexplained, and a
constant that appears in three separately built files is exactly the kind of thing that is a bug until shown
otherwise. Recorded as plan §5 **item 35**. **No job for it yet** — it is a WP2 question to settle when the
scenario build is next opened, not a reason to hold a number.
Also noted, in the opposite direction and also unexplained: weekend `R3_presence_bounds` is **19** in the
unmodified file and **3, 4 and 9** in the scenario arms, so the unmodified file has *more* weekend
presence-bound failures than any scenario.

### One report defect to fix in future briefs, not in this job

Where a household fails on Weekday, the report prints `Weekend total=nan`. The weekend hourly values are
printed in full beside it and are fine — `48609` under λ=0.0 is 24 hours of exactly 1.0, which sums to 24.0,
and I checked that by hand rather than assuming it. **The `nan` is a short-circuit artefact of the reporting,
not a value in the data.** But `nan` in a report reads as a data problem, and a reader without the hourly
values printed beside it could not tell. **Future briefs: a quantity that was deliberately not computed
prints "not computed (short-circuited after Weekday failed)", never `nan`.**

### Already ruled, restated so it is not reopened
The docstring-versus-code gap (five rules documented, four implemented) stands as recorded in the interim
entry: **`integration.py` is not touched**, and **no prose may claim the pipeline rejects always-occupied
schedules** — `48609`'s weekend is all 1.0 and passes.

The prose correction owed to `draft_SI_schedule_completion.md` — the filter drops a household with **fewer
than two presence-hours in a day type**, not only one "never home at all" — is now **unblocked** and carries
the counts above with it. WP10 writes both in one edit.

## WHAT I DID NOT VERIFY
- Did not wait for or read job 1329673's output — per the no-parking rule, submitted and stopped. Its report is
  unread by me; everything under "Verified" above except the explicit hand-`grep` checks is a prediction the job
  will confirm, not yet confirmed by the job itself.
- Did not check the population-wide drop counts (item 4) for any file — only the two known households were hand-checked.
- Did not verify item 5 (shared metadata) beyond eyeballing the two households' `PR`/`MATCH_TIER` columns from the raw
  `grep` output while writing this doc (both are `PR=BC`, `MATCH_TIER=1_Perfect`; `DTYPE` and `HHSIZE` differ) — the
  job's own item-5 output is the one to quote, not this line.
- Did not verify `/speed-scratch/o_iseri/envs/step4/bin/python` can successfully `from eSim_bem_utils_2J import
  integration` in a bare script outside the full `_import_step8()` chain other wrappers use — I mimicked that same
  import pattern (`sys.path.insert` + `from eSim_bem_utils_2J import integration`) since other jobs in this env do
  exactly this successfully, but did not smoke-test it standalone before submitting; if the job fails at import, that
  is the first thing to check in the slurm log.
- Did not check Speed disk/CPU quota before submitting (same gap other T-series docs note as unverified).
