# T60 — B3's sample-size test is mis-specified; redo it correctly, and read B4 properly (plan §5 item 36)

Task doc:   this file.
Opened by:  manager, 2026-09-18, after adjudicating T54 (Progress Log (co)).
Status:     SUBMITTED 2026-09-18 (employee). JobID 1329691. Employee: fresh Sonnet.
Scope:      **Arithmetic on two CSVs that already exist. No EnergyPlus runs. No re-simulation. No new
            campaign. Read-only on every input.** This is a cheap job; it must not become an expensive one.

## Why this exists — the mistake is in the TEST, not in the runs

T54 scored T28 (the 200-home sample-size campaign) and all four of its controls fired correctly, so its
`B0`, `B1`, `B2`, `B5` PASS verdicts stand. **`B3` is the problem.**

`B3` wrote `/speed-scratch/o_iseri/2J_revision/T28/out/t28_b3_wp4_test.csv` (72 metric-cell rows, header
`cell,metric,mean_n50,mean_n200,halfwidth_t_n50,halfwidth_t_n200,halfwidth_boot_n200,inside_t_ci,inside_boot_ci`).
**14 of the 72 rows carry `inside_t_ci=False`.** Read naively, that says "the 50-home answer is outside the
200-home confidence interval in 19 % of cases, so 50 homes is not enough." **That reading is wrong, and the
manager has already ruled it NOT_INTERPRETABLE.**

**The reason, and you must reproduce this arithmetic before doing anything else.** `B1` confirmed
`prefix_ok=True` in all four cells: **the 50 homes are the first 50 of the same 200**, not an independent
sample. Write `mean50 − mean200` in terms of the 200 draws and its variance is

```
Var(mean50 - mean200) = sigma^2 * (1/50 - 1/200) = sigma^2 * 3/200
```

so its standard deviation is **sqrt(3) times** the standard error of `mean200` itself. The `inside_t_ci`
flag compares that difference against the `mean200` **confidence interval**, i.e. against a yardstick
**sqrt(3) too short**. Under perfectly well-behaved sampling the flag is therefore expected to read `False`
roughly **26 %** of the time (`2*(1-Phi(1.96/sqrt(3)))`). **The observed 19 % is BELOW that.** As
constructed, `B3` is evidence *for* the runs being well behaved, not against — but it is not a test, and no
verdict may be quoted from it in either direction.

**This is the same family as plan §5 item 29 (entry (cd)): a check whose two sides are not on the same
basis. Do not "fix" it by widening a band. The band was never the problem; the yardstick was.**

## What to compute — Part A, the corrected comparison

Work **only** from `t28_b3_wp4_test.csv`. Every quantity you need is in it; **no simulation output is
re-read.**

1. Recover the sample standard deviation for each row from the reported half-widths:
   `s_n = halfwidth_t_n / t(0.975, n-1) * sqrt(n)`, once from the n=50 column and once from the n=200
   column. **Report both, per row, and report their ratio.** If `s_50` and `s_200` disagree by more than a
   few percent for some row, say which rows and by how much — that is information about the spread, not an
   error to smooth over.
2. Compute the correct half-width for the difference:
   `hw_diff = t(0.975, 199) * s_200 * sqrt(1/50 - 1/200)`.
   Report, per row, `mean50`, `mean200`, `diff = mean50 - mean200`, `hw_diff`, and a new flag
   **`consistent_nested`** = `abs(diff) <= hw_diff`.
3. **Count how many of the 72 rows are `consistent_nested=False`, and list them in full.** Then state the
   rate as a fraction of 72 and compare it against the 5 % a correctly specified 95 % test should give.
4. **Break the count down by metric family** — energy totals (`elec_facility_kWh*`) against load-shape
   metrics (`mean_peak_hour*`, `midday_share*`, `evening_ramp_kW_mean*`, `mean_daily_peak_kW*`) — and by
   **level** (`@2022`, `@2030`) against **change** (`_delta_2022to2030`). **That split is the whole point of
   the task:** the paper's energy conclusions and its load-shape conclusions do not have to survive together,
   and the manuscript needs to know which of them the 50-home sample supports.
5. Do the same with the bootstrap column where one exists, and say whether the two agree.

## What to compute — Part B, the answer the reviewer actually asked for

`B4` wrote `/speed-scratch/o_iseri/2J_revision/T28/out/t28_b4_convergence.csv` (432 rows, header
`cell,metric,N,mean,halfwidth`), with N in {10, 20, 50, 100, 150, 200}. **This is the honest answer to
"is 50 homes enough", and it needs no significance test at all** — it reports the precision achieved at each
sample size directly.

6. For every cell and metric, report the half-width at **N=50** and at **N=200**, and **the half-width at
   N=50 as a percentage of the `mean200`** (a relative precision). Sort the table worst-first.
7. State, per metric family, **the relative precision the 50-home sample achieves.** A metric whose 50-home
   half-width is a fraction of a percent of its mean is settled; one whose half-width is comparable to the
   quantity itself is not, whatever any flag says.
8. **Check the curve behaves.** Half-width should fall roughly as `1/sqrt(N)`. Report, per cell and metric,
   the ratio `halfwidth(50)/halfwidth(200)` against the expected `sqrt(200/50) = 2.0`. **Any row far from 2.0
   is worth naming** — it means the spread itself changes with N, which a simple sample-size argument does
   not cover.
9. Flag by name any metric whose `mean` moves **monotonically** with N across all six N values rather than
   settling. A mean that drifts in one direction as N grows is not a precision problem and must not be
   described as one.

## Controls — no number of yours is quotable without them
- **Seen-working:** re-derive, by hand and printed in the report, the `hw_diff` for **one** named row from
  its own numbers, and show it matches your script's value for that row. Also reproduce one row's
  `halfwidth_t_n200` from your recovered `s_200` and show it returns the CSV's own value — that proves your
  inversion of the half-width formula is right, which everything in Part A rests on.
- **Seen-failing:** feed your comparison a row you have altered by hand so that `diff` is deliberately larger
  than `hw_diff`, and show `consistent_nested=False` fires for it.
- **A third control, and it is the important one:** generate 72 rows of pure noise with a known sigma under
  the **nested** design (draw 200 values, take the first 50), run your `inside_t_ci` reproduction over them,
  and show the flag fires at roughly the predicted **26 %** — then run `consistent_nested` over the same
  rows and show it fires at roughly **5 %**. **This is what demonstrates the original flag is mis-specified
  rather than merely asserting it.** Report both observed rates with the number of draws used.
- All controls in **one** file under `T60/logs/`, from **one** invocation, with **"did not run" / "ran and
  did not fire" / "ran and fired" kept as three distinct outcomes.**

## Hard rules
- **Login node `speed-submit2` is for submission only.** Allowed there: `sbatch squeue sacct scancel
  scontrol cd ls scp module load` plus **single-file** `tail head grep wc -l cat`. **Forbidden there, by
  name: `python` (any form, including one-liners), `find`, `mkdir`, `du`, `md5sum`, `cp`, and any blocking
  `srun`.** Create remote directories only by `scp -r` of a local folder containing `.keep` files.
- ssh `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Remote shell is **tcsh**:
  **no `2>&1`, no `2>/dev/null`.**
- Every job `-p ps -t 7-00:00:00`. Python on compute nodes only:
  `/speed-scratch/o_iseri/envs/step4/bin/python`. Submit at **`-c 1 --mem=16G`; do not raise it.**
- **Read-only on every input.** Do not edit `t28_check.py`, do not edit either CSV, do not touch anything
  under `T28/` or `T54/` other than reading. **Write only under `T59`-style new tree `T60/`.**
- **Change no band and no threshold anywhere.** You are correcting a yardstick, not moving a limit.
- **You never wait.** Submit, write the JobID into the Ledger, end the turn.
- The two CSVs are small (73 and 433 lines). You may read them; do not read any simulation output.

## Report
`/speed-scratch/o_iseri/2J_revision/T60/logs/t60_b3_correction.txt`, `==== CONTROLS ====` first, then
`==== PART A ====` and `==== PART B ====`.
**Write each inner exit code into the report by name.** A wrapping job that exits 0 whatever happens inside
has already fooled this project once (T58, job `1329676`, `sacct` said `COMPLETED 0:0` on a job that raised).
**Never print `nan` for a quantity you deliberately did not compute — print "not computed" and why.**

## Ledger
<!-- employee: JobID · what · state · exit · output path -->
- **Read both real input CSVs in full** via ssh `cat`/`head` on the login node (allowed, single-file):
  `T28/out/t28_b3_wp4_test.csv` (73 lines = 72 data rows, header `cell,metric,mean_n50,mean_n200,
  halfwidth_t_n50,halfwidth_t_n200,halfwidth_boot_n200,inside_t_ci,inside_boot_ci`) and
  `T28/out/t28_b4_convergence.csv` (433 lines = 432 data rows, header `cell,metric,N,mean,halfwidth`,
  N in {10,20,50,100,150,200}) — line counts match the task doc exactly.
- **Confirmed scipy is on the compute env** (`/speed-scratch/o_iseri/envs/step4/bin/python`): `grep scipy`
  on `T28/T28_scripts/t28_check.py` (read-only) shows `from scipy import stats as _stats` — same package
  this script needs, so no new dependency is introduced.
- **Wrote `t60_analysis.py`** (scratchpad, then staged) implementing Controls 1-3, Part A (items 1-5) and
  Part B (items 6-9) exactly per the task doc's formulas. `py -3 -m py_compile` clean.
- **Local smoke test, 3 iterations**, using read-only `scp`'d copies of the two real CSVs (not the
  originals) in `scratchpad/smoke_inputs/`:
  - Run 1 caught a **real bug**: `s200`/`hw_diff`/`consistent_nested` come out as `numpy.bool_`/
    `numpy.float64` (scipy's `t.ppf` returns numpy scalars), so `x is False` identity checks silently
    never matched. This zeroed the `consistent_nested=False` count in Part A (reported 0/72) and mislabeled
    Control 2 as "did not fire" even though the printed value was correctly `False`. Fixed all three sites
    (`t60_analysis.py`, Part A false-row filter, per-family false count, Control 2 status check) by
    replacing `is False` with `not x`, and additionally wrapped every `consistent_nested*` assignment in
    `bool(...)` for defense.
  - Run 2 (post-fix): Control 2 now correctly reports "ran and fired"; Part A now reports **6/72 (8.33%)**
    `consistent_nested=False`, all 6 in the `load_shape` family (0 in `energy`, 0 in `other_unclassified`),
    close to the 5% a correctly specified test should give. Also caught a cosmetic bug: two `rep.w(...)`
    calls used literal `%%` inside a plain string with no `%`-operator substitution applied, so `%%` printed
    verbatim instead of collapsing to `%`. Fixed both (Control-3 STATUS line, Part B family-summary header).
  - Run 3 (post both fixes): exit 0, `diff` against run 2's report shows only the two `%%`->`%` lines and
    timestamps changed — no other numbers moved. Confirms the numeric fix was the `is False` bug alone;
    the `%%` fix was purely cosmetic.
- **Staged to Speed** via `scp -r` of the local `T60/` folder (no `mkdir` on the login node): `T60/
  T60_scripts/t60_analysis.py` (23,747 B), `T60/T60_scripts/t60_job.sh` (997 B), `T60/logs/.keep` (0 B).
  Remote `ls -la` confirmed exact byte-count match to local on both script files.
- **Job submitted.** `cd /speed-scratch/o_iseri/2J_revision/T60/T60_scripts && sbatch t60_job.sh` ->
  **JobID 1329691**. `#SBATCH -p ps -t 7-00:00:00 -c 1 --mem=16G`, output
  `T60/logs/t60_slurm_%j.out`, report at `T60/logs/t60_b3_correction.txt`. `squeue -j 1329691` immediately
  after submit: `R` (running), node `speed-16`. Status: **SUBMITTED**, not waited on.

## Verified
- 73/433 line counts on the real remote CSVs match the task doc's stated 73/433 exactly (`wc -l` on the
  login node).
- All 72 real B3 rows and the B4 header/first rows read directly (`cat`/`head` on the login node) before
  writing the script, to confirm column names, `True`/`False` string casing, and that
  `halfwidth_boot_n200` is populated on every one of the 72 rows (no "not computed" needed for the
  bootstrap side in the real data).
- Local smoke-test numbers (from the read-only downloaded copies, run 3): `consistent_nested=False` count
  **6/72 (8.33%)**, all 6 in `load_shape` (0/4 `energy` change, 0/8 `energy` level, 0/4
  `other_unclassified` change, 0/8 `other_unclassified` level; 3/16 `load_shape` change, 3/32
  `load_shape` level) — this is the shape of result the task doc's item 4 asked for (energy vs
  load-shape do not have to survive together), but it is a **local reproduction only**; the real Speed run
  reads the same unmodified files so is expected to match, not independently confirmed here.
  Control 3 (Monte Carlo, seed=60, n=72): naive flag 19/72=26.39% (predicted 25.78%), `consistent_nested`
  2/72=2.78% (predicted 5.00%) — both within 2 binomial SE of prediction.
  Control 1: independent reproduction of `s_200` and `hw_diff` for `SingleD__Montreal_6A /
  elec_facility_kWh@2022` agreed with the shared-function values to <1e-13 absolute difference; reproduced
  `halfwidth_t_n200` matched the CSV's own value to 0.000e+00.

## Decisions
- **`load_factor*` metrics (12 of 72 B3 rows) are reported as their own `other_unclassified` family.** The
  task doc's item 4 names only `elec_facility_kWh*` (energy) and `mean_peak_hour*`/`midday_share*`/
  `evening_ramp_kW_mean*`/`mean_daily_peak_kW*` (load-shape); it does not say where `load_factor*` goes.
  Rather than guess it into either named group, the report gives it a third, clearly-labeled bucket and
  states this explicitly in the report text itself.
- **Bootstrap-side `consistent_nested_boot`** is computed by applying the SAME half-width-inversion formula
  used for the t-based column to `halfwidth_boot_n200` (i.e. treating the bootstrap n=200 half-width as if
  it had the same `t(0.975,199)` structure, to recover an effective boot-based spread for the nested-diff
  formula) — there is no boot n=50 column to invert directly, and the task doc says only "do the same with
  the bootstrap column where one exists" without specifying the inversion. This is a judgment call, stated
  in the report.
- **"s50/s200 disagree by more than a few percent"** (item 1) implemented as >3.0% absolute deviation of
  the ratio from 1.0 — the task doc did not give a number. Fully documented as `S_RATIO_DISAGREE_PCT` in
  the script and named as a decision in the report text.
- **"Any row far from 2.0" (item 8)** implemented as `|ratio - 2.0| > 0.4` — again no number given in the
  task doc. Documented as `RATIO_FAR_BAND` in the script and named in the report text.
- **Wrapping job does NOT force exit 0.** Unlike T54 (whose controls are designed to make the checker
  itself FAIL), nothing in T60 is supposed to crash the python process — the controls only produce
  True/False values inside the report text. So `t60_job.sh` propagates the real python exit code, and also
  appends `RC_MAIN=<code>` as the last line of the report for a belt-and-suspenders read (avoiding the T58
  always-exit-0 trap by construction, not by convention).
- **Did not touch `t28_check.py` or either CSV** — read-only via `cat`/`head`/`scp` throughout. Nothing was
  written under `T28/` or `T54/`.

## Next
Job 1329691 is running. Next agent (manager or fresh employee, NOT this one — no waiting/polling here):
after the job finishes, read `/speed-scratch/o_iseri/2J_revision/T60/logs/t60_b3_correction.txt` (allowed
single-file `cat`/`grep`/`head` on the login node), `==== CONTROLS ====` first — confirm Control 1 says
"ran and matched", Control 2 says "ran and fired", Control 3 says "ran and fired as predicted" (or read the
actual rates it prints if not) before trusting `==== PART A ====` / `==== PART B ====`. Also check the
report's last line `RC_MAIN=0` (or read `sacct -j 1329691` for wall-clock, but the report's own `RC_MAIN`
line is the pass/fail source of truth here since it is not artificially forced). If the real Speed numbers
differ from the local smoke-test numbers above (run 3), that is expected to be impossible (same code, same
files) but should be checked, not assumed.

## WHAT I DID NOT VERIFY
- **Did not wait for or check job 1329691's actual completion, exit code, or report contents on the real
  Speed run** — only one `squeue` snapshot immediately after submit (state `R`), per the no-parking/
  no-waiting rule. Everything under "Verified" above comes from the LOCAL smoke test on downloaded copies
  of the two CSVs, run with local `py -3` (numpy 2.3.5, scipy 1.17.0) — not the cluster's
  `/speed-scratch/o_iseri/envs/step4/bin/python`. The two environments' scipy/numpy versions were not
  confirmed to match; `t.ppf` and `norm.cdf` are standard enough that a version mismatch is unlikely to
  change results, but this was not checked.
- **Did not independently verify `scipy.stats.t.ppf(0.975, 199) = 1.9719565443`** against a source outside
  scipy itself (e.g. a printed statistical table) — Control 1's "independent" re-derivation still calls
  `scipy.stats.t.ppf`, so it proves internal consistency between the shared function and an inline
  re-implementation of the same formula, not that scipy's own t-quantile is correct. This is the same class
  of gap T54 flagged for its own hand-check control.
- **Did not check disk quota or any other Speed-side resource constraint** before submitting — the job's
  footprint is tiny (reads two CSVs under 40 KB combined, writes one text report), so this is judged
  low-risk but not measured.
- **Did not re-derive why 6 of the 72 real rows are `consistent_nested=False`** beyond reporting which rows
  and their family/kind split (all 6 in `load_shape`, split between `mean_peak_hour*`/
  `evening_ramp_kW_mean*`) — whether this reflects real non-normality in those load-shape metrics'
  household-to-household distribution, or is just the 8.33%-vs-5% draw one would expect from only 72
  trials, is a manuscript-writing judgment call for the manager, not decided here.
- **Did not check whether `T28_scripts/t28_check.py`'s own B3/B4 CSV-writing code has any other undocumented
  quirk** (e.g. rounding, a different `n` used internally) beyond what the two CSVs' own column values show
  — this task worked strictly from the CSVs as delivered, per its scope.

---

## MANAGER RULING — 2026-09-18 (Progress Log (cp)): ACCEPTED. Item 36 CLOSED. New item 37 — **this brief's own expected value was wrong.**

**Control 3, the load-bearing one, fired exactly as predicted.** On 72 rows of pure noise generated under
the **nested** design, the original `inside_t_ci` logic read `False` **19/72 = 26.4 %** against the
predicted `2(1-Phi(1.96/sqrt3)) = 25.8 %`; `consistent_nested` read `False` **2/72 = 2.8 %** against the
predicted 5 %. Both within two binomial SE. **Entry (co)'s ruling on `B3` is now demonstrated on invented
data, not merely derived on paper.** Controls 1 and 2 also fired (`0.000e+00` reproduction; hand-broken row
flagged).

**Corrected result: 6 of 72 rows inconsistent = 8.3 %**, which is **1.3 binomial SE** from the 5 % a correct
95 % test gives — *not distinguishable from a well-behaved test*. **The rate may not be pushed harder in
either direction:** the 72 rows are 4 cells x 6 metrics x 3 forms, and `@2022`, `@2030` and `_delta` are
strongly correlated, so the effective number of independent trials is well under 72. **No adequacy verdict
from a rate.**

**The family split is real in direction.** Energy **0 of 12** flagged; load-shape **6 of 48**, all in
`mean_peak_hour` or `evening_ramp_kW_mean`; `load_factor` 0 of 12. The employee was right to report
`load_factor` separately rather than guess it into a family this brief failed to assign.

### Item 37 — the brief's `expected sqrt(200/50) = 2.0` is wrong, and so was its implicit N=50 comparison
Part B's numbers did not line up with Part A's, so the manager read `t28_check.py` directly.
`b4_convergence()` (lines 353-380) builds every sub-`N` point as the **2.5-97.5 percentile of 1,000
subsample means drawn WITHOUT REPLACEMENT from the same 200** — a **finite-population** quantity carrying
`sqrt((200-50)/199) = 0.8682`, with a percentile 1.96 rather than `t(49)`.

That explains, to about 2 %, both anomalies the report surfaced:
- `B3`'s `halfwidth_t_n50` vs `B4`'s N=50 `halfwidth` differ by 14-37 % while their **N=200 values agree to
  six decimals**. Predicted `1.1811 x (s50/s200)`: SingleD 1.379 vs **1.369**, OtherDwelling 1.270 vs
  **1.246**, MidRise 1.376 vs **1.352**, HighRise 1.125 vs **1.136**.
- `hw50/hw200` sits near **1.73** on all 72 rows. The correct expectation is
  `1.96*0.12277 / (1.97196/14.1421) = 1.726`. **The observed values sit on it.**

**Consequences.** The convergence curve behaves **exactly** as it should. The single row this brief's
threshold flagged as "far from 2.0" (`MidRise / midday_share@2030`, 1.5589) is **0.17 from the true
expectation and is not an outlier — do not report it as one.** The "s50 vs s200 differ by more than 3 %"
list (56 of 72 rows) is **noise, not a finding**: SD of `log(s50/s200)` is about 0.09, so ~74 % of rows
should exceed 3 %; 78 % did.

**Lesson for the gates doc: a brief that states an expected value is itself a check, and it must be derived
from the code that produces the number, not from the textbook formula that code resembles.**

### What the manuscript may quote
Dividing the finite-population factor back out (the reviewer asks about 50 drawn from **16,326**, not from
200), the honest half-widths are **15 % larger** than Part B prints.
- **Quotable: at 50 households a cell's annual electricity total is resolved to better than +/-0.6 % of
  itself** (worst 0.5075 % -> **0.585 %**). Load-shape **levels**: ~6 % median, up to ~49 % worst.
- **Not quotable:** per-cell **2022->2030 changes are not resolved at 50 or at 200**. `mean_peak_hour_delta`
  and `evening_ramp_kW_mean_delta` have intervals containing zero by a wide margin in every cell.
  **Rule: no per-cell 2022->2030 load-shape change may be quoted as a change unless its own interval
  excludes zero.** A limitation of what 200 homes resolve — **no band moved, no flag relaxed.**
