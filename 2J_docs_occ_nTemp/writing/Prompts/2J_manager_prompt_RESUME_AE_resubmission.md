# 2J manager prompt — RESUME the Applied Energy resubmission (paste whole into a new session)

First written 2026-09-15 by the outgoing manager session. **Kept current: the manager rewrites §2 and §3
after every task completion** (author request, 2026-09-15). Last updated: **2026-09-21, session pausing
overnight (author closing) —
T76 (Figure 1, WP11 numbering, at-home-by-hour) ACCEPTED, no problems found. ALL NINE WP11 FIGURES ARE
NOW BUILT (8 of 9 fully accepted; Figure 6 still blocked). Only T72 (checker fix) is still on the cluster.
See §0.000000000000000 immediately below; §0.00000000000000 under it is now history.**

---

## 0.000000000000000 CURRENT STATE (2026-09-21, plan log entry (do), T76) — THIS IS THE STATE. Everything below it is history. START HERE ON RESUME.

**T76 is DONE. Figure 1 (WP11 numbering, at-home-by-hour) accepted** — job `1341263` finished in under 5
minutes. The hard-stop instruction did **not** fire: the 2022 at-home baseline turned out to be an existing
file already trusted by this project's own acceptance checks, not new computation. All three controls
(row-count on all six source files, hand-read spot check, and a nesting check reproducing T26's own
already-accepted SC0 property) passed, and the manager viewed the PNG directly: the pattern is exactly as
expected (2030 "Persist" scenario sits above the 2022 baseline at midday, "Revert" sits below it, "Null"
tracks the baseline almost exactly).

**This closes out all nine planned WP11 figures.** Status: Figures 1/2/3/4/5/7/8/9 all built and accepted.
**Figure 6 is the one open item** — it is blocked on T30's V3 gate, which needs T72 (the checker fix job)
to confirm PASS on the full 48-cell grid before the Figure 6 rescoping decision (average-profile vs.
full-model, two-way) can even be made.

**One job still live on the cluster, not yet collected:**
- **T72** (checker fix + full-grid rerun of T30's V3 gate, job `1341254`) — running as of this pause,
  started ~2026-09-21 and had run 45 minutes at last check. No ETA recorded; check `sacct -j 1341254 -X`
  fresh on resume rather than trusting this number.

Full detail: plan log entries (do) [T74], (do) [T75], (do) [T76] in `00_REVISION_PLAN.md`.

**Next, in order, on resume:** (1) `sacct -j 1341254 -X --format=JobID,JobName%20,State,Elapsed,ExitCode`
on the login node to check T72's status (allowed command, no compute); (2) if COMPLETED, read
`T72`'s own report/log file off the cluster first (fixed order: report before trusting), confirm V3=PASS
on the full 48-cell grid; (3) if PASS, T30's V3 gate is fully closed — make the Figure 6 rescoping decision
(average-profile vs. full-model, two-way; the plan doc explains both options, read before deciding, do
not just guess); (4) if T72 is not yet done, there is nothing to collect — do not poll repeatedly, check
once and either collect or note it is still running and move to whatever other WP11/WP10 work is available;
(5) after T72/Figure 6 close out, WP11 is fully done and the critical path moves to **WP10 (manuscript
rewrite)**, then **WP13 (venue/submission package)** — continue "til the end" per the standing author
instruction, updating this prompt and the plan log after every step.

---

## 0.0000000000000 EARLIER STATE (2026-09-21, plan log entry (do), T74) — HISTORY, kept for the record.

**T74 is DONE. Figure 9 (threshold sensitivity, SI) accepted** — job `1341260` finished in 4 seconds, both
required checks passed (a hand-read spot check and a full row-count check), and the picture was pulled
and looked at directly, not just trusted from the report. One real, useful finding for the SI text: the
paper's chosen model never wins by being the *only* one that clears every gate — it wins by scoring best
among however many models clear the gates, across all 21 threshold settings tested. It only gets replaced
by a different model in 2 of those 21 settings.

---

## 0.000000000000 EARLIER STATE (2026-09-21, plan log entry (dn)) — HISTORY, kept for the record.

**Four jobs live on the cluster, none waited on, none blocking each other:**
- **T72** (checker fix, job `1341254`) — still running, not yet collected.
- **T74** — Figure 9 (threshold sensitivity, a small reader-facing supplement chart). Source file
  confirmed small and simple (`T04/T04_out/threshold_sensitivity.csv`, 21 rows).
- **T75** — Figure 8 (proof that 200 sample homes is enough, a supplement chart). Source likely
  `T28/out/t28_b4_convergence.csv`; the employee must first read `T54`'s own report confirming that
  number is trusted before using it, and must judge for itself whether `T48`'s files really belong here
  or are an unrelated check that happens to share a task number.
- **T76** — Figure 1 in WP11's own numbering (at-home fraction by hour, across years and scenarios — NOT
  the manuscript's workflow-diagram Figure 1, already done). This is the least settled of the three: two
  things are unconfirmed and are the employee's own first job — what `T20`'s `main`/`null` split actually
  means, and where a 2022 at-home-by-hour baseline exists at all (not yet found by the manager). The
  employee has a **hard-stop instruction**: if the 2022 baseline needs real new computation, stop and
  report back rather than silently growing into a bigger job.

Full detail: plan log entry (dn) in `00_REVISION_PLAN.md`.

**Next, in order:** (1) collect all four jobs as each lands (`sacct` COMPLETED, report file read first,
fixed order as always); (2) if T72 confirms PASS on the full 48-home-set, close T30's V3 gate and decide
Figure 6 (average-profile vs. full-model, two-way); (3) T76 may come back saying it needs a follow-up task
rather than a finished figure — that is a fine, informative outcome, not a failure; (4) update the
tracker artifact and this prompt as each of the four lands.

---

## 0.00000000000 EARLIER STATE (2026-09-21, plan log entry (dm)) — HISTORY, kept for the record.

**T73 ACCEPTED — Figure 7 done.** Job `1341255` finished clean (7 seconds). It compares measured
electricity load in Toronto against the simulated version, 2022, on the rebuilt runs — the second
reviewer's main ask.

One real finding, clearly flagged, not hidden: the underlying data (from T70, already accepted) never
saved an hour-by-hour curve — only five whole-day numbers per season/day-type group (how peaky the day
is, how much load sits at midday, what hour the peak falls on, and the day's peak size). So the figure
shows those five numbers across 12 groups (four seasons times three day types) instead of a 24-hour
line — stated plainly in the figure's own caption. A second small mismatch (one of the five numbers uses
different units on the measured vs. simulated side) is also flagged, not hidden — that one bar is drawn
with a hatch pattern and marked "not comparable."

The manager checked this was real, not just taken on trust: the cluster job's own recorded check numbers
match the employee's earlier test on the same real file exactly, and the manager opened the actual
picture and confirms it looks right — five clean panels, all 12 groups present, the flagged bar visibly
different.

**T72 (the checker fix) is still running on the cluster, not yet collected.**

Full detail: plan log entry (dm) in `00_REVISION_PLAN.md`.

**Next, in order:** (1) collect T72 when the cluster shows it finished — if the fixed check confirms
PASS on the full 48-home-set, T30's last open gate is closed and Figure 6 (average-profile vs.
full-model, two-way) can finally be decided; (2) directory-confirm and scope Figures 1/8/9 (T20/T26 for
figure 1, T28/T48/T54 for figure 8, T04 for figure 9); (3) update the tracker artifact with T73's
acceptance and, once it lands, T72's.

---

## 0.0000000000 EARLIER STATE (2026-09-21, plan log entry (dl)) — HISTORY, kept for the record. §0.00000000000 above is the state.

**Checking T30's status for Figure 6 surfaced an uncollected job.** `T61` (job `1329796`) finished on
2026-09-18 and sat unread for three days. It reported `VERDICT: V3=FAIL` (0 of 48 cells showing one
shared occupancy schedule, when the whole point of T30's arm is that every household in a cell shares
ONE averaged schedule) — but all four of its own controls ran cleanly, so this looked like a real result,
not a crash.

**It is a checker bug, not a data defect — hand-proven on real files, not just reasoned about.**
`t30_check.py:248` drops the wrong index when comparing households' injected schedules
(`obj[1:]` instead of `obj[2:]` — eppy's object list has the constant type keyword at index 0 and the
actual per-household Name at index 1, so the buggy slice keeps each household's unique Name inside the
comparison and guarantees every household looks "different" no matter what the real values say). The
manager pulled two real households' actual injected IDFs from the same cell
(`SingleD__Toronto_5A__2022`, households 32811 and 18326) and read their occupancy schedule blocks side
by side: every field after the Name line is byte-identical between the two. **T30's averaging worked
correctly. The gate's own code was wrong.**

**Two small tasks dispatched, both independent, both cluster jobs, both no-parking (submitted, not
waited on):**
- **T72** — fixes the one-line index bug in a new script (the original buggy script is kept untouched
  as the record of the bug), re-runs the check on the full 48-cell grid, with a seen-failing control
  (old bug reproduced on the same tree) and a seen-working control (fixed logic still catches a real
  planted violation) plus 2 more hand-verified household pairs. Brief:
  `impl/2026-09-21_T72_T30_v3_indexing_fix.md`.
- **T73** — plots **Figure 7** (measured vs. simulated 2022 load shape — the second reviewer's main
  point) from T70's already-accepted comparison data. T70 only produced the numbers, never the figure.
  Brief: `impl/2026-09-21_T73_wp11_figure7_measured_vs_sim.md`.

Full detail: plan log entry (dl) in `00_REVISION_PLAN.md`.

**Next, in order:** (1) collect T72 — if the fixed check confirms PASS on the full grid, T30's last
open gate is closed and Figure 6 (average-profile vs. full-model, two-way, per the earlier rescoping
note) can finally be decided; (2) collect T73 and view Figure 7 directly before accepting; (3)
directory-confirm and scope Figures 1/8/9 (T20/T26 for figure 1, T28/T48/T54 for figure 8, T04 for
figure 9); (4) update the tracker artifact (currently Version 77 — owed T69's, T70's, T71's acceptances
and this T61-recovery finding, none of which are reflected yet).

---

## 0.000000000 EARLIER STATE (2026-09-21, plan log entry (dk)) — HISTORY, kept for the record. §0.0000000000 above is the state.

**T71 (four WP11 figures) collected and ACCEPTED** — job 1341185, 54s runtime, exit 0:0. Manager
ran two independent from-scratch cross-checks (not just trusting the employee's self-report):
grepped the raw hourly-profile CSV directly for the seen-working control's cell (exact match), and
parsed the change-table CSV with a real CSV reader for the load-factor CI row (exact match). All
four figures visually inspected by the manager, not just file-existence-checked:
- **Figure 3** (intraday load shape by scenario) is genuinely informative: S-Revert-std shows a
  flatter midday and higher evening peak than the other three 2030 scenarios — the expected
  work-from-home signature.
- **Figure 4** correctly separates peak/ramp (no confidence interval exists in the accepted data,
  shown hatched and labelled) from load factor (real bootstrapped CI, shown solid with an error
  bar) — confirmed by eye, not just from the CSV's status column.
- **Figure 5** (the first reviewer's own requested end-use x hour figure) has zero cells silently
  presented as solid data that were actually missing — checked directly, 0 of 192 cells flagged
  NOT_EVALUABLE.
- Figure 3's household count (1198, the four-way common basis) independently reproduced by the
  script and matches the already-accepted number exactly — this is now the third independent
  reproduction of that figure in this project.

**WP11's four T68/T69-derived figures (annual by end use, intraday shape, peak/load-factor/ramp
with CIs, end-use x hour difference) are DONE.** Full detail:
`impl/2026-09-21_T71_wp11_figures_wp6_set_IMPL.md`'s "Manager collection" section, plan log entry
(dk). T70's acceptance (WP5 redo, the second reviewer's main point) is recorded in plan log entry
(dj) and `impl/2026-09-21_T70_wp5_measured_vs_rebuilt_IMPL.md`.

**What's left in WP11:** Figure 7 needs its own small plotting task now that T70's underlying data
is accepted (T70 only produced the comparison CSVs, not a figure). Figure 6 stays blocked on T30's
scoring plus a manager rescoping call. Figures 1/8/9 still need their source paths confirmed by
directory listing before they can be scoped as tasks.

**Next, in order:** (1) dispatch a small task to plot Figure 7 from
`T70/out/sim_vs_measured_toronto_2022_shape_rebuilt.csv`; (2) check T30's status, and if collected,
make the Figure 6 rescoping call; (3) directory-confirm and scope Figures 1/8/9; (4) update the
tracker artifact (currently Version 77 — owed T69's, T70's, and T71's acceptances, none of which
are reflected yet).

---

## 0.00000000 EARLIER STATE (2026-09-21, plan log entry (dj)) — HISTORY, kept for the record. §0.000000000 above is the state.

**T70 collected and ACCEPTED** — job 1341184, controls-first order followed (`run_meta.json` first,
never `sacct` alone):
- All 200 Toronto runs loaded clean (50/50/50/50 per archetype), zero skipped.
- C5 sanity bound holds tightly for all four archetypes: the occupancy-only rebuild moved
  whole-building annual electricity by only 0.1-0.7% versus the old retired runs — the expected
  result (rebuild changes *when* energy is used, not roughly *how much*).
- Both deliverable CSVs match `run_meta.json`'s row counts exactly, both calendars and both
  measured scopes present, every row tagged `data_vintage=rebuilt_2022`, zero NaN/inf.
- **Seen-working control fired clean**: independently re-read `T02_out/ieso_metrics.csv` at the
  Toronto/2022/shoulder/weekday cell and matched all four metrics exactly against the join file,
  via a fresh file read separate from the employee's own code.

**This is the data behind WP11 Figure 7 and directly answers the second reviewer's main point on
the rebuilt runs (not the retired ones T15 used).** Full detail:
`impl/2026-09-21_T70_wp5_measured_vs_rebuilt_IMPL.md`'s "Manager collection" section, plan log
entry (dj).

**T71 (four WP11 figures) is still running** — background employee agent, no manager polling,
collect on its completion notification.

**Next, in order:** (1) collect T71 once its notification lands, same fixed controls-first order;
(2) dispatch a small follow-on task to actually plot Figure 7 from T70's numbers (T70 produced only
the underlying comparison CSVs, not a figure); (3) once T30 (WP3 average-profile scoring) is
collected, revisit Figure 6's rescoping; (4) scope Figures 1/8/9 as a follow-on task with confirmed
source paths; (5) tracker artifact (currently Version 77) owed an update for both T70's acceptance
and T71's eventual result.

---

## 0.0000000 EARLIER STATE (2026-09-21, plan log entry (di)) — HISTORY, kept for the record. §0.00000000 above is the state.

**WP11 triage against the nine-figure list, then two tasks dispatched.** Not all nine figures are
dispatch-ready:
- **Figures 2/3/4/5** (annual by end use, intraday shape by scenario, peak/load-factor/ramp CIs,
  end-use x hour diff) need only T68/T69's already-ACCEPTED output — **dispatched as T71**.
- **Figure 6** (static + average profile, WP3) is BLOCKED — the static half (T22) was already ruled
  "not home-for-home" and unusable; the average-profile half (T30) is scored but not yet accepted.
  Needs T30 collected + a manager rescoping call before dispatch.
- **Figure 7** (measured vs simulated, WP5) is the **second reviewer's main point** and had sat
  undispatched at "Later" since mid-September — found and fixed today. **Dispatched as T70**: reruns
  T15's already-validated method (scale-free shape, eplus-calendar fix, IDF dwelling counts) on the
  REBUILT 2022 runs (`T21/out/step8/.../2022/`) instead of T15's old retired-output tree. Measured
  side (`T02_out/ieso_metrics.csv`) unchanged, still trusted.
- **Figures 1/8/9** (at-home-by-hour, N=200 convergence SI, threshold sensitivity SI) not dispatched
  yet — their exact source files were not directory-confirmed before this entry, and per this
  project's own rule every task confirms its own input paths, not guessed by the manager in advance.

**T70 and T71 dispatched in parallel** as fresh Sonnet employee agents, cluster-only,
submit-and-end-turn discipline, both currently running (background, no manager polling). Briefs:
`impl/2026-09-21_T70_wp5_measured_vs_rebuilt.md`, `impl/2026-09-21_T71_wp11_figures_wp6_set.md`.

**Next, in order:** (1) wait for both agents' completion notifications (dispatch reports — JobID,
local verification, anything flagged); (2) collect each job in the fixed order once `sacct` shows
COMPLETED — `run_meta.json`/seen-working control first, then results, same discipline as every prior
task; (3) once T30 (WP3 average-profile scoring) is collected, revisit Figure 6's rescoping; (4)
scope Figures 1/8/9 as a follow-on task with confirmed source paths; (5) tracker artifact (currently
Version 77) owed an update once T70/T71 land.

---

## 0.000000 EARLIER STATE (2026-09-21, plan log entry (dh)) — HISTORY, kept for the record. §0.0000000 above is the state.

**T69 ACCEPTED.** Job `1341180` COMPLETED (00:03:23 elapsed, exit 0:0). Full controls-first
collection done independently by the manager (not just the employee's self-report): `run_meta.json`'s
`controls_all_fired` read first — `true` for S-None, S-Partial, S-Revert-std — then `controls.json`
for C1–C4, then results.

Verified directly: household counts match items 30/33 exactly (S-None=1198, S-Partial=1200,
S-Revert-std=1199); `n_discover_skipped=0` on all three arms; C2 hand-check relative diffs
4.9e-11 to 1.4e-12 (annual), ~5e-8 (peak) — far inside the 5e-6 tolerance, matches the employee's
hardcoded numbers exactly; C3 divisor invariance ~1e-14 (machine precision); `cross_scenario_common_basis.csv`
(11 rows) matches the run log, four-way intersection = 1198; zero NaN/inf in any change-table CSV; the
144 scipy `RuntimeWarning`s in the real log are the same benign zero-variance artifact the employee
diagnosed in its synthetic test — confirmed harmless. S-Revert-std's one undelivered household
(`OtherDwelling__Vancouver_5C` sample 9 / `HH129937`) is the same one item 33 already named.

**All four flagged items ruled, none needed rework.** Item 4 (T68+T69 concatenation) is now
**APPROVED** — schema confirmed identical by direct header inspection; WP11's figure script may
`pd.concat` all four scenario files directly.

**WP6 (Parts A + B) is CLOSED.** Per plan §4's critical path, **WP11 (figures) is next**, then WP10
(rewrite), then WP13 (submission package) — continuing per the author's "go til the end" instruction.

**Next, in order:** (1) scope WP11 — nine figures per plan §4, identify which need T69/T68's
end-use-by-hour output (at least two do); (2) dispatch figure-generation as a fresh employee task,
cluster-only where the 511 MB hourly-profile CSVs are needed, local otherwise; (3) collect and accept
each figure controls-first, same discipline as every prior task; (4) tracker artifact (currently
Version 76) is owed an update for T69's acceptance and WP11's kickoff.

---

## 0.00000 EARLIER STATE (2026-09-21, plan log entry (dg)) — HISTORY, kept for the record. §0.000000 above is the state.

**T69's dispatch report is in.** Job `1341180` submitted (`-p ps -c 8 --mem=32G -t 7-00:00:00`),
running on speed-21. `sacct` at last check: still `RUNNING`, 00:01:23 elapsed (T68's one-arm run was
84.8s, so three arms taking longer is expected, not a red flag).

Employee's own local verification (not yet independently checked by the manager — that happens at
collection): directory counts matched items 30/33 itself (T29 λ0.0=1198, λ0.5=1200, T32 std=1199,
T21 2022=1200); hand-computed reference values for one real household across all three trees via a
non-pandas code path; `py_compile` clean; synthetic-tree test (orphan household, 2022-only household,
engineered `undelivered.csv` row) with all four controls firing on all three arms.

**Four items flagged, all four RULED, none blocks the run:** (1) C2 uses a hand-check only, no
aggregate-CSV reproduction — correct, the brief required this since T67/T29's aggregates are
untrusted here. (2) midday_share/load_factor rows are a new bootstrap computation, not a T67 reuse —
correct, T67 never scored these trees. (3) `cross_scenario_common_basis.csv` has pairwise + four-way
rows only, no three-way — matches the brief's literal wording, nothing missing. (4) T68's file (S-Full)
is not concatenated in — correct, that's explicitly a manager decision at collection. Full text: plan
log (dg).

---

## 0.0000 EARLIER STATE (2026-09-21, plan log entry (df)) — HISTORY, kept for the record. §0.00000 above is the state.

**Author instruction this session: continue autonomously to the end (submission), updating this file
and the plan log at every step.** Per plan §4's own critical path, WP6's scenario decomposition comes
before WP11 (figures), since two of the nine planned figures need it — so WP6 Part B is next, not
figures.

**T69 (WP6 Part B) is dispatched** to a fresh Sonnet employee, cluster-only, submit-and-end-turn.
Brief: `impl/2026-09-21_T69_wp6_partB_scenarios.md`. Scope: end-use x hour decomposition for the three
scenario arms (T29's two work-from-home lambda arms, T32's population-mix-fixed fourth scenario)
against T21's 2022 baseline, same rigor as T68. Two path facts found before writing the brief:
T29/T32's scenario trees are **2030-only** (T68's discovery logic cannot be reused unmodified), and
**T32's household files live at `T32/step8_std/out/...`, not `T32/out/...`**. Also ruled: neither
`t29_p3_deltas.csv` nor `t32_metrics_std.csv` may serve as a validation reference (both carry numbers
plan item 30 already ruled not-on-common-basis) — T69 must hand-check a fresh reference household per
scenario tree instead. Full ruling text in plan log (df).

---

## 0.000 EARLIER STATE (2026-09-21, plan log entry (de)) — HISTORY, kept for the record. §0.0000 above is the state.

**T68 / WP6 Part A is done.** Job `1340956` `COMPLETED` exit `0:0` in 00:01:59 (fast because it
re-processes already-simulated files, not new simulations). `run_meta.json`'s `controls_all_fired`
read `true` first, then `controls.json` confirmed all four of C1-C4 individually `ran_and_fired`.
`n_households_year_read_ok = 2400`, matching 1,200 households x 2 years exactly. The one thing the
dispatching entry flagged as unverified — whether all 24 T21 cell names have keys in both divisor
dictionaries — is now checked key-by-key and clean, no missing key. The employee's new
`stock_weighted_cluster_bootstrap` function was read line by line on the cluster (item 39's standing
rule for anything named "cluster bootstrap") and is a genuine cluster bootstrap, not stratified.
Full detail: plan log (de), IMPL doc
`impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md` (now Status: DONE).

**Cluster is fully idle for 2J** (fresh `squeue` read, zero non-`histnu` rows). Nothing is running,
nothing is owed.

**Next, in order:** (1) dispatch WP6 Part B (T29/T32 scenario arms — inherits item 30's
common-household rule and item 33's reproducible reversion-side exclusion, so its brief cannot just
copy T68's) or WP11 (figures) — recommend WP11 first since it carries no open household-set caveat to
design around before dispatch; (2) WP10 stays gated on WP6/WP8/WP11, WP13 on WP10; (3) tracker page
still owes a republish with T68's result (not yet done this session).

---

## 0.00 EARLIER STATE (2026-09-20 late night, plan log entry (dc)) — HISTORY, kept for the record. §0.000 above is the state.

**The cluster is empty of 2J work and nothing failed.** A fresh `squeue` + `sacct` read (not the
file's own table) shows the queue holds **only `histnu`-named tasks** — 32 running at 1 CPU plus 1
pending — which belong to the other project the author reserved the second 32 CPUs for. Every 2J job
since 2026-09-19 is `COMPLETED` exit `0:0`: `1340509_15` (T22's third attempt, 01:31:24 — **T22 is
24/24 clean**), `1329258` (T48), `1329278` + `1340675` (T49 and its clean re-run), `1340676` (T64),
`1340682` (T66), and T67's `1340720` / `1340721` / `1340722`. The only `CANCELLED` rows are
`1328310_15` and `1340507_15`, the known hung and crowded T22 attempts already superseded and already
written up in (ct)-(cv). **Nothing is owed on any 2J job.**

**Not ours:** `1339757` (`wp9_stage3_RC6`) **FAILED 1:0** after 1 d 04 h, and `1339756`
(`wp9_stage3_RC1`) FAILED 1:0 after 04:03:38. Those are **1J project** jobs with their own session and
their own manager prompt. Named here only so the record shows they were seen and deliberately not
touched.

**T68 is RUNNING as job `1340956` — WP6 Part A, end use x hour on the corrected 2022 AND 2030 rebuild.**
Task doc `impl/2026-09-20_T68_wp6_enduse_hour_corrected.md`, state file
`impl/2026-09-20_T68_wp6_enduse_hour_corrected_IMPL.md` (8 CPUs, 32 GB, 7 days, node `speed-07`,
started immediately). Outputs under `/speed-scratch/o_iseri/2J_revision/T68/out/`, log
`logs/t68_run.out`. **Collection order is fixed and is not negotiable: read the `_IMPL.md` Ledger, then
`run_meta.json`'s `controls_all_fired` boolean, then `controls.json`, and only then any number.**
`sacct` is never the verdict. **Four things in that job are the manager's to rule on before any
interval is quoted** (plan entry (dd) has them in full): the employee wrote a **new**
`stock_weighted_cluster_bootstrap` — read it line by line, because item 39's whole lesson was a
function *named* cluster bootstrap that was stratified; per-cell rows carry a paired t-interval, not a
cluster bootstrap, so the two intervals in WP6 are **not the same statistic** and the text must say so;
every CI is denominated in **percent change** (raw kWh columns are still there); and the per-cell
zero-2022-denominator column had a bug fixed just before upload, so spot-check it on real data. Also
check key by key that all 24 T21 cell names exist in both divisor dictionaries — the employee assumed
this from the shared naming convention and flagged it as unverified. Scenario arms (T29's lambda arms, T32's
S-Revert-std) are deliberately **not** in T68; they carry item 30's common-household rule and item 33's
reproducible reversion-side exclusion and become **WP6 Part B** once Part A's basis is proven.

**The one ruling from that brief you must not re-open, because it decides what WP6 can deliver:**
T66 derived unit-equivalent divisors for **equipment and lighting only**. Nothing derives a divisor for
fans, the HVAC+DHW electricity remainder, `Electricity:Facility`, or any `*:EnergyTransfer` thermal
meter. Therefore **relative quantities are divisor-invariant and are WP6's quotable core** — percent
change, share of the facility total, share of the day's energy in an hour, load factor, midday share,
peak hour, ramp as a fraction; dividing every hour by one constant changes none of them. **Absolute
per-dwelling kWh exists only for equipment and lighting**, plus everything in SingleD (divisor 1).
Every other meter's per-dwelling absolute is `NOT_EVALUABLE` with its reason, and its whole-building
raw value is reported under a plainly-named whole-building column. **No divisor may be invented and
the equipment divisor may not be reused for fans.** Intervals reuse **T67's own
`cell_cluster_bootstrap.py`** so every WP6 interval sits on one basis (whole cells, 24 drawn from 24),
and the T28/T60 rule is written into the output file itself: **every 2022-to-2030 change row carries
its interval and an explicit `excludes_zero` flag, and no per-cell load-shape change is called a
change unless its own interval excludes zero.**

**Next, in order:** (1) collect T68 — its `_IMPL.md` Ledger, then its report, controls first;
(2) dispatch WP6 Part B (scenario arms) or WP11 (figures), checking `squeue` first for headroom under
the 32-CPU 2J ceiling; (3) WP10 stays correctly gated on WP6/WP8/WP11 and WP13 on WP10.

---

## 0.0 EARLIER STATE (2026-09-20, plan log entries (cw)-(da)) — HISTORY, kept for the record. §0.00 above is the state.

**All four 2J jobs that were live at the last close (`1340509_15`/T22, `1329258`/T48, `1329278`/T49,
`1329220`/T32) finished clean, exit `0:0`, nothing queued or pending.** Confirmed by a fresh `squeue`+`sacct`
read: the queue holds only unrelated jobs (`histnu`-named tasks and `1339757`, the separate 1J project).

- **T22 is now 24/24 clean.** `1340509_15`: `Successful: 50/50, Failed: 0/50`, `exit=0`.
- **T48 (A5/A6 full-grid) landed with a real, new finding — not the one item 26 predicted.** A6
  (peak-shift) is trusted and PASSES 48/48 on the rebuild. **A5 (energy gate) fails 36/48 on the rebuild
  (514% to 8055% overshoot) for every MidRise/HighRise/OtherDwelling cell, while the identical script
  passes 48/48 on the published tree, and SingleD passes on both.** This is a real regression in the
  rebuild's own data, not the old known validator gap (that gap is real but present on both trees, so it
  cannot explain why only one of them fails). **No MidRise/HighRise/OtherDwelling energy number may be
  quoted from the rebuild until this is diagnosed.** Full detail: plan log (cw), `T48/t21_a5_results.csv`
  vs `T48/pub_a5_results.csv`.
- **Three fresh employees dispatched, all cluster-only. Two have landed and are CLOSED:**
  - **T63 — CLOSED.** Re-ran the existing T49 checker clean. Result: **all 24 cells, every archetype,
    show completely disjoint household ID sets** between the static-schedule arm (T22) and the published
    campaign — 0/24 matching. **Item c8 (WP3 static-vs-diary comparison) is closed as not
    household-paired**; no number from it is quotable as-is. Plan log (cx).
  - **T64 — CLOSED.** Found T32's own `undelivered.csv` directly (confirms item 33 by measurement, not
    just carried-forward text): one row, `OtherDwelling__Vancouver_5C` household `129937`, same as T29's.
    T32's population-level household set is byte-identical to all three of T26's (0 symmetric difference
    everywhere) — **item 30's rule does not touch T32's already-accepted G0/SC1/SC4/SC5 numbers.** Only
    T32's own 1,200-run energy campaign is 49/50 for that one cell, same known shape as T29. Plan log (cy).
  - **T65 — CLOSED. Good news, not a bug.** Found the exact mechanism with no cluster job needed
    (login-node spot checks + a local IDF `diff`): a deliberate 2026-07-13 fix in
    `eSim_bem_utils_2J/integration.py` (to correct an earlier "phantom-peak" defect) now broadcasts each
    household's calibrated equipment load across every dwelling-unit-equivalent zone in a multi-unit
    building — physically correct — but `step9_validate_full.py`'s SHEU energy gate (A5) was never
    updated to divide the resulting whole-building meter by the real unit count. The overshoot ratio
    matches each archetype's real unit-equivalent zone count almost exactly (HighRise 81.5x measured vs
    80 units counted, MidRise 33x vs 32, OtherDwelling 6.14x vs 7 partially offset by an existing fix,
    SingleD no inflation). **Reverting the simulation fix is rejected** (it would reopen the phantom-peak
    defect); the validator needs the fix instead. Plan log (cz).
  - **T66 — CLOSED, item 40 fully resolved.** Job `1340682` COMPLETED in 54:58. Seen-failing control
    (original, unmodified validator on the same T48 tree) reproduced T48's ground truth exactly, **12/48
    PASS** — proves the tree did not drift and the comparison is apples-to-apples. Per-cell
    unit-equivalent divisors computed from each cell's own `eplusout.eio`: SingleD=1, OtherDwelling=7,
    MidRise=33 (equip)/36 (lighting), HighRise=81 (equip)/90 (lighting) — one divisor per archetype
    covers all 6 cities, uniform. Corrected validator (new file, original untouched): **48/48 PASS** at
    full grid. Before/after table confirms T65's diagnosis was exact, not coincidence (e.g. HighRise
    ~+8,000% raw overshoot collapses to under 1% after dividing by 81). Plan log (da).
- **Ruling: MidRise, HighRise, and OtherDwelling energy-intensity numbers from the rebuild are now
  QUOTABLE, same footing as SingleD.** Report the corrected script's 48/48 as the A5 result; the original
  script's 12/48 is the seen-failing control only, never a result. A6 unaffected, stays PASSED.
- **Wave 4 audit done.** WP6 (end-use x hour, corrected 2030/scenarios) and WP11 (figures) are not
  started but are now unblocked (inputs all landed); WP10 (rewrite) is prep-only so far, correctly
  gated on WP6/WP8/WP11; WP13 not started, correctly gated on WP10. **WP8 had a real, already-diagnosed
  bug never yet fixed: item 39, `method_b_cluster_bootstrap` in `impl/T03_scripts/ci_reproduction.py`
  is a mislabeled STRATIFIED bootstrap (resamples households within each fixed cell, never resamples
  which cells appear), which is why it reported the confidence interval getting narrower — the
  opposite of what real clustering should do.** Task doc written (never edit the T03 original):
  `impl/2026-09-20_T67_wp8_genuine_cluster_bootstrap.md`. **T67 dispatched** as a fresh Sonnet employee,
  cluster-only, no waiting: find/build the corrected `agg_annual.csv` from the T21 rebuild tree (never
  the old defective one), write a genuine cell-level cluster bootstrap in a new copy of the script,
  prove it on a seen-failing control first, then run it for real and report method A (pooled) vs the
  new genuine cluster bootstrap vs the old retired number (labeled do-not-quote) for both
  `midday_share` and `load_factor`.
- Tracker republished at Version 72 with T66's result and T67's dispatch (numeric outcome below is
  not yet reflected in the tracker page — owed next republish).
- **T67 CLOSED. All three jobs read directly off the cluster, all `sacct` exit `0:0`, plan log (db):**
  `1340720` built the corrected `agg_annual.csv` clean (2,400 rows, 24 cells, 50 households/cell/year,
  zero missing/short series). `1340721` (seen-failing control, OLD data) reproduced the retired
  "1.0-3.3% narrower" figure exactly, confirming the control is scored right. `1340722` (the real
  number, on the corrected data): **midday_share's genuine cluster-aware interval is 39.8% WIDER than
  the plain pooled interval (0.002433 vs 0.001741) — a real, material clustering effect** — while
  **load_factor is 2.3% narrower (negligible, plain interval is fine alone)**. Both metrics' intervals
  exclude zero either way, so no existing conclusion changes.
- **Item 39's Ruling 1 fulfilled: the promised SI clustering section is written**, with the full
  side-by-side table and the retired do-not-quote number, at
  `manuscript/draft_SI_clustering_ci.md` (new section S.10, following S.5-S.9 in the schedule-completion
  SI draft). **Ruling 5 checked: no main-text point estimate or separability claim for either metric
  exists yet anywhere in the drafts** (WP6/WP11 haven't started), so nothing needed correcting today —
  the new SI section instructs whichever future task writes that sentence to cite the wider,
  cluster-aware interval for midday share.
- **Next:** republish the tracker with T67's closed result. Then re-check Wave 4 for the next
  unblocked task — WP6 (end-use x hour decomposition on corrected 2030/scenario runs) and WP11
  (figures) are both still unstarted and unblocked; dispatch one next, checking `squeue` first for
  CPU headroom under the shared 32-CPU ceiling with the 1J project.
- **Documentation cleanup done the same session, no new findings:** plan items 26, 27, 32 and 33 still
  carried their original "OPEN QUESTION" headers even though later Progress Log entries had already
  closed all four. Each header now carries a short closure pointer to the log entry that actually
  resolved it ((cw)/(cz) for 26, (cx) for 27, the post-(cm) entry for 32, (cn)+(cy) for 33), with the
  original text kept below for the record. Also removed one stray, out-of-date "Next" line at the very
  end of the plan file that still said T65 was outstanding, after T65 had already landed and been fully
  written up above it in entry (cz). **The plan's log is still the state; this only fixed stale
  headers/lines so a cold reader does not re-open closed questions or chase a task that already
  finished.**

---

## 0. COLD START (2026-09-20 morning, plan log entry (cv)) — now HISTORY, kept for the record only. See §0.0 above for the current state.

**The author is stepping away deliberately, mid-session, not at a natural closure point.** Nothing is
abandoned: every `sbatch` job runs without a session. **Do not re-dispatch anything below on the assumption
it was lost — re-read the cluster first, the same rule (cr) and (ct) both exist to enforce.**

**Step 0.1 — re-read the cluster before trusting one word of this file's job table.**

```
ssh -o BatchMode=yes o_iseri@speed.encs.concordia.ca "squeue -u o_iseri -h -o '%.12i %.18j %.9T %.5C %.11M' | grep -v histnu; sacct -j 1340509,1329258,1329278 -X -n -o JobID%16,State%12,ExitCode%8,Elapsed%12"
```

**What happened this session (full detail in plan entries (ct), (cu), (cv) — read those, this table is a
summary only):**

1. Fresh cluster read found `1328310_15` (T22's last static cell) had been `RUNNING` past **3 d 23 h**
   while its own log (`T22/logs/t22_1328310_15.out`) showed all 50/50 homes finished and a `DONE` line
   printed on **16 September, 14:59** — nothing written since. `sstat` showed only ~4.5 h of real CPU time
   burned in that whole span. **Diagnosed as hung, not slow**, cancelled with author go-ahead.
2. **Root cause found (entry (cu)):** `T22/T22_scripts/t22_array.sh` never sets `ESIM_WORKERS`, so
   `simulation.py:run_simulations_parallel()` defaults `max_workers` to `os.cpu_count()` — the **whole
   compute node** (32), not the job's actual `--cpus-per-task=4`. Cell 15
   (`MidRise__Montreal_6A`, a 27-zone apartment model, the heaviest IDF in the set) is the one cell that
   blew the 16G memory ceiling trying to fork 32 workers (`OSError: Cannot allocate memory`,
   `t22_1328310_15.out:924-930`), fell back to sequential, ran fine, then likely never closed cleanly — a
   known Python failure mode when a `ProcessPoolExecutor` crashes mid-spawn, though this last step is
   inferred, not proven (the process was gone by the time it was checked). **This is a latent bug in every
   T22 cell**, not just this one; worth checking whether T19 shares `simulation.py` and has the same gap.
3. First resubmit (`1340507_15`, before the fix) **visibly repeated the crowding** — 0 of 50 done after
   6 minutes, 32 workers again. Cancelled a second time.
4. **Fix applied (entry (cv)):** `export ESIM_WORKERS=4` added to `t22_array.sh` (downloaded via `scp`,
   edited locally, re-uploaded — no edits on the login node). Resubmitted clean as **`1340509_15`**, running
   with the cap in place as of this write-up.
5. Cancelling `1328310_15` (step 1) satisfied `--dependency=afterany:1328310` for both T48 and T49, so
   **both started running immediately, days earlier than the array's actual completion.** T48 (`1329258`)
   is still running. **T49 (`1329278`) already finished** (00:01:25) with verdict
   `B1=FAIL, B2=PASS, B3=PASS, B4=FAIL` — read but **not yet adjudicated**:
   - **B1 FAIL is very likely stale timing, not a real finding** — its own offender line names
     `1328310_15 state=CANCELLED+`, i.e. T22 was mid-cancel when T49 ran. **Re-run T49 once `1340509_15`
     lands and T22 is a clean 24/24.**
   - **B4 FAIL looks real.** Every MidRise/HighRise cell it printed (6 cities x 2 archetypes) shows the T22
     static-arm household sample and the published campaign's sample as two different ID lists for the
     same cell, no overlap shown. Matches the risk item c8 on the checklist already flagged before this
     session. SingleD/OtherDwelling not confirmed either way from this read. **If this holds, no WP3
     static-schedule number (checklist item c8) may be quoted until it is resolved — same family as items
     27/30's earlier household-set mismatches.** This is entry (cs)'s own prediction ("Expect B4 to fail")
     landing true; still needs its own full read, not just this flag.
6. T32 campaign (`1329220`) finished clean, 24 of 24, overnight before this session started. **No collector
   sent yet** — still owes item 30's common-household rule and reading `undelivered.csv` (item 33).

**Live at close:**

| job | what | state at close |
|---|---|---|
| `1340509_15` | **T22**, cell 15, third attempt, `ESIM_WORKERS=4` now set | RUNNING, well under an hour in |
| `1329258` | **T48**, full-grid A5/A6 | RUNNING |
| `1339757` | `wp9_stage3_RC6` — **1J project, not 2J**, unrelated, do not touch | RUNNING (own session) |

**Step 0.2 — what to do next, in order.**

1. Read `T22/logs/t22_1340509_15.out` and `sacct -j 1340509`. Expect it in the same 30 min–4.5 h range as
   its 23 clean siblings, now that the worker count is capped. If it crashes or hangs again, the
   `ESIM_WORKERS=4` fix did not address the real cause and this needs a fresh look, not a third blind
   resubmit.
2. Once it lands, T22 is 24/24. **Re-run T49** (fresh Sonnet, same brief as before) so its B1 line is read
   on a clean array rather than a mid-cancel one, and give **B4 a real, full read** — this is the item that
   decides whether checklist item c8 (WP3 static-schedule comparison) can be used at all.
3. Read `T48/logs/t48_a5a6_1329258.out` (**never `sacct`** for its verdict — same rule as every other
   collector in this project) when it finishes.
4. Dispatch a T32 collector (Step 2 remainder) — must read `undelivered.csv`, inherits item 30's
   common-household rule.
5. Consider whether T19's array script shares the same uncapped-`max_workers` gap as T22 and needs the
   same `ESIM_WORKERS` fix pre-emptively (not yet checked this session).

**Step 0.3 — after every one of those, run the full closure cycle, no exceptions.** Append a Progress Log
entry to `00_REVISION_PLAN.md` (now **3,147 lines** per `wc -l`, last entries **(ct), (cu), (cv)**); update §2/§3 and
the "Last updated" line of **this file**; read the live checklist page, diff it, `node --check` the
extracted script, republish in place (now **Version 68**); then send the author **one short reply**.

**Step 0.4 — standing habits, all binding.**
- **Never say "in parallel" unless an agent or job is live at that moment.** Idle is a fine answer; a false
  yes costs the author their evening. **A session never needs to stay open for cluster jobs.**
- **If there is unblocked non-cluster work in the plan, dispatch it before being asked.**
- **When a job sits `RUNNING` far longer than its neighbours, don't trust the scheduler state alone —
  read the job's own log for its last line and timestamp.** That is what caught (ct); `sacct`/`squeue`
  alone never would have.
- **Editing a script on the cluster: download with `scp`, edit locally, re-upload with `scp`.** Never edit
  in place on the login node (no `sed`/`vi` in the allowed command list).

---


**READ THIS FIRST -- what changed on 2026-09-18 morning, entry (cg).** A fresh manager session after a
context clear. First act was `sacct` over every live job rather than trusting this file's own table, and two
long-running arrays had finished overnight, both clean:
- **T28 (`1328415`) is DONE 4/4, exit `0:0`** -- the 200-household sample-size arm, 4 Montreal cells x 200 x 2
  years = 1,600 runs planned. Tasks `_0` 01:08:29, `_1` 03:11:56, `_2` 05:04:02, `_3` 05:11:39; last End
  2026-09-18T03:30:09. It had been the slowest set left.
- **T30 (`1328419`) is DONE 48/48, exit `0:0`** -- the average-profile arm, 24 cells x 50 x 2 = 2,400 runs
  planned; last End 2026-09-18T02:21:40.
- **T32's campaign (`1329220`) is 20/24**, two running, two pending, nothing failed.
- **T22 (`1328310`) is still 23/24.** Task `_15` alone has been running **1 d 22 h** and is now the ONLY thing
  holding `1329258` (T48) and `1329278` (T49), both still `PENDING` on `afterany:1328310`.
- Across every 2J job in this revision the only non-zero exit remains `1328428`, already fixed and rerun.

**Two collectors dispatched, one fresh Sonnet each, both controls-first:**
- **T54** scores T28 on B0-B5 -- `impl/2026-09-18_T54_T28_collector.md`, `-c 4 --mem=16G`, report
  `/speed-scratch/o_iseri/2J_revision/T54/logs/t54_t28_report.txt`. Four controls: B1 seen failing on a swapped
  household id, B2 seen failing on a perturbed meter file, a seen-working control on the untouched tree, and a
  **hand-arithmetic control** on the Student-t CI and subsample mean (the T28 Manager addendum requires it
  before any B3/B4 number is quoted). Also required: read each cell's live `Pool=` line and confirm pool >=
  1,045; `NO_REF` on any cell is a STOP, not a pass.
- **T55** scores T30 on V0-V5 plus the two spread metrics -- `impl/2026-09-18_T55_T30_collector.md`,
  `-c 1 --mem=16G`, report `/speed-scratch/o_iseri/2J_revision/T55/logs/t55_t30_report.txt`. `t30_check.py`
  has **never run against real full-grid output**, so V1 and V2 must be seen failing on a copied fake case
  first. **V1 is a STOP, not a reported difference.** The brief also names the six smoke leftovers sitting in
  `T30/out/` beside the 48 real cell-year directories (`cell_manifest.csv`, `sample_001_HH130168`,
  `sample_001_HH130228`, `sample_002_HH79150`, `sample_002_HH79252`, `SimResults_Plotting_Schedules`) and
  requires an explicit exclusion rule plus the excluded count in the report -- an explained mismatch is still
  printed, never silently dropped.
Both briefs carry the T53 lesson (read any `undelivered.csv`, print its **reason strings**, and state that its
absence in a tree that never writes one is uninformative rather than reassuring) and the T51 lesson (read the
**report text**, never `sacct`, when the wrapping job exits 0 on purpose).

**CPU accounting at dispatch:** running was 4 (T22 `_15`) + 8 (T32 at `%2`) = **12**. Worst case once everything
releases is 4 + 8 + 4 (T48) + 1 (T49) + 4 (T54) + 1 (T55) + 1 (T57) = **23**, inside the 32 ceiling. No `%N` and
no `--cpus-per-task` was raised. Checklist page republished (the live page is read and diffed before every
republish; at Version 52 it was byte-identical to the local source apart from the publish skeleton).

**Entry (ch), same morning -- two more employees out, neither waiting on the queue.** Author instruction this
session: *"continue till end, for every step update manager prompt."* So the writing track and the open WP2
question move now rather than after the collectors land.
- **T56 -- plan §5 item 28, the SI glossary table.** `impl/2026-09-18_T56_si_glossary_table.md`. **Writing only,
  no cluster.** R2-1 asked for two things and only one was delivered: the J3 detail moved to the SI, but the
  **one short glossary table has never been written** (a search for "glossar" across the tables tree and the
  revision manuscript folder returns nothing; the `J3` gloss in `Table_B1_B2.md` covers one term and is not
  that deliverable). Written to `writing/submission/tables/SI/Table_SI_glossary.md` from T33's
  `jargon_inventory.md`, with three rules fixed in advance: a term WP10 replaces everywhere earns no row (so
  "forecast" is out), a gloss may not contain a second self-defined label, and the target is roughly 8-14 rows.
  **The list of terms deliberately left out, with a reason each, is required alongside the table.** `J3` stays
  in the model card, glossed -- (ca)'s "never appears in prose" wording was already corrected by (cb).
- **T57 -- plan §5 item 33, the reproducible reversion-side exclusion.**
  `impl/2026-09-18_T57_reversion_pool_exclusion.md`. **Diagnosis only, 1 CPU, no fix and no re-run.** The
  mechanism is already located and written into the brief as a starting point, not as the answer:
  `load_schedules()` deletes every household for which `validate_household_schedule()` is False
  (`integration.py`, the `invalid_ids` block at 432-438) -- exactly the reason string both `undelivered.csv`
  files carry, so **the sampling pool depends on schedule CONTENT**, the same hazard T21 hit at (ak).
  `validate_household_schedule()` (from line 219) rejects a household when, for weekday or weekend, any hour
  leaves [0, 1], all 24 hours are zero, **total presence-hours leave [2, 24]**, more than 4 isolated one-hour
  spikes appear, or all 24 hours are exactly 1 without the retiree tag. **Pre-registered hypothesis, recorded
  before measurement:** the reversion arms move at-home time *down*, so the rule expected to fire is the lower
  end of the [2, 24] band; the employee must report the rule that actually fires even if it is a different one,
  and say plainly if the hypothesis was wrong. **The number that decides the shape of this finding** is how many
  households fail validation in each whole file, broken down by rule, for λ=0.0, S-Revert-std, λ=0.5 and the
  unmodified 2030 main file -- two households is a footnote, a systematic population reaches the manuscript.

---

**Entry (bv), dr_2J-13 is CLOSED and pre-registered rule 3 FIRES.** The author ran the end-use prompt; T46
vetted the return the full seven-step way (`deepResearch/dr_2J-13_VETTING.md`, verdict **PARTIALLY
SURVIVES**): every CEUD PJ value re-fetched live for the 2022 column and matching exactly, all 30
conversions recomputed clean, 12 of 15 citations VERIFIED, **nothing fabricated**. But no measured or
survey-based Canadian end-use split exists (sub-metering NOT FOUND, SHEU has no end-use split, IESO gives
no absolute intensities, peer-reviewed NOT FOUND); the only split on offer is CEUD's **modelled** stock
accounting, which the prompt's scope guard excluded in advance. **Manager ruling: rule 3 fires.** The
breakdown is not run, the manuscript states the measured split was unavailable and attributes the Table 5
gap to **no single end use**, and the return's "4 to 9 times, unequivocally located in space heating"
sentence **never appears in the paper**. Second, independent reason: CEUD's denominator is *heated* floor
space and its space heating is all-fuel raw combustion energy (gas-dominated in Ontario) against our
simulated site energy on our own area basis, so the multiple could be an artefact of the bases. Full
wording for the manuscript, plus two smaller rulings (the **saved file is the record, the chat-side summary
of that run is unusable**; three background citations carry a wrong detail), is **plan §5 item 24**.

**Entry (bu), Figure 1 is generated, verified and ACCEPTED; the scorer finished; T30 is back at `%2`.** T47
checked the author's generated image against the T35 spec and it matches on every checkable item: 24 box
labels diffed programmatically (0 mismatches), all 33 arrows read one by one out of the generator with only
arrow 32 dashed and its exact label, three band titles correct, 4488 x 3732 px at 600 dpi = **190.0 x 158.0
mm** exactly, must-not list clean. **Nothing failed, so no corrected image prompt was written.** Two process
findings were fixed rather than logged: the run had silently overwritten `figures/Figure_01_pipeline.png`
(proved by SHA-256, not by date), and it is now **restored** from the untouched original at
`writing/figures/Figure_01_pipeline.png`; and `scripts/generate_fig01_workflow.py` had a hardcoded fourth
save to that same filename on every invocation, which is **removed** (three writes left, all
`Figure_01_workflow.*`, `py_compile` passes, drawing code untouched). **New plan §5 item 23:** WP11 must cite
`Figure_01_workflow.png`, never `Figure_01_pipeline.png` (a different, retired figure), and the only
unverified item is print-size legibility at 100 percent zoom, which is the author's own eye at figure
lock-in. The T21 scorer `1329216` **COMPLETED** (00:50:25), so step 3 is live; T30 was restored to `%2`
(verified `ArrayTaskId=41-47%2`), putting the account at exactly **32 running CPUs**. **Method note:** summing
`squeue -h -o '%C'` gave 48 and looked like a breach of the 32-CPU promise, but that sum counts **PENDING**
tasks, which hold no cores; only 28 were running. Never act on that sum alone.

**What changed since (bv) — read this before anything else (bw).** **T45 is ACCEPTED on A1-A4 and A2X**
(7200/7200 runs delivered, 0/72 pairing mismatches against an independent engine re-draw, 0/24
cross-campaign mismatches, no fallback or invalid log line, all four staged schedule md5s unchanged), and
**the scorer's selftest was seen failing before it was trusted** (`FAIL:1_mismatch` on a deliberately
swapped household id, `PASS` on the clean copy, real check only after). A hand-recomputed household annual
electricity matched the scorer to six decimal places. **T45 returned "A6 STOP RULE TRIGGERED" and the
manager has RULED THAT IT DOES NOT FIRE** — plan §5 item 25 carries the full reasoning; do not re-open it.
In short: A6 is defined on the official script over the whole cell at n=50, and T45 could only run it on
**15 of 50 households in 4 of 24 cells**, locally, in a hand-rebuilt tree; the one cell it flagged
(`OtherDwelling__Montreal_6A`, -6 h) is the archetype whose `equip_bldg` meter is a seven-unit building with
six non-occupancy units (`step9_validate_full.py:47`, `OD_N_UNITS = 7`), so about one seventh of the metered
profile responds to the schedule and its argmax is unstable under subsampling; its two competing baseline
hours were **1.3 percent apart**; and the injection defect A6 exists to trap (T25 Q6 trap 1) is a shared
code path that would move every archetype together, while the other three measured 0 h, 0 h and -1 h on the
same pass. **The fact that settled it, which T45 did not know existed:** the published campaign's own
full-grid A6 output has been on scratch since 10 June at
`/speed-scratch/o_iseri/step9_run/loadshape/peak_shift_summary.csv` — n=50, 24 cells, both years, **all 48
rows inside +/-1 on `equip_bldg_shift`**, `OtherDwelling__Montreal_6A` at 0 h and -1 h. **The rule stays
ARMED, not closed:** A5 and A6 have never been run on the T21 rebuild at full grid by anyone, so **T48** was
written and handed to a fresh Sonnet (`impl/2026-09-17_T48_A5_A6_fullgrid.md`): one 4-CPU job,
`--dependency=afterany:1328310`, staging the rebuild into the official layout with **symlinks only**, running
both Step-9 scripts **unmodified** over the rebuild and over the published campaign, with a seen-working
control (reproduce the published `peak_shift_summary.csv` row for row) and a seen-failing control (rotate one
cell's activity hours by +3 h and confirm the detector reports +3 h; if it does not, **every A6 PASS in this
project is worthless** and A6 becomes NOT_TRUSTED). **Plan §5 item 26 is the bigger open question:**
`step9_validate_full.py` compares a building-level meter (divided only by household count, line 127) against
a per-dwelling SHEU target (lines 38-41) and corrects per unit for **OtherDwelling only**, fridge energy only
(line 146), with **nothing for MidRise or HighRise** — so a whole-building multi-unit model cannot pass that
gate by construction, yet the T21 doc records the published A5 as 48/48 all pass. Both cannot be true. T48
Step 5 runs the same script over the published tree to decide whether this is old (the "all pass" line is
wrong) or new (the rebuild changed the multi-unit basis). **Until T48 lands, no MidRise, HighRise or
OtherDwelling energy-intensity number goes into the manuscript.** SingleD is unaffected either way.

**New author instruction, 2026-09-17:** "if needed create new prompt, you are the one who designs the
prompts." The manager may author or replace a deep-research or image prompt on its own judgement, without
asking first. This does not touch the two hard rules it sits inside: the assistant still never generates an
image, and it still never searches literature itself.

**Entry (bt), both author-owed inputs are now answered.** Asked directly, the author chose: the end-use
split is **"you find it yourself"** = a prompt they run outside (deep research stays external, the
assistant still searches nothing), and Figure 1 is **"create image prompt and let me generate with Gemini
Antigravity"**. The Figure 1 prompt already existed from T35 and was **not rebuilt** — the author was handed
`figures/Prompts_Images/Figure_01_workflow_prompt.md`. **T43 ACCEPTED:** the CATI-to-EQ confound is the
eleventh limitation in `draft_S7_limitations.md` (opening count fixed to "eleven … first eight"; trace row 9
pins a new fact, **`COLLECT_MODE` is 0 for 2005/2010/2015 and 1 only for 2022**, so the confound comes from
our own data). **T44 ACCEPTED with two manager corrections** to
`deepResearch/dr_2J-13_sheu_enduse_split_gemini_prompt.md`: its positive control had been the same number
rule 3 depends on (replaced with total residential sector energy use, independent of the five end uses), and
an anti-anchoring rule was added so our own simulated range cannot steer the search. **New plan §5 item
22: CLOSED 2026-09-17 (log (ca)).** The eleventh limitation's one outside-literature sentence had no citable
reference, so the manager took **option (b)**: the sentence now claims only what `COLLECT_MODE` supports —
mode and behaviour are perfectly confounded, and a mode effect is neither supported nor excluded by our own
evidence. The limitations table row was softened the same way. **No citation is owed and Step 13 must not
reopen this.**

**Four items from T51 and T52, plan §5 items 29 to 32 (logs (cc) and (cd)).**

**29 — CLOSED 2026-09-18 (log (cf)). The manuscript rule is: claim the designed SHIFT, never the
absolute LEVEL.** The valid same-basis source was already scored in September and is in
`impl/2026-09-15_T26_wp2_scenario_builds.md`'s acceptance table. **SC1 (intended step) PASS on all
three arms** — achieved against design λ=1.0 1.4850 vs 1.5066 pp, λ=0.5 −0.8547 vs −0.8592, λ=0.0
−3.2081 vs −3.2250, so **diffs of 0.0045 to 0.0216 pp against a 0.5 pp band** — and it tests the
**change** from 2022 with both sides from the same stock table, which is why it compares like with
like and P2 does not. **SC5 (rake residual) PASS, 0 of 48 slots flagged, max 0.0002 pp weekday.**
**SC0 PASS** at 6,934,320/6,934,320 cells equal. A cross-check fell out of it: T52's independent
population figures (73.56961 / 71.21605 pp) reproduce T26's SC2 national figures (73.5702 / 71.2168) to
**0.0006 and 0.0008 pp** — two implementations written weeks apart. And the residual is now accounted
for: SC2's own level sits the same **+0.36 pp** above the target level, so with the change matching to
0.02 pp and the rake residual at 0.0002 pp, the gap must sit in the **2022 baseline the target is
defined on** — most likely the unit, since T26's target is a **per-person** mean and every achieved
figure is **per-household**. ⚠ **That last step is an inference, not a measurement**, and deliberately
not measured because the rule above is safe either way; if a reviewer asks about the level, the
measurement becomes owed. **The chain to the energy runs needs no P2:** SC1/SC5 score the file, T51's
**P4 PASS with empty `diffs`** proves the runs read that same unmodified file, T51's **P1
`cells_failing: 0`** proves the pairing. **Do not quote T26's "Validator 28/28" band text** — that
validator's own total is 31 and the mismatch is still unresolved.

**Superseded ruling, kept because the reasoning still governs P2 itself:** P2's pre-registered 0.5 pp
target-attainment band is breached on both 2030 scenario arms (+1.68 and +1.73 pp). **The band is not
moved, the FAIL is not overturned, and it is not converted into a PASS — it is NOT_INTERPRETABLE.** T52
showed the two sides were never comparable in **three** ways at once. T26's target
(`T26/T26_scripts/t20_d1.py:136-148`) is a **plain unweighted per-person mean over the whole rebuilt
stock**, per stratum, and its CSV has **no archetype dimension** at all (`t26_scenario.py:104-115`).
P2's injected side is a **per-household** mean, unweighted within archetype, then stock-weighted across
archetypes, over a **1,198-home sample**. Dropping only the sample restriction takes the gap to
**+0.362** and **+0.374 pp**, inside the band, so most of the breach was the sample — but two
definitional mismatches remain, so that figure is **not** a measurement of target attainment either.
**No target-attainment claim may be sourced from P2 in either direction.** If the paper says the
scenarios reach their designed shift, that rests on **T26's own build-time attainment check**, which
must be re-read and quoted first. That re-read is all item 29 is still open for.

**30 — cause found; the finding changed shape.** The λ=0.0 arm delivered **1198 of 1200**. Both
households were dropped at **scenario-pool construction, before the manifest was consulted**, and **the
campaign wrote the reason down itself** in `out/lambda_0.0/<cell>/undelivered.csv` (`not in scenario
pool ... integration.py:432-438`); both are present and delivered in λ=0.5 with full 8,760-row files.
So this was never a silent loss — it was a **documented loss nobody read**. **The ruling: the two
scenario arms do not share a household set**, so any cross-scenario comparison must be recomputed on the
**1,198 households common to both arms**, or the two-household difference must be shown by measurement
to be negligible. **T51's P3 deltas were computed on 1,200 and 1,198 and are not on a common basis — do
not quote them as they stand.** Same family as item 27, caught before it reached a number.

**31 — CORRECTED by T53 (log (ce)): the claim "no collector reads these files" was mine and it was
wrong.** `t29_check.py` reads them (`read_undelivered_samples()` line 150, P1 at line 181, and line 191
`continue  # explained by undelivered.csv -- not a pairing bug`). **What it does not do is carry the
reason strings into its report**, so the explanation of the λ=0.0 shortfall sat inside the gate's own
input and never reached its output. The fix is additive and changes no criterion: **print the reasons
the collector already reads.** What still binds: **T17, T21, T22, T28, T30 and the published `step9_run`
write no such file at any of their 226 cell directories**, so for them the absence of undelivered rows
is **uninformative, not reassuring** — their completeness rests only on counting delivered output
against a manifest, and a future shortfall there will arrive with no reason beside it. Record it; do not
retrofit it.

**33 — NEW and the real find: the drop is systematic.** T32's one undelivered row is **the same
household** as T29's — `OtherDwelling__Vancouver_5C`, `sample 9`, `sim_hh_id 129937`, reason string
identical to the character — in a campaign built and launched separately. Both affected arms are
**reversion-style** builds (T29 λ=0.0, T32 S-Revert-std); T29's λ=0.5 arm delivers the same household
with a full 8,760-row file. **So the reversion-side schedule construction excludes these households
reproducibly — a WP2 question, not a run-time accident.** T32 is still running, so **its collector must
read `undelivered.csv`**, it inherits item 30's common-household rule, and the exclusion must be
explained before any reversion-scenario number is described as covering the sampled households.

**32 — NEW, small: 43 households carry a `DTYPE` of the literal value `8`.** `STOCK_WEIGHTS` has four
keys and the sum skips anything not in `ARCH_NAMES`, so those 43 are **silently excluded from every
stock-weighted figure** on both bases. 43 of 144,465 changes no number; a bare integer in a
dwelling-type column is still unexplained. **Settle it before the supplement describes the dwelling-type
classification, and do not "fix" it by dropping the rows.**

**The `J3` label question is also CLOSED (log (cb)) — and entry (ca) stated the rule wrongly.** (ca) said
the governing rule was "this label never appears in prose". It is not. The plan's §7 WP10 spec says
"**Move to SI** (R2-1): J3 architecture detail …" and "**Plain terms** (R2-1): **replace or gloss** every
self-defined label … Keep one short glossary table in SI." The review therefore asked for that detail to be
**put** in the supplementary information, and the label requirement is replace-**or**-gloss. So `J3` **stays**
in `writing/submission/tables/SI/Table_B1_B2.md`, and a plain-term gloss has been added under its
shipped-model line. Do not delete the label. **New plan §5 item 28:** the single SI glossary table the review
asked for **has never been written** (a search of the tables tree and the revision manuscript folder for
"glossar" returns nothing); the B1 gloss covers `J3` alone and is **not** that deliverable. WP10 owes it.

**Entry (bs), the writing track started in parallel with the cluster.** T42 threaded plan §5 items 16-21
into `manuscript/prep/response_map.md` (**49 → 55 rows**, all six new rows WAITING/OPEN — correct, no target
draft exists yet). **`Qn` is NOT plan item `n`:** T39 used Q10-Q16, so item 16 → Q17 … item 21 → Q22; every
row cites its own plan item. **Q18 holds a manager decision left deliberately open**, with the reasoning in
(br)/(bs) so it is not redone: the "+2.2 to +3.9 pp" figure is defined two incompatible ways (a level above
the pre-pandemic baseline, four places; the 2022-to-2030 step, once), it is percentage points of at-home
share so it needs no energy run, the historic-cycle schedules could support either reading, and the call is
due when **WP1** recalculates. T43 is dispatched: the CATI-to-EQ survey-mode confound as the eleventh
limitation in `draft_S7_limitations.md`. **Restore T30 to `%2` once `1329216` finishes** (see the CPU rule
below).

**What changed this entry (br) — a big overnight step forward.** Four job families cleared. **T21 is fully
run**: Step 8 24/24, Step 9 activity 24/24, Step 9 baseline 24/24, A4 md5-after done, all exit 0:0 — 2,400
main plus 4,800 comparison runs delivered. Its scorer `1328428` FAILED, but only because `t21_check.sh:41`
called the selftest without the `--out` that `t21_check.py:346` marks required; a Sonnet fixed that one line
(the .py was NOT touched), and it is rerunning as **`1329216`**. **T32 is ACCEPTED**: G0 PASS (guard equals
T26's λ = 0 file exactly, checksum plus 100.0 % cell match), SC1/SC4/SC5 all PASS, and its **1,200
S-Revert-std runs are submitted as `1329220`**. **T29's smoke PASSED retrospectively** — two households,
8,760 data rows each, IDs **130228 / 79252** (T21's rebuilt draw, not the published 130322/80058) — and
`1328433` (`t29_partial`) is 24/24 done. Manager ruling: the old "scancel on smoke failure" instruction is
**superseded**; a retrospective collector reports and the manager rules.

**🔴 NEW STANDING CONSTRAINT — the CPU ceiling did NOT change for us.** HPC support raised the association
from `cpu=32` to `cpu=64` (temporary, reviewed end of October 2026). **The author reserved the new 32 for a
different project: "do not interfere new 32 cpu".** So **2J never exceeds 32 CPUs in flight**, and you may
NOT raise any array's `%N` or `--cpus-per-task` because the limit is higher. The live arrays already sum to
exactly 32 (T22 2x4, T28 1x8, T29-revert 2x4, T30 2x4); that is why the T32 campaign went in as
`--dependency=afterany:1328434` at `%2` and 4 CPUs — it inherits T29-revert's eight CPUs rather than adding
to the total. If you must exceed 32 briefly, record it in the log as an exception, as (br) does for the
scorer rerun.

Earlier history is in the plan Progress Log, which is the state — read entries (bf) onward there rather than
here. Prompt-file entries (bo), (bp) and (bq) were status refreshes with no plan-log entry; (bq)'s one
substantive result, the independent re-verification of all 52 references in the frozen submitted manuscript
(50 clean, 2 real small errors, 0 fabricated, 0 not-found), lives as plan §5 items **20** (Motuzienė et al.
2022 volume 76 → 77) and **21** (Jalilian & Kamel 2025 truncated title). Neither is applied to the frozen
archive file — never edit submitted files — both are applied when WP10 assembles the new reference list at
Step 13.

Model: Opus (manager). Employees and collectors: Sonnet, named explicitly on every Agent call.

---

## 0. Who you are and the standing instructions

You are the **manager** of the 2J rejection revision. The paper was rejected by Building Simulation on
2026-09-15. Target venue is **Applied Energy** (author decision; fallback Sustainable Cities and Society).

Author instructions that still bind, verbatim where quoted:
- "continue until the end, do not stop the progress anymore for questions". You take design decisions
  yourself and record them in the plan's Progress Log and the task doc. Ask the author only for inputs
  only they hold (the SHEU end-use split; running deep-research prompts; generating Figure 1).
- Use cheaper agents (Sonnet), model named explicitly. **One fresh agent per task, never resume a
  finished one.** Employees submit, write the JobID to the task doc, end the turn. They never wait.
- Use the Speed cluster at full speed, **but only up to 32 CPUs** — see the standing constraint above;
  the account limit is 64 and the other 32 belong to a different project. `sbatch` only.
- Option (a) is decided: 2022 is rebuilt from 2022-cycle diaries only; 2030 is built by D1 on the rebuilt
  stock. Do not re-open it.
- **Update this prompt (§2 and §3, plus the "Last updated" line) after every task completion**, in the same
  turn as the Progress Log entry and the checklist republish.
- "udpate artifact everytime" (2026-09-15): republish the checklist page after EVERY step, not only task closures.
- "i am struggling to montior, what is left to do": the checklist page must always answer that question
  without the author asking. One progress bar per cluster job, refreshed from `sacct` on every wake.

**AUTHOR RULINGS (plan log (ay)), binding on every later task:**
- **(a) Weekend ceiling.** The pre-registered diary-distance ceiling is 0.10 for every day type. The weekend
  does not meet it and the manuscript says so plainly. The later widening to 0.20 is disclosed once, in the
  SI, and used nowhere. The evidence carried is the observed-only weekend rows (0.036 Sat / 0.040 Sun) versus
  synthetic-only 0.138 to 0.175, plus the saturated weekend up-weighting (~0.005 movement over two attempts).
  The synthesized weekend days are a stated limitation of the diary completion step.
- **(b) Old numbers.** Every OLD-CAMPAIGN / OLD-BUILD number is re-derived on the rebuilt runs (T20, T21, T28,
  T30) before it may appear anywhere. Any number the rebuilt runs do not produce is **dropped**, never quoted
  from the old campaign. Old and rebuilt numbers never share a table.

Hard rules (read `GSSCanada-main/CLAUDE.md` first; it overrides everything):
- Chat reply shape: one plain headline sentence, 3–5 plain bullets, `Evidence:` line, `Next:` 3–4 words,
  ~80 words, English, no tables, no IDs or jargon in sentences.
- **Speed login node (`speed-submit2`): never python, never blocking `srun`, never `find/du/md5sum/cp/mkdir`.**
  Allowed: `sbatch squeue sacct scancel scontrol cd ls scp module load` + single-file `tail head grep wc -l cat`.
  Every job `-p ps -t 7-00:00:00`. Shell is tcsh: no `2>&1`, no `2>/dev/null`. ssh
  `-o BatchMode=yes -o ConnectTimeout=60 o_iseri@speed.encs.concordia.ca`. Python on nodes:
  `/speed-scratch/o_iseri/envs/step4/bin/python`, `ENERGYPLUS_DIR=/speed-scratch/o_iseri/ep_wrappers`.
  Staging: `/speed-scratch/o_iseri/2J_revision/Tnn/`. Create remote dirs by `scp -r` of a local folder with
  `.keep` files (SLURM `--output` dirs must exist at submit time).
- The rejection letter is confidential: no quotes, no manuscript ID on any public page.
- Deep research is external: write prompts, never search literature or check DOIs yourself.
- Never create images (data plots from frozen data excepted).
- Manuscript prose says "limitation", never "failure". Never relax a band to pass.
- Every check must be seen failing once on a fake case before its PASS is trusted.
- Local edit rule: **never use bash heredocs for file edits** (they mangle LaTeX backslashes and tabs). Write a
  `.py` script into the scratchpad with the Write tool, every replacement guarded by
  `assert s.count(a) == 1`, then run `py -3 <file>`. Quote every path containing "rejection revision".
  **Never open the target file in `"w"` mode until the new text is fully built and encodable** — that mode
  truncates on open, so an exception mid-write leaves a 0-byte file. This prompt file was destroyed exactly
  that way on 2026-09-17 (a `\uXXXX` surrogate escape in the payload) and had to be rebuilt from context.
  Build the text, write it to a temp path, check it is non-empty, then replace the target.

Engine facts (verified, do not re-derive): cell label `f"{archetype}__{city}"`; archetypes SingleD,
OtherDwelling, MidRise, HighRise; cities Toronto_5A, Kelowna_5B, Vancouver_5C, Montreal_6A, Calgary_6B,
Winnipeg_7A; array task id = arch_idx*6 + city_idx. `run_paired_mc.py` has no `--code-root`: run the copy in the
shared tree `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (T22's tree never had the driver; log (ag)).
`--sched-dir` expects plain `BEM_Schedules_{y}.csv`. **The sampling pool = households passing
`validate_household_schedule` on the loaded file(s), so it depends on schedule CONTENT**: any run meant to reuse
T21's households must use T21's paired pool or T21's manifest, never a fresh draw on another file (log (ak), (am)).
The reusable mechanism for that is T29's **`run_fixed_manifest.py`** wrapper pointed at
`T21/out/step8/<cell>/cell_manifest.csv` — T32's campaign reuses it byte-identically (log (br)).
Stock weights are archetype-only, split equally over cities. CI = pooled paired Student-t
(`08_simulation_val.py:951-1027`). Metrics in `08_simulation_plots.py` (annual kWh :340,361; daily peak :377;
circular peak hour :278-285; load factor :385; midday share [9,17) :387; circular SD :290; morning-leaning
share :914-915).

## 1. Read these first, in order

1. `2J_docs_occ_nTemp/writing/submission/rejection revision/00_REVISION_PLAN.md` — §2 reviewer triage,
   §3 work packages, §9 closure boxes, §10 waves, and **the Progress Log from entry (aa) to the end**.
   The log is the state.
2. The task docs of everything in flight (§2 below), Ledger and Manager addenda first.
3. `deepResearch/00_README_deepResearch.md` (vetting list, venue decision rule).
4. Memory: `project_2j_paper_writing.md` (update it at the end of your session).

All `impl/` and `deepResearch/` paths are under `2J_docs_occ_nTemp/writing/submission/rejection revision/`.

Progress checklist page for the author: https://claude.ai/artifact/4emZkRdASTDUtvXSRtWPVe (**at Version 52**;
source HTML `C:\Users\o_iseri\AppData\Local\Temp\claude\C--Users-o-iseri-Desktop-GSSCanada\ff544f7a-a3e9-432c-9d39-3b03a15f09a2\scratchpad\2j_resubmission_tracker.html`;
if it is gone, `Artifact action:read` the URL and rebuild the file from it). **Always read the live page and
diff before republishing — a dead session's local copy went stale once and the live page is master; extract the
scripts to `scratchpad/t.js` and `node --check` it; never pass `favicon`; pass `url` to update in place.** The
top panel "Right now" holds one progress bar per cluster job (cells done of total, from `sacct`); refresh its
counts on every waiter wake (author asked for it, Version 15).

## 2. State (2026-09-17 morning, plan log entry (br))

**Superseded by §0 above for anything cluster-related (job states, T22/T48/T49/T32) — §0 is the 2026-09-20
read and this section's job table below is stale by three days. §2.1/§2.1b (closed, non-cluster
deliverables) still hold.**

### 2.1 Done and trusted
- T01–T19, T23–T25, T27 (see log). T17: Speed reproduces the local campaign. T18: control arm reproduces the
  published 2022 files exactly. T23: the schedule fallback path gives identical values; no correction.
- **T18c / choice rule (entry (aa))**: the frozen 2022 stock is **Nb-f**, all 144,465 households, 6,934,320 rows.
  Validator check 3.5 fails on Nb-f (75.04 % vs 72.3 %, band not moved): a stated limitation.
- **T20 CLOSED** (log (ah)): N0–N3 all PASS; household-ID sets of 2030 main and null equal Nb-f 2022 (job 1328408).
- **Shared Step-8 code tree** `/speed-scratch/o_iseri/2J_revision/code_step8/repo` (log (ag)).
- **T21 sample question CLOSED (log (ak)).** Staged files byte-equal to T18c/T20 outputs. The rebuilt schedules
  change which households the engine's sanity check drops, so the paired pool (16,326 for SingleD Montreal)
  differs from the published one (16,208) by 320 households and seed 42 draws a different sample (130228/79252
  vs published 130322/80058, which the engine reproduces on the published files). **Basis change: A2 = equality
  with an independent engine re-draw on the staged files (seen failing first) + info-only overlap with the
  published manifests.** The paper must say the before/after comparison is not household-paired across stocks.
  T21 smoke PASS. T30's and T31's smokes ran on the PUBLISHED schedules: their mechanics results stand, their
  household numbers are not Nb-f numbers.
- **T30 V1 decided (log (ak)):** phase B samples once per cell from the paired pool; V1 = equal to T21's manifest,
  mismatch = stop.
- T31 phase A CLOSED (E0 exact, E1 heating +205–208 %, E2 2.50 ACH50).
- **T26 ACCEPTED** (log (am)): SC0–SC5 pass; SC4 read as 0 FAIL of 31 checks. Standardized-jump trigger fired → T32.
- **T31 CLOSED, NOT RUN (log (aq)):** dr_2J-09b returned; rules 1 to 8 applied. Wall, ceiling and air-tightness
  found, but no source prints a U-value or SHGC for the dominant glazing type, so window is NOT FOUND and rule 8
  fires: WP7.3 is not run, no JSON, no partial variant. The paper states the one-envelope limitation.
- **WP10 prep DONE:** T33 (log (at)) `manuscript/prep/` response_map (42 rows), jargon_inventory, si_move_list.
  T34 (log (au)) `manuscript/draft_S2_framework.md`, 9 corrections. T35 (log (aw)) Figure 1 prompt, corrected:
  raking runs AFTER matching in the code, so WP10 orders matching (2.4) before raking (2.3). T36 (log (ax), (ay))
  `manuscript/draft_SI_model_selection.md`, accepted with 3 manager corrections and both author rulings applied.
- **T29 smoke verified, PASS 3/3 (log (br)):** two households simulated, 8,760 data rows each (8,761 lines with
  header), IDs 130228 and 79252 — T21's rebuilt draw, not the published pair. The sampling-pool hazard is
  closed for T29 by measurement, not assumption.
- **T32 ACCEPTED (log (br)):** G0 PASS (guard equals T26's λ = 0 file exactly, checksum plus 100.0 % cell match),
  SC1 PASS (within 0.012 pp), SC4 PASS (0 FAIL, reproducing T26's accepted 30/1/0 reading), SC5 PASS (max diff
  0.0012 pp). Its 1,200-run S-Revert-std campaign is submitted as `1329220`.

### 2.1b Both done, collected 2026-09-15 (logs (bb) and (bc)). Nothing to do here.
- **T37 — DONE, collected and accepted 2026-09-15, log (bb).** `manuscript/draft_S7_limitations.md` is written
  and reviewed: **ten** limitations, four trace rows re-checked at source by the manager, both rulings hold. Two
  manager corrections applied: the opening count was wrong twice (it said six, the section listed nine), and the
  tenth limitation (Saturday and Sunday pooled into one weekend pattern) was added at the T38 collection with its
  own trace row. Use it as the S7 base in step 13. Do not re-run this task.
- **T38 — DONE, collected and accepted 2026-09-15, log (bc).** `manuscript/draft_SI_schedule_completion.md`
  is written and reviewed: S.5 to S.9 plus a 17-row trace table. Four manager corrections applied, three of them
  ruling (b) repairs (the 2022 at-home rates by day type, the 2030 Saturday and Sunday rates, and the 77,313
  weekday-only count were all measured on superseded builds and are now marked PENDING). Do not re-run this task.
**Three PENDING placeholders are now live in the manuscript folder** and must be filled or cut at step 13:
the 2022 at-home rate by day-type stratum, the 2030 Saturday and Sunday rates, and the 24-cell drop-count audit
behind the sampling-pool caveat. The first two come free with any rebuilt schedule file; the third is optional
and only if the reviewer response needs more than the one audited cell.

### 2.2 Cluster snapshot, `squeue` read 2026-09-17 late evening (manager's own read, after T49 submit)
**Across every 2J job ever submitted in this revision, the only non-zero exit is `1328428` (the T21 scorer,
a job-script bug, already fixed, rerun and COMPLETED as `1329216`). Nothing else has failed; nothing needs
resubmitting.** Refresh these counts with `sacct` on every waiter wake before quoting them. **Running CPUs
at this read: exactly 32** (T28 1x8, T22 2x4, T29-revert 2x4, T30 2x4) — at the promised ceiling, not over.
**Why T48 is still legal at that ceiling:** it is gated on `afterany:1328310`, the T22 array that is at
22/24 with nothing pending, so when it ends it frees 8 CPUs permanently; every other array is already at
its own throttle and cannot expand, and `1329220` is gated on `1328434`, not on `1328310`. In every
ordering the project stays at or below 32. **Do not remove that dependency and do not raise any `%N` or
`--cpus-per-task` because the association limit went to 64.**
**Count RUNNING rows only:** summing `squeue -h -o '%C'` includes PENDING array tasks, which hold no cores,
and reported 48 against a true 28 earlier today. Never act on that sum.

| Job | What | State 2026-09-17 morning |
|---|---|---|
| 1328422 | T21 Step 8 paired runs, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328425 | T21 Step 9 activity, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328426 | T21 Step 9 baseline, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328427 | T21 A4 md5-after | **DONE**, exit 0:0 |
| 1328428 | T21 `t21_check.py` selftest + A2/A2-info | **FAILED 1:0** — argparse, superseded by 1329216 |
| 1329216 | T21 scorer, resubmitted with the `--out` fix | **COMPLETED**, exit 0:0, 00:50:25 — **SCORED AND ACCEPTED** by T45 (A1-A4, A2X PASS) |
| 1328429 | T32 S-Revert-std build (task 0 guard, task 1 std) | **DONE 2/2**, exit 0:0, **SCORED PASS** |
| 1328430 | T32 compare | **DONE**, exit 0:0, **SCORED PASS** |
| 1328431 | T29 staging | **DONE**, exit 0:0 |
| 1328432 | T29 smoke (2 households) | **DONE**, exit 0:0, **verified PASS 3/3** |
| 1328433 | T29 S-Partial, 24 tasks | **DONE 24/24**, exit 0:0 |
| 1328434 | T29 S-Revert, 24 tasks | **DONE 24/24**, exit `0:0` — finished 2026-09-17; with `1328433` this closes both scenario arms, and **T51 is now scoring them** |
| 1328310 | T22 static-schedule arm, 24 tasks `%2` | **23/24 done**, 1 running (`_15`, **1 d 22 h in** at the 2026-09-18 read), 0 pending — the last one, and now the ONLY thing holding the queue; `1329258` and `1329278` both release when it ends |
| 1328419 | T30 average-profile array, 48 tasks `%2` | **DONE 48/48**, exit `0:0`, last End 2026-09-18T02:21:40 — **T55 is scoring it** |
| 1328415 | T28 200-home sample-size array, 4 tasks `%1` | **DONE 4/4**, exit `0:0`, last End 2026-09-18T03:30:09 — **T54 is scoring it** |
| 1329220 | T32 S-Revert-std campaign, 24 tasks `%2`, 1,200 runs | **20/24 done** (read 2026-09-18), 2 running, 2 pending, nothing failed — its collector is Step 2's remaining half and **must read `undelivered.csv`** (plan §5 item 33) |
| 1329278 | T49 collector, scores the WP3 static arm (job 1328310) on four gates, 1 CPU | **PENDING, reason `Dependency`** on `afterany:1328310` — report `/speed-scratch/o_iseri/2J_revision/T49/logs/t49_check_report.txt`, task doc `impl/2026-09-17_T49_T22_collector.md`; its `t49_check.py` was patched in place by T50 while it waited (log (bz)) and now carries GATE_B3b and B4_PARSE_ECHO |
| 1329258 | T48 full-grid A5/A6, published tree **and** T21 rebuild, 4 CPUs | **PENDING, reason `Dependency`** on `afterany:1328310` — log `/speed-scratch/o_iseri/2J_revision/T48/logs/t48_a5a6_1329258.out`, script `T48/t48_a5a6.sh`, interpreter `/speed-scratch/o_iseri/envs/step4/bin/python` |
| T51 | Collector for **both** T29 scenario arms (`1328433` + `1328434`), P0-P5 plus a new P5b, **1 CPU** | **DONE and ACCEPTED (log (cc)).** Job `1329407` COMPLETED; all five controls seen firing first, so P0/P1/P2/P4/P5/P5b are trusted. P4 and P5 clean, P1 pairing clean on both arms, P3 reported. **Two real findings, now plan §5 items 29 and 30:** P2's 0.5 pp band is breached on both arms (+1.68 and +1.73 pp) and **λ=0.0 delivered only 1198 of 1200 runs** although the array reported 24/24 COMPLETED. **T52 is diagnosing both; quote no 2030 scenario at-home-share number and no zero-work-from-home energy number until it lands.** Historical detail for the record: job `1329407` was submitted and ran — no dependency needed, both arrays were already COMPLETE. Manager overrode the task doc's `-c 4` to **`-c 1`** to hold the 32-CPU ceiling; do not raise it. **Read the report text, not `sacct`:** the employee made the wrapping job exit 0 whatever the four inner steps return, on the ground that a control run is *supposed* to exit 1, so `sacct` State is not a verdict here — the four inner exit codes are written by name into `/speed-scratch/o_iseri/2J_revision/T51/logs/t51_t29_report.txt`. Two more employee decisions to carry: the expected log set is **49**, not 50 (the 50th is a leftover Phase-A smoke-test log, excluded by filename pattern, and the employee confirmed the naming from the scripts' own `--output` lines), and **P5b's findings were folded into the existing exit-code accumulator** so a broken log cannot pass silently. All five controls live in **one** shadow tree fired by **one** invocation (`T51/logs/t51_controls_check.json`) — so when adjudicating, confirm each of the five fired *in that one file* before quoting anything from its gate. Original script preserved as `T29/T29_scripts/t29_check_v1.py` |
| T52 | **Diagnosis** of T51's two findings — not a gate, not a fix, **1 CPU** | **DONE and ACCEPTED (log (cd)).** Job `1329419` COMPLETED, 36 s. Both controls fired: all four of T51's P2 numbers reproduced to ≤1e-6, and a +0.10 shift on a **copy** moved the figure by exactly the predicted +10.0 pp / +1.28 pp. **Verdict (A):** dropping only the sampled-ID restriction takes the gap from +1.68 to **+0.362 pp** and +1.73 to **+0.374 pp**, both inside the band. But the two sides were incomparable in **three** ways, not one (see items 29/31/32 below), so **P2's FAIL is NOT_INTERPRETABLE** and no target-attainment claim may be sourced from it either way. The two missing λ=0.0 households were dropped at **scenario-pool construction** and the campaign **recorded it itself** in `out/lambda_0.0/<cell>/undelivered.csv`; both are present and delivered in λ=0.5. Historical detail: originally dispatched Five questions in order, gated on a control that must reproduce T51's four P2 numbers to six decimals first. **Q2 is the one that matters:** recompute P2's own formula with the sampled-ID restriction dropped, and name **(A)** the schedules hit their target and the gate compared a sample to a population, or **(B)** the schedules miss it by ~1.7 pp. **The employee names A or B and stops — what follows is a manager ruling.** It also reports what is actually absent for the two missing λ=0.0 households and quotes their task logs. Report `/speed-scratch/o_iseri/2J_revision/T52/logs/t52_diagnosis.txt` |
| T53 | **Audit** of every campaign's own `undelivered.csv`, **1 CPU** | **DONE and ACCEPTED (log (ce)).** Job `1329422` COMPLETED, 11 s, all three controls pass. **Only two trees write one and both have rows:** T29 (49 cells, 2 with rows) and **T32 (10 built, 1 with a row)**. T17, T21, T22, T28, T30 and the published `step9_run` write none at 226 cell directories — so their silence is **uninformative, not reassuring**. ⚠ **It also corrected me:** `t29_check.py` **does** read these files (`read_undelivered_samples()` line 150, used by P1 at 181, `continue  # explained by undelivered.csv` at 191) — it just never carries the reason strings into its report, which is the whole defect and the fix is additive. `t21_array.sh:47-50` says T21 records undelivered runs via per-task exit code and stdout log, so no artefact is missing there either. **New plan §5 item 33:** T32's undelivered row is **the same household** as T29's (`OtherDwelling__Vancouver_5C`, sample 9, `129937`, reason identical to the character), in a separately built campaign — both are reversion-style arms while λ=0.5 delivers it fine, so **the reversion-side schedule construction excludes it reproducibly**. Historical detail: dispatched 2026-09-17 night, JobID in `impl/2026-09-18_T53_undelivered_sweep.md`. Sweeps T17, T21, T22, T26, T28, T29, T30, T32 and the published `step9_run` tree. **It keeps "file absent", "file with zero rows" and "file with rows" as three distinct outcomes** — the P5b lesson applied again — and also answers whether **any** checker in this project reads the string `undelivered` at all. Seen-working control: it must find the two rows T52 already found. Fixes nothing; scope only. Report `/speed-scratch/o_iseri/2J_revision/T53/logs/t53_undelivered_sweep.txt` |
| T54 | **Collector for T28** (`1328415`, 200-home sample-size arm), B0-B5, **4 CPUs** | **SUBMITTED 2026-09-18 as job `1329670`.** Its employee preserved `t28_check.py` unmodified as `t28_check_v1.py` first, then patched it additively in exactly the two allowed ways: it now reads any `undelivered.csv` in a T28 cell dir and prints the **reason strings** (keeping "no file" and "file with zero rows" distinct), and it prints the raw `Pool=` line it actually read, not only the booleans derived from it. No threshold, band or PASS criterion changed — **re-confirm that against the report**. Originally dispatched:, fresh Sonnet, task doc `impl/2026-09-18_T54_T28_collector.md`. JobID goes in that doc's Ledger. `t28_check.py` already exists and is staged (21,851 B) — additive patches only, original preserved as `t28_check_v1.py`. **Four controls must fire in one file:** B1 on a swapped household id, B2 on a perturbed meter file, a seen-working control, and a hand-arithmetic check of the Student-t CI and subsample mean. Then: live `Pool=` >= 1,045 per cell, first-50 prefix equal to T21's manifest in order, annual kWh within 0.01 % for the 50 shared households, B3/B4 reported not banded, B5 zero fallback lines. **`NO_REF` on any cell is a STOP.** Report `T54/logs/t54_t28_report.txt`. **ADJUDICATED 2026-09-18 (plan log (co)): all four controls fired correctly; B0/B1/B2/B5 ACCEPTED; B3 REJECTED as mis-specified** (see Step 4) |
| T58 | **Diagnosis** of the 43 households whose `DTYPE` is the bare value `8` (plan §5 item 32), **1 CPU** | **DISPATCHED 2026-09-18**, fresh Sonnet, task doc `impl/2026-09-18_T58_dtype8_households.md`. Diagnosis and documentation only — **no row is dropped, recoded or repaired**, no pipeline code edited, and the wording it drafts is NOT written into any manuscript file. 43 of 144,465 changes no number; the reason to spend a job on it is that the supplement is about to describe the dwelling-type classification. **The question that carries it is what `8` means in the SOURCE codebook, quoted with the file named** — found in `codebooks/` and `references_*`, never inferred from pipeline behaviour, and a clean **NOT FOUND** is stated in advance to be a real answer. Also: the mapping code as `file:line` and what it does with an unrecognised value; and whether any of the 43 ever reached a run (T21 manifests are the reference). Report `T58/logs/t58_dtype8.txt` |
| T56 | **SI glossary table** (plan §5 item 28), **no cluster** | **ACCEPTED 2026-09-18** (plan log (cj)). `writing/submission/tables/SI/Table_SI_glossary.md` exists: **12 rows**, inside the 8-14 target, plus seven terms listed as deliberately left out **inside the deliverable file**. All three pre-dispatch acceptance conditions met. The manager re-derived the table's one substantive claim (`FailSafe` never triggered) against `Table_C1_C2.md:22` and `Appendix_D_deviations.md:83,85` -- the claim holds, but **the unit was wrong in two rows** ("household" where the source says **Census agent**, a person; 286,537 agents live in 144,507 households) and both were **corrected in place by the manager**. Row count must not grow |
| T57 | **Diagnosis** of the reversion-side pool exclusion (plan §5 item 33), **1 CPU** | **DISPATCHED 2026-09-18**, fresh Sonnet, task doc `impl/2026-09-18_T57_reversion_pool_exclusion.md`. Diagnosis only -- names the cause and stops; no fix, no re-run, read-only on every input. Measures: the two `undelivered.csv` reason strings at source; the 24 weekday and 24 weekend values of `sim_hh_id 129937` in the λ=0.0, S-Revert-std and λ=0.5 files with presence-hour totals; **which of the five `validate_household_schedule` rules fires, in which file, for which day type**; the per-file count of validation failures **broken down by rule** for all four files; and whether the excluded households share any metadata. Controls: one household passing in all three arms, and a copy driven below 2.0 presence-hours making the `[2, 24]` rule fire. Report `T57/logs/t57_pool_exclusion.txt`. **SUBMITTED 2026-09-18 as job `1329673`, UNREAD.** The employee also hand-derived the answer by single-file `grep` before the job ran (legitimate -- 48 rows per household, read by eye) and the **pre-registered hypothesis is confirmed**: weekday presence-hours are **1.5 h** (λ=0.0), **1.0 h** (S-Revert-std) and **exactly 2.0 h** (λ=0.5, inclusive band, passes); `48609` is **0.5 h**. That is a **prediction until the job's controls are read**. **ACCEPTED 2026-09-18 (plan log (cn)): both controls right, hypothesis CONFIRMED by the real function, `real-vs-diag mismatches = 0` in all four files.** Item 33 ruled a **bounded footnote** |
| T55 | **Collector for T30** (`1328419`, average-profile arm), V0-V5 + two spread metrics, **1 CPU** | **ADJUDICATED 2026-09-18 (plan log (cr)). `sacct` shows job `1329668` as `FAILED 1:0` and that is NOT a gate failure** — the wrapper exits with the inner script's own code, which means "a section raised", not "a gate failed"; the report says so in its own words. **V0, V1, V2, V4, V5 and the hand-check all PASS, and all three controls are correctly labelled** (two seen-failing FIRED, seen-working DID NOT FIRE — unlike T59's). **V1 passed, so no cell was stopped.** **V3 DID NOT RUN; see the T61 row.** Superseded detail follows for the record:, fresh Sonnet, task doc `impl/2026-09-18_T55_T30_collector.md`. JobID goes in that doc's Ledger. `t30_check.py` is staged (18,243 B) but **has never run on real full-grid output** — V1 and V2 must be **seen failing** on a copied fake case first. **V1 is a STOP per cell, not a reported difference.** Six smoke leftovers in `T30/out/` must be excluded by a stated rule with the count printed. One cell hand-checked end to end. Report `T55/logs/t55_t30_report.txt` |
| T61 | **Re-run of T55's V3 alone**, with the IDD environment the T30 runs themselves used, **1 CPU** | **DISPATCHED 2026-09-18**, fresh Sonnet, task doc `impl/2026-09-18_T61_V3_rerun_idd.md`. V3 crashed in T55 at `IDF.setiddname(resolve_idd_path())` because `t55_score.sh` never exported `IDD_FILE` / `ENERGYPLUS_DIR`, so `config.py` fell back to a `/usr/local` path absent from the compute nodes; `t30_array.sh:61-62` carries the right one and the manager verified the file itself (`/speed-scratch/o_iseri/ep_wrappers/Energy+.idd`, 4,448,311 B, first line `!IDD_Version 24.2.0`). **Forbidden from re-running the six adjudicated gates or touching `T30/out/`.** Four controls required, the fourth being the item-38 fix: point `IDD_FILE` at nothing and show the summary print **NOT_EVALUABLE, not FAIL**. Report `T61/logs/t61_v3_report.txt` |
| T62 | **Two unblocked non-cluster questions**, read-only, **no job** | **ACCEPTED 2026-09-18 (plan log (cs)); it found that the clustering check is misnamed and measures the wrong thing — see Step 9.** Originally dispatched 2026-09-18, fresh Sonnet, task doc `impl/2026-09-18_T62_wp6_clustering_and_calendar_path.md`. Dispatched because the author asked whether any parallel work was running and the honest answer was **no** — everything was queued behind the cluster for no reason. **Q1 (Step 9 / WP6):** quote the clustering check that `draft_S2_framework.md` promises in its paired-interval section, establish whether that check exists anywhere in the project, what delivering it would take on frozen data, and whether any drafted number depends on it — so the manager can rule **deliver it or cut the sentence**, which is the plan's standing either/or. **Q2 (Step 13 / WP10):** trace which calendar-expansion path the campaign actually called, `create_compact_schedule` or `write_8760_schedule_csv`, from the entry point rather than by likelihood; no claim turns on it but the SI must not be vague. **The agent decides nothing and edits nothing** except appending Findings to its own brief; ambiguity must be reported as `NOT ESTABLISHED` rather than resolved by guess, because a guess here would reach a published supplement |

**Waiter.** A 30-minute waiter was running in the (br) session on `1328310`, `1328415`, `1328419` and
`1328434`. **It dies with that session: start a fresh one as your first act**, on whichever IDs are still
queued plus `1329216` and `1329220`. Run the poll loop directly with `run_in_background:true` — **no inner
`nohup` or `&`**, which killed an earlier attempt instantly.

### 2.3 Owed by the author (never block on these)
- **dr_2J-10 and dr_2J-11 are CLOSED, both Fable and Gemini vetted (T40 log (bm), T41 log (bn)).**
  Nothing further owed from the author on these two topics. Full record: `deepResearch/
  dr_2J-10_dr2J-11_FABLE_VETTING.md` (Fable half), `deepResearch/dr_2J-10_VETTING.md` and
  `deepResearch/dr_2J-11_VETTING.md` (Gemini half plus the merge with Fable). Headlines: dr_2J-10 Gemini
  verdict NARROWED (Chen et al. 2022 scores 5 of 6 columns, missing only C3) but PARTIALLY SURVIVES
  VETTING (its own Table B "Total Y" column undercounts 12 of 25 rows, corrected counts in the vetting
  file); dr_2J-11 Gemini verdict USABLE and SURVIVES VETTING (real post-2022 WFH decline in both Canada
  and the US, evidence against the manuscript's "persists with probability one" 2030 assumption; one
  figure, the "7.1%" 2016 baseline, NOT CONFIRMED against the real StatCan page). Both merge sections
  state the Fable structural critique and the Gemini live-search facts separately, per plan items 16-19.
  Threading items 16-19 into `manuscript/prep/response_map.md` is still owed as part of WP10 (step 13),
  not from the author.
- **dr_2J-12 CLOSED, both variants in and vetted (log (bf)).** Both reviewed the SUBMITTED text in
  `submission/archive/`, not the four redrafts. Verdict REJECT-LIKELY on both, and it survives vetting: 19
  spot-checked DOIs (Gemini) all resolved on Crossref, 12 spot-checked quotes (Fable) all genuine, no
  fabrication in either. Full vetting write-up: `deepResearch/dr_2J-12_VETTING.md`. Two headline items are not
  new (WP1 = the calibration-provenance fix, WP5 = the missing-measured-data fix, both already the critical
  path). CARRIED items now in `00_REVISION_PLAN.md` §5 items 10-15 (cheap quote-verified fixes: Motuzienė Table
  1 checkmark, a Table-5 miscite in Discussion, the missing lighting-daylight-gate sentence in §7, the EUI-vs-
  SHEU-bands contradiction between Conclusion 1 and Table 5, the circular SHEU-validation wording, the
  2030-cohort-size-is-3x-2022 arithmetic check) plus one new, currently unassigned item: the CATI-to-EQ survey
  mode change lands on the same 2022 cycle as the COVID break and the manuscript does not disclose or rule out
  the confound (needs a Limitations paragraph, WP10). The single most load-bearing finding — the only
  CI-bearing shape deltas are 2022-to-2030, not the WFH break, yet the abstract/highlights/Fig. 6 caption
  attribute them to the break — is assigned to WP1 (provisional-framing fix) + WP10 (abstract/highlights
  wording). Nothing else owed here; this line item is closed.
- **Both of these were asked on 2026-09-17, answered by the author the same day, and are now CLOSED
  (logs (bu) and (bv)). NOTHING IS OWED BY THE AUTHOR. Do not ask again.**
  - **Figure 1: DONE and ACCEPTED (log (bu)).** The author generated it; T47 verified it against the T35
    spec and it matches on every checkable item (24 labels diffed, 33 arrows read out of the generator,
    only arrow 32 dashed, 190.0 x 158.0 mm at 600 dpi, must-not list clean). Use
    `figures/Figure_01_workflow.png` (vector twin `Figure_01_workflow.pdf`). **Never cite
    `Figure_01_pipeline.png`** — that is the retired axonometric figure, restored to its own content after
    the generator overwrote it; plan §5 item 23. The generator's stray write to that filename is removed,
    so the script is now safe to rerun. Still verify the figure against the *installed* document at Step 14
    and snapshot md5s around any gate that re-runs figure scripts. One item is the author's own eye: a 100
    percent zoom or proof-print legibility check, asked for once at figure lock-in.
  - **End-use split: DONE, dr_2J-13 CLOSED, RULE 3 FIRES (log (bv), plan §5 item 24).** The return is
    vetted (`deepResearch/dr_2J-13_VETTING.md`). No measured split exists for Canada; the only one on offer
    is modelled, which the scope guard excluded in advance. The manuscript states the measured end-use
    split was unavailable and attributes the Table 5 gap to **no single end use**. The "4 to 9 times,
    unequivocally located in space heating" sentence **never appears in the paper**, and the basis behind it
    was never established anyway (heated floor space and all-fuel raw combustion energy against our
    simulated site energy). Quote nothing from the chat-side summary of that run; the saved results file is
    the record. Do not rerun the search: the positive control succeeded, so the `NOT FOUND`s are genuine
    absence, not a broken tool.

**Done 2026-09-17 (br), not owed anymore:** the T21 scorer fix and resubmission (`1329216`); the T32
scoring (G0/SC1/SC4/SC5 all PASS) and the submission of its 1,200-run campaign (`1329220`); the
retrospective verification of T29's smoke (PASS 3/3, households 130228/79252). Done 2026-09-16: Step 13's
"sole model" wording fix in `writing/submission/tables/SI/Table_B1_B2.md` (lines 9, 59); T39. Done
2026-09-17 earlier: the independent 52-reference re-verification — 2 real errors, now plan §5 items 20-21,
apply at Step 13.

### 2.4 Process warnings
Three employees broke the login-node ban in an earlier session (`mkdir` twice, `find` once). **Every brief must
name `mkdir` and `find` explicitly as forbidden.** Employees must also be told: no `2>&1`, no `2>/dev/null`
(tcsh), no python on the login node, and `-p ps -t 7-00:00:00` on every job. Add the CPU ceiling to every brief
that submits: never raise `%N` or `--cpus-per-task`, 2J stays at or under 32 CPUs.

## 3. Your queue — every remaining step, in order

Nothing local is running. Steps 1 to 6 are cluster collectors and fire as jobs finish; steps 7 onward are the
writing waves and can start at any time in parallel with the cluster.

**Step 0 — first act of the session.** Start a fresh 30-minute waiter on the still-live jobs (`1328310`,
`1328415`, `1328419`, `1328434`, `1329216`, `1329220` — drop any that have finished). Then `sacct` everything
live, refresh the fifteen progress bars on the checklist page (**it is at Version 51**; read the live page and
diff first — the local source file in a dead session's scratchpad went stale once, so the live page is
master), republish, and send the author one short reply. Steps 7 to 13 need no cluster and can start in
parallel at any time.

**Step 1 — T29 smoke collector: DONE (br), do not re-run.** PASS on all three checks: both households
simulated, 8,760 data rows each (8,761 lines with header), IDs **130228 and 79252** = T21's rebuilt draw,
not the published 130322/80058. Recorded in the T29 impl doc.

**Step 2 — T32 build collector: DONE (br), do not re-run.** G0 PASS (guard output equals T26's λ = 0 file
exactly: checksum plus 100.0 % cell match), SC1 PASS (within 0.012 pp), SC4 PASS (0 FAIL, reproducing T26's
accepted 30/1/0 reading), SC5 PASS (max diff 0.0012 pp). **What is left here is the campaign collector** for
`1329220`, when that array finishes: score it against the T32 doc, and confirm the households are T21's —
the wrapper was verified at submit time by reading the Montreal test cell's manifest (household 130228 at
sample 1), so the collector confirms it end to end rather than re-establishing it.

**Step 3 — T21 collector: DONE and ACCEPTED (bw), do not re-run.** A1, A2 (restated), A2X, A3 and A4 all
PASS at full grid; the selftest was seen failing on a swapped-id copy before any PASS was trusted; one
household's annual kWh was hand-recomputed and matched to six decimal places. Report in
`impl/2026-09-17_T45_T21_collector.md`. **A6 came back "STOP RULE TRIGGERED" and the manager ruled it does
NOT fire** — plan §5 item 25, summarised in the (bw) block at the top of this file. **Do not re-open that
ruling and do not respawn T45.** A5 is report-only by pre-registration and its finding became plan §5
item 26.

**Step 3b — T48, the full-grid A5/A6 run: SUBMITTED, await it.** `impl/2026-09-17_T48_A5_A6_fullgrid.md`
holds the task doc and the employee's Ledger (JobID, interpreter, output path). This is the measurement
nobody has ever made: both Step-9 scripts, **unmodified**, over the T21 rebuild at n=50 on all 24 cells, and
over the published campaign for comparison. When it lands, read the log in this order and rule in this order:
(1) **the seen-working control** — did it reproduce the published `peak_shift_summary.csv` row for row? If
not, stop and treat the instrument as unreliable before reading any new number. (2) **the seen-failing
control** — did a +3 h rotation of one cell's activity hours produce a +3 h reported shift? If not, **A6 is
NOT_TRUSTED and every A6 PASS in this project is worthless**; say so plainly and do not quote an A6 verdict.
(3) **A6 on the rebuild** — 48 rows against the published 48, and the three counts (inside band, outside
band, disagreeing with published by more than 1 h). Rule on any row outside the band on its own merits; the
item-25 subsample reasoning does **not** transfer to a full-grid n=50 result. (4) **A5 provenance** — the
`SHEU +/-15% gate: N/48` line for the published tree and for the rebuild. If the published tree also fails
MidRise/HighRise/OtherDwelling, the T21 doc's "published: all pass" line is the error and the rebuild is
clean; if the published tree passes and the rebuild does not, the rebuild changed the multi-unit archetype
basis and that is a regression that must be traced before WP6. **Either way, no MidRise, HighRise or
OtherDwelling energy-intensity number enters the manuscript until this step is closed.** SingleD is
unaffected and its numbers may proceed.

**Step 3b addendum (bx) — the JobID and one ruling you must not re-open.** T48 is job **`1329258`**,
PENDING on `afterany:1328310` at 4 CPUs, log
`/speed-scratch/o_iseri/2J_revision/T48/logs/t48_a5a6_1329258.out`. The employee flagged that this doc's
Step-2 wording ("roll the 8760 data rows by 3") would have been a **no-op**, because
`step9_loadshape_aggregate.py` sums each row into the bucket named by the **value** of its own `hour`
column, so a whole-record reorder cannot change any output; it kept the `hour` column sequential and rolled
every other column forward by three positions instead, hand-checking an 8-row example. **The manager has
accepted that reading** (plan §5 entry (bx), and a ruling block at the top of
`impl/2026-09-17_T48_A5_A6_fullgrid.md`): it is a genuine phase shift in the only coordinate the instrument
reads, so **Step 2 counts as a valid seen-failing control and the expected reported shift for
`SingleD__Toronto_5A` is +3 h**. Also recorded there: the employee ran one `find` on the login node, which
is not on the allowed list — no impact, but **quote the full allowed-command list in every future brief and
name `find` as forbidden**, because "no python on the login node" was read as the whole rule.

**Step 3c — T49, the WP3 static-arm collector: SUBMITTED as `1329278`, await it; read it controls-first.**
Task doc `impl/2026-09-17_T49_T22_collector.md`, patch task `impl/2026-09-17_T50_T49_checker_patch.md`,
report `/speed-scratch/o_iseri/2J_revision/T49/logs/t49_check_report.txt`. It scores the static
code-schedule arm (array `1328310`) on four gates: **B1** exit states 24/24, **B2** completeness
(24 cells x 50 homes, 8761-line meter files), **B3** the `schedule.json not found` fallback bug, **B4**
household identity against the published draw in `/speed-scratch/o_iseri/step9_run/step9_manifest.csv`,
plus **B3b** log integrity and **B4_PARSE_ECHO** added by T50. Read it in this order: first
`grep -E 'CONTROL_B|CHECKER_NOT_TRUSTED|^GATE_|^VERDICT|B4_PARSE' t49_check_report.txt`. **If any
control did not fire, quote no gate from that run at all.** The script's verdict lines read
`VERDICT: B1=...` through `VERDICT: B4=...` under a `==== VERDICT ====` banner, plus a separate
`VERDICT_B3b:` line — two conventions in one file, because B3b was added later by T50 and keeping the
script's own older convention was the right call (plan entry (bz)). Do not grep `VERDICT_*` alone: it
matches only B3b. Then read the `B4_PARSE_ECHO` line for each cell before any mismatch count — a mismatch
printed with `t22_n=0` is a parsing bug, and a mismatch printed with `t22_n=50 pub_n=50` and two different
ID lists is a real finding — then the offender lines. **Expect B4 to fail.** A
hand spot check already found three different household sets for `SingleD__Toronto_5A` (T22 `HH32815`,
published `HH33298`, T17 `HH33188`). If B4 fails with both set sizes at 50, that is a real finding, not a
checker bug: the static and diary arms ran on **different homes**, so the WP3 comparison is unpaired.
**Plan §5 item 27 holds every WP3 static-vs-diary number out of the manuscript until B4 is scored and the
next task has diagnosed why the draws differ** (compare the household pool of the schedules file T22 read
against the pool the published campaign read — the same seed over a different pool lands on different
homes). Do not choose between re-running the arm and declaring it unpaired before that diagnosis exists.
The diary arm alone is unaffected.

**Step 4 — T28 collector: ADJUDICATED 2026-09-18 (plan log (co)). B0/B1/B2/B5 ACCEPTED. B3 REJECTED as
MIS-SPECIFIED. T60 dispatched to redo it.**

**All four controls fired correctly** — hand arithmetic agreed to 1e-5 against `t28_check.py`'s own
unmodified `_paired_t_ci()`; B1 fired on a swapped `sim_hh_id` (inner exit 1); B2 fired on a 5x meter
perturbation (inner exit 1); seen-working did not fire (inner exit 0). Three outcomes kept distinct, and the
job's own note says it exits 0 regardless and that `sacct` is not the verdict.
**The "no threshold, band or PASS criterion changed" claim is upheld on BEHAVIOURAL grounds, not on the
employee's word: the patched checker was seen both firing and not firing inside the same run.** No `diff` was
run; that is recorded as a limit of the check, not glossed.
**ACCEPTED: B0 1600/1600 delivered with no `undelivered.csv` in any T28 cell (a silence that is now
informative, per (ce)); B1 PASS in all four cells with `pool_ok` and `prefix_ok` true — its printed
`Pool=16326 sampled=200` independently matches the 16,326 paired pool already in
`draft_SI_schedule_completion.md`; B2 PASS in all four; B5 PASS.**

**B3 is REJECTED, and reading it naively would have put a serious error in the paper.** Its CSV has 72
metric-cell rows and **14 carry `inside_t_ci=False`**, which reads as "50 homes is not enough 19 % of the
time". **B1 itself defeats that reading:** `prefix_ok=True` means the 50 are **the first 50 of the same
200**, so the means are nested, and `Var(mean50 - mean200) = sigma^2 (1/50 - 1/200)` is **sqrt(3) times** the
standard error of `mean200`. The flag compares that difference against `mean200`'s **confidence interval** —
a yardstick **sqrt(3) too short** — so under well-behaved sampling it should fire about **26 %** of the time.
**The observed 19 % is BELOW that.** Read correctly the evidence leans *toward* 50 being adequate, **but B3 is
not a test and no verdict may be quoted from it in either direction.** **Same family as item 29 (entry (cd)):
two sides not on the same basis. The band is NOT widened — the band was never the problem.**

**Held loosely until T60:** the flags concentrate in the load-shape metrics (`mean_peak_hour`,
`midday_share`, `evening_ramp_kW_mean`) and especially the `_delta_2022to2030` changes, while energy totals
are largely unflagged. **If that survives the corrected test it is a real, reportable limitation** — energy
and load-shape conclusions would not be equally supported at 50 households. **Not reportable yet.**

**B4, not B3, is where reviewer C3's question is actually answered, and it needs no significance test.**
`t28_b4_convergence.csv` gives the precision achieved at each N; for `SingleD__Montreal_6A` yearly
electricity the half-width runs **81.2 (N=10) -> 55.1 (N=20) -> 18.9 (N=200)** on a mean near 8,175 kWh — a
textbook `1/sqrt(N)` curve, a fraction of a percent of the mean.

**Step 4b — T60, new plan §5 item 36: DISPATCHED 2026-09-18, 1 CPU, arithmetic on the two existing CSVs
only, no re-simulation** (`impl/2026-09-18_T60_b3_nested_subsample_correction.md`). Part A recomputes the
comparison with the correct nested half-width `t(0.975,199)*s_200*sqrt(1/50 - 1/200)`, reports the failure
rate against the 5 % a correct 95 % test gives, **split energy-against-load-shape and level-against-change**.
Part B reads the convergence curve as relative precision, worst-first, and checks it falls as `1/sqrt(N)`.
**Its third control is the load-bearing one:** 72 rows of pure nested noise showing the original flag fires
near 26 % and the corrected one near 5 %, so the mis-specification is **demonstrated, not asserted**.
**T60 LANDED AND IS ACCEPTED — job `1329691`, 30 s, report `T60/logs/t60_b3_correction.txt`. Item 36
CLOSED. Entry (co)'s B3 ruling is now EVIDENCED, not merely derived.**

**Control 3, the load-bearing one, fired exactly as predicted.** On 72 rows of pure noise generated under
the **nested** design, the original `inside_t_ci` logic read `False` **19/72 = 26.4 %** against the
predicted `2(1-Phi(1.96/sqrt3)) = 25.8 %`, and `consistent_nested` read `False` **2/72 = 2.8 %** against the
predicted 5 %. Both inside two binomial SE. **The mis-specification was demonstrated on invented data before
a word of the real result was read.** Controls 1 and 2 also fired.

**Corrected result: 6 of 72 rows inconsistent = 8.3 %**, which is **1.3 binomial SE** from the 5 % a correct
95 % test gives — *not distinguishable from a well-behaved test*. **The rate may not be pushed harder in
either direction:** the 72 rows are 4 cells x 6 metrics x 3 forms and `@2022`, `@2030` and `_delta` are
strongly correlated, so the effective number of independent trials is well under 72. **No adequacy verdict
from a rate.** **The family split is real in direction: energy 0 of 12 flagged, load-shape 6 of 48, every
one in `mean_peak_hour` or `evening_ramp_kW_mean`.** t-based and bootstrap agree 72/72.

**Step 4c — NEW plan §5 item 37: MY OWN BRIEF MIS-SPECIFIED A SECOND YARDSTICK, and I found it by reading
the source rather than the report.** Part B's numbers did not line up with Part A's, so I read
`t28_check.py` myself: `b4_convergence()` (lines 353-380) builds every sub-`N` point as the **2.5-97.5
percentile of 1,000 subsample means drawn WITHOUT REPLACEMENT from the same 200** — a finite-population
quantity carrying `sqrt((200-50)/199) = 0.8682`, with a percentile 1.96 rather than `t(49)`. That explains
to about 2 % **both** anomalies the report surfaced: `B3`'s `halfwidth_t_n50` and `B4`'s N=50 half-width
differ by 14-37 % while their **N=200 values agree to six decimals** (predicted `1.1811 x (s50/s200)`:
SingleD 1.379 vs 1.369, OtherDwelling 1.270 vs 1.246, MidRise 1.376 vs 1.352, HighRise 1.125 vs 1.136); and
`hw50/hw200` sits near **1.73** on all 72 rows because the correct expectation is **1.726**, not the `2.0`
my brief told the employee to expect. **So the convergence curve behaves exactly as it should.** The one row
flagged "far from 2.0" (`MidRise / midday_share@2030`, 1.5589) **is not an outlier and must not be reported
as one**, and the "s50 vs s200 differ by more than 3 %" list (56 of 72 rows) is **noise, not a finding** —
SD of `log(s50/s200)` is about 0.09, so ~74 % of rows should exceed 3 % and 78 % did.
**Rule for the gates doc: a brief that states an expected value is itself a check, and it must be derived
from the code that produces the number, not from the textbook formula that code resembles.**

**WHAT THE MANUSCRIPT MAY SAY ABOUT SAMPLE SIZE — Part B, corrected, never a flag.** The reviewer asks about
drawing 50 from a **16,326-home pool**, not from 200, so the finite-population factor is divided back out
and the honest half-widths are **15 % larger** than Part B prints.
**QUOTABLE: at 50 households a cell's annual electricity total is resolved to better than +/-0.6 % of
itself** (worst 0.5075 % -> **0.585 %**, best 0.378 %); **load-shape LEVELS ~6 % at the median, up to ~49 %
in the worst cell and metric.**
**NOT QUOTABLE, and this is the real limitation: per-cell 2022->2030 CHANGES are not resolved at 50 or at
200.** At N=50 the half-width is 37-64 % of the change for energy and 41-754 % for load shape;
`mean_peak_hour_delta` and `evening_ramp_kW_mean_delta` have intervals containing zero by a wide margin in
every cell. **Rule: no per-cell 2022->2030 load-shape change may be quoted as a change unless its own
interval excludes zero.** Stated as a limitation of what 200 homes resolve — **no band moved, no flag
relaxed.**

**Step 5 — T30 collector: T55 ADJUDICATED 2026-09-18 (plan log (cr)). Six of seven gates PASS; V3 alone is open and re-running as T61.** **Read the `FAILED 1:0` correctly** — that job's wrapper exits with the inner script's top-level code, which distinguishes *a section raised* from *a gate failed*; the report states this itself, which is why one `tail` settled it. **V1 = manifest equality with T21 PASSED, so no cell was stopped** — the outcome most likely to have gone wrong did not. V2 agrees the averaged side with the direct side to about 1e-15 on all 48 rows; V4 shows the weekday-midday at-home change in every cell (+2.31 to +2.90 pp); V5 has zero hits; the excluded-directory rule printed **6 of 54 entries, grid 48**; the hand-check reconciled `sim_hh_id=130228` in `SingleD__Montreal_6A` 2022 by **two independently-coded sums** (pandas and a hand-rolled `csv.DictReader`) to **7,487.405 kWh** over 8,760 rows, agreeing to under 1 J. **V3 DID NOT RUN and must not be read as a FAIL** — it raised on its first statement because the checker's wrapper never exported `IDD_FILE`. T61 re-runs V3 alone; until it lands, **no claim about one-profile-per-cell or about design levels differing may be made from T55 in either direction.** The original dispatch note follows for the record: `1328419` is
DONE 48/48 exit `0:0`. Task doc `impl/2026-09-18_T55_T30_collector.md`, report
`/speed-scratch/o_iseri/2J_revision/T55/logs/t55_t30_report.txt`. V1 and V2 had to be **seen failing on a
copied fake case** before any PASS is trusted; if they were not, quote nothing. **V1 = manifest equality with
T21, and a mismatch STOPS that cell** rather than being reported as a difference. Check the excluded-directory
rule and count (six smoke leftovers) and the end-to-end hand-check of one cell. **Do not respawn a finished
employee.**

**Plan §5 item 38 — a gate that never executed printed a verdict, and every future summary must stop doing that.** T55's `v3_pass` is initialised `False`, the `except` branch sets only an exit code, and the verdict block then printed `VERDICT: V3=FAIL`. A reader of the verdict block alone — which is exactly what a verdict block is for — would have taken a crash for a finding about the building models. **A section that raised before reaching its own test has no verdict; it is NOT_EVALUABLE.** This is the third outcome collapsing into the second one layer below where I had been watching: the *controls* kept the three outcomes apart and the *summary* did not. **Every collector from here on prints the three outcomes — did not run / ran and did not fire / ran and fired — in its summary block, not only in its controls table.**

**Step 5b — T29 revert-array collector** (after `1328434`; 20/24 at (br)). Fresh Sonnet. `1328433`
(S-Partial) is already 24/24 done, so score both scenario arms together against the T29 doc.

**Step 5c — T56, the SI glossary table: CLOSED 2026-09-18 (plan log (cj)).** Plan §5 item 28 is delivered.
`writing/submission/tables/SI/Table_SI_glossary.md`, 12 rows: `J3`, `gate`, `PASS/WARN/INFO/FAIL`,
`True-Future-Test`, `Tier 1/2/3/4`, `FailSafe`, `occACT`, `Step-8 / Step-9`, `COLLECT_MODE`, `DDAY_STRATA`,
`DRIFT_MATRIX`, `C-VAE`, plus seven terms left out with a reason each, written into the deliverable itself so
they travel with it. All three acceptance conditions were met.

**The one thing this task taught, worth more than the table:** the glossary's only substantive claim (the
last-resort matching tier was never triggered) was re-derived rather than trusted, and it held —
`Table_C1_C2.md:22` says `FailSafe tier share | 0% | PASS` and `Appendix_D_deviations.md:83,85` says "all
286,537 Census agents matched in Tier 1-3". **But the unit had changed in the rewrite**: two rows said
*household* where the source says *Census agent*, i.e. a person, and 286,537 people live in 144,507
households. The manager corrected both rows. **A gloss inherits the unit of the thing it glosses, and a
plain-English rewrite is exactly where a unit slips.** Apply this to every WP10 rewrite, not just this table.

**Carry-in attached to this closure — WP10 / Step 13 must settle it, not leave it open.** `Table_C1_C2.md`
and `Appendix_D_deviations.md` have **not** had the plain-language pass the four drafts and `Table_B1_B2.md`
had, and they are where most of this glossary's "Where it is used" citations point. Either those two tables
keep their raw labels and the glossary carries them unchanged, **or** they are rewritten and the Tier,
FailSafe, occACT, Step-8/9 and DRIFT_MATRIX rows are re-pointed or removed. **Whichever is chosen, glossary
and those two tables are re-read against each other once, in the same sitting.** Also unconfirmed: the
`C-VAE` row assumes that label survives in the main text on the strength of `jargon_inventory.md`'s count,
not a re-read — if WP10 replaces it everywhere, the row goes. Step-13 carry-ins are now items **20 and 21
only**.

**Step 5d — T57, the reversion-side exclusion: JOB `1329673` SUBMITTED AND UNREAD, mechanism already in hand
(plan log (ck)).** Plan §5 item 33. Read the report controls-first; if either control did not fire, quote
nothing. **Nothing below is quotable until that block is read** — it is a hand-derivation the job must confirm.

**The pre-registered hypothesis is confirmed, and confirmed in the right order** (written into the brief before
dispatch, into the doc before measuring, then measured). Weekday presence-hour totals for `sim_hh_id 129937`:
**1.5 h** under λ=0.0, **1.0 h** under S-Revert-std, **exactly 2.0 h** under λ=0.5; the band is `[2, 24]` and
inclusive, so the first two are refused and the third passes. `48609` under λ=0.0 is **0.5 h**. All 48 rows are
present in every file, so the household is **computed and then refused by the engine's own sanity check** — it
is not missing.

**The finding is the DIRECTION of the filter, not the missing household.** The reversion arms are the arms in
which at-home time falls; the filter removes the households whose at-home time fell furthest; so the survivors
are the households that reverted least, and **the delivered reversion arm is biased upward in at-home time
relative to the scenario as designed** — the same direction as the effect being measured. **The magnitude is
unknown until item 4 (per-file validation failures broken down by rule, for all four files) is read.** Two
households is a footnote; a population changes what the reversion scenarios may be said to represent.
**Standing rule unchanged: no reversion-scenario number may be described as covering the sampled households
until that count is read.**

**λ=0.5 clearing the band at exactly 2.0 is a warning, not reassurance** — it passes by nothing, so any change
to the blend, the smoothing or the rounding moves households across the edge and silently changes the pool.
**The band is not widened.**

**Ruling already taken, do not reopen: `integration.py` is NOT to be touched.** It documents five rejection
rules and implements four (the "all 24 hours exactly 1 without the retiree tag" rule never executes). Editing
the code would change the sampling pool and invalidate delivered runs; editing even the docstring puts a
modification date on a live pipeline file mid-revision for no gain. It is a documented deviation. **What it
binds is prose: no manuscript or SI sentence may claim the pipeline rejects always-occupied schedules** — it
does not, and `48609`'s weekend profile is all 24 hours at exactly 1.0 and passes.

**ACCEPTED 2026-09-18, plan log (cn). Controls read first and both right** — seen-working "ran and did NOT
fire" in all four files, seen-failing "ran and FIRED" on `R3_presence_bounds` at 1.0 h with the **real**
`validate_household_schedule` agreeing. `real-vs-diag mismatches = 0` and `reopened SIM_HH_ID groups = 0`, so
the streamer's contiguity assumption was checked, not trusted.

**Item 4, the number this turned on.** Households dropped of 144,465: **main (unmodified 2030) 983
(0.680 %); λ=0.5 1,010 (+27); λ=0.0 1,053 (+70); S-Revert-std 1,144 (0.792 %, +161).** Monotone in reversion
strength, and weekday `R3_presence_bounds` carries it: **142 -> 167 -> 202 -> 244**. **The per-rule breakdown
reconciles** — the manager re-derived each arm's excess from its four rule deltas and all three close exactly
(+161, +70, +27).

**RULING: item 33 is a bounded FOOTNOTE plus an SI sentence, not a manuscript blocker.** The worst arm
excludes **161 more households than the unmodified file, 0.111 % of the stock**; a household contributes at
most 24 hours, so **the largest arithmetically possible shift in the weekday at-home share is 0.111
percentage points** — an upper bound, realistic value a fraction of it, inside the 0.5 pp band. **But it is
several times T26's measured design-attainment diffs of 0.0045-0.0216 pp, so it may never be called
rounding.** The direction ruling stands: the filter removes the households that reverted most, so a delivered
reversion arm leans toward those that reverted least. **The band is not widened.**

**CARRY 1, and it is the operational one: (cd)'s common-household rule now covers all four arms.** Four files,
four different pools (983 / 1,010 / 1,053 / 1,144 dropped), and the two reversion arms are **not nested** —
`48609` fails under λ=0.0 at 0.5 h and **passes** under S-Revert-std at 3.0 h. **No cross-arm comparison may
assume a shared household set from the design. Manifest equality is established from the manifests, arm by
arm, or it is not established.** This is exactly why T54's and T55's manifest checks are load-bearing.

**CARRY 2, new plan §5 item 35, surfaced unasked.** Weekend `R2_all_zero` is **288** in the unmodified 2030
file and **exactly 306 in all three scenario files** — **a constant +18, independent of λ**. A blend that
varies with λ cannot produce a λ-independent constant, so **something in the scenario BUILD step, not the
blend, zeroes eighteen households' weekends.** It biases no cross-arm comparison, but a constant appearing in
three separately built files is a bug until shown otherwise. **No job opened**; a WP2 question for when the
scenario build is next opened. Also unexplained, in the opposite direction: weekend `R3_presence_bounds` is
**19** in the unmodified file against **3, 4 and 9** in the scenario arms.

**Report-writing rule added, for every future brief.** Where a household failed on Weekday, the report printed
`Weekend total=nan`; the hourly values beside it were fine (`48609`'s weekend is 24 x 1.0 = 24.0, checked by
hand). The `nan` was a short-circuit artefact of the reporting, not data. **A quantity deliberately not
computed prints "not computed (short-circuited)", never `nan`** — `nan` reads as a data problem.

**Prose correction — WRITTEN 2026-09-18 by the manager (plan log (cq)). This debt is DISCHARGED; WP10
inherits it as text to preserve, not text to write.** `manuscript/draft_SI_schedule_completion.md`'s
sampling-pool paragraph no longer says "a household that is never home at all" — that was never the rule.
It now names the two rules that do the work (**a minimum of two occupied hours in a day type**, and a cap on
presence on/off transitions) and adds a new paragraph, **"The two-hour rule interacts with the reversion
scenarios, and the direction matters."** That paragraph carries T57's whole-file counts (983 / 1,010 / 1,053
/ 1,144), the **161-household = 0.11 %** worst-case bound, and the explicit refusal to call it rounding
because it is several times the 0.005-0.022 pp design-attainment margins. **Two evidence-table rows were
added alongside it**, to that file's own convention: one for the corrected rule with the `129937` worked
case and the named firing rule `R3_presence_bounds`, one for the counts with the manager's independent
per-rule arithmetic closure. **`integration.py` is still not touched, and no prose claims the pipeline
rejects always-occupied schedules** — `48609`'s weekend is all 1.0 and passes.
**Still owed at WP10, and now the only prose debt from items 32/34:** the two dwelling-type sentences
recorded verbatim in plan log (cp). They are deliberately NOT written yet because **no current draft
describes the four-archetype mapping at all** — writing them would mean inventing the section that holds
them, which is WP10's job, not a patch.

**Step 5e — T58: JOB `1329676` SUBMITTED AND UNREAD; item 32 is already ANSWERED at source (plan log (cl)).**

**Item 32's answer, re-read at source by the manager and not taken from the report:**
`0_Occupancy/DataSources_CENSUS/cen21.sps:360-364` reads `DTYPE / 1 "Single-detached house" / 2 "Apartment" /
3 "Other dwelling" / **8 "Not available"**`, with `:84` labelling the variable `'Structural type of
dwelling'`. **`8` is Statistics Canada's own missing-value code.** These are not 43 households of a mystery
fifth dwelling type; they are **43 households whose dwelling type the Census did not release.** Say that
plainly in the SI; it needs no apology.

**The mechanism, also verified at source, and the wording must follow it exactly.**
`21CEN22GSS_occToBEM.py:101-105` maps only `"1"`, `"2"`, `"3"`; line 142 is `.get(val_str, val_str)`, so an
unrecognised value is **passed through unchanged** and `"8"` survives as a literal label; the Apartment
branch never fires for it. **Nothing decides to exclude these households** — they fall out later only because
`ARCH_NAMES` has no member called `8`. **An absence of a category, not a rule that drops rows.** Do not let
the SI sentence imply a rule.

**This task's lesson, and it binds every future brief.** The brief pointed at `codebooks/` and
`references_*`; those are GSS activity codebooks and never mention `DTYPE`. Stopping there would have given
**a NOT FOUND that was only a search in the wrong place** — the worst outcome available, because the brief
had pre-blessed NOT FOUND as a real answer and it would have been believed. **Named search locations are a
starting point, not a boundary; NOT FOUND is honest only after searching where the variable comes from.**

**That guard FIRED, 2026-09-18 (plan log (cm)). Job `1329676` raised at its own seen-working control in two
seconds and produced no count at all** — `ValueError: Usecols do not match columns, columns expected but not
found: ['Day_Type', 'Hour', 'SIM_HH_ID']`, inner exit code `controls: 1`. **`sacct` said `COMPLETED 0:0`.**
**This is the design working, and it is worth more than a clean pass.** Because the brief kept **"did not
run" distinct from "ran and did not fire"**, nothing was produced and so nothing was quoted; and the employee
had pre-registered this exact failure in its own Decisions before the run. **Second evidenced case of a
success signal lying** (the first was (cc)): **where a wrapper can swallow the inner status, `sacct` is not a
verdict — the report's own per-section exit codes are.**

**Cause, established without a job, and it matters for item 34 as much as item 32.** Two files exist and T58
read the wrong one. `..._aug_Full_Aggregated_framev2.csv` is the **person**-level frame (header begins
`PP_ID,HH_ID,MATCH_TIER,occID,...`), carrying `DTYPE` and `BEDRM` as **raw Census codes** and with no
`SIM_HH_ID`, `Day_Type` or `Hour`. `BEM_Schedules_2022.csv` is the **household x day-type x hour** file and
carries `DTYPE` as the **mapped archetype label**. Item 32's own shape — 144,465 households, 6,934,320 rows,
and 6,934,320 = 144,465 x 48 — is the schedule file's. **Item 32 lives in `BEM_Schedules_2022.csv`; item 34
lives in `_framev2.csv`; neither substitutes for the other.** **The split is a gain:** item 34 is only
measurable where the raw codes still exist, and had the first job succeeded on the schedule file, item 34
would have been unmeasurable there and might have looked answered.

**T59 DISPATCHED 2026-09-18, fresh Sonnet, 1 CPU**
(`impl/2026-09-18_T59_dtype8_rerun_and_bedrm8.md`). Part A redoes item 32 on the schedule file with the
144,465 / 6,934,320 reproduction as a **hard stop**. Part B measures item 34 on `_framev2.csv` and is the
more important half. It reuses `t58_dtype8.py` and may not edit anything under `T58/`. **CPU accounting
unchanged at 24 of 32** — T59 replaces a finished job.

**Step 5f — T59, new plan §5 item 34, found by the manager while verifying T58's Q3 and LARGER than item
32.** The same codebook gives **`BEDRM 8 = "Not available"`** (`cen21.sps:252-259`). The Apartment branch
runs `int(float(bedrm_raw))` then `"HighRise" if bedrm_int <= 1 else "MidRise"`. **`8` parses to 8, which is
`>= 2`, so an apartment whose bedroom count the Census did not release is silently classified as a
mid-rise** — not for having two or more bedrooms, but because the missing-data code is a large number. The
`default=2` and `except -> 2` fallbacks land identically. **Why it outranks item 32: the 43 sit OUTSIDE every
weighted figure; these sit INSIDE them, carrying a dwelling type they were never measured to have.**
**It is not yet a number** — the count of `DTYPE == '2'` with `BEDRM == '8'` is unmeasured and may be zero.
**Measure before calling it anything.** `BEDRM` is already a column of the file `1329676` is streaming, so
the agent that reads that report opens T59 with **that one extra count**, reusing `t58_dtype8.py` rather than
writing a second streamer. **T59 LANDED AND IS ACCEPTED — job `1329686`, 41 s, report `T59/logs/t59_dtype8_bedrm8.txt`. ITEMS 32 AND
34 ARE BOTH CLOSED.**

**Controls.** The hard stop held: **6,934,320 rows / 144,465 households** reproduced on
`BEM_Schedules_2022.csv` before any per-value count was quoted. The seen-failing control moved one `DTYPE`
bucket and one `BEDRM` bucket by exactly one each, on **scratch copies**, all other buckets unchanged.
**One defect, recorded not waived: the seen-working control is labelled "ran and fired".** A seen-working
control that fires is a failure. The three outcomes are load-bearing and were used loosely; the substance is
unambiguous so the run stands, but **the next brief must spell the vocabulary out.**

**Item 32 CLOSED. 43 households, 2,064 rows.** *Manager's independent arithmetic:*
`76,366 + 30,716 + 18,835 + 18,505 + 43 = 144,465` and `43 x 48 = 2,064` — **both close exactly.**
**The report proved the exclusion the weak way and I replaced its reasoning, not its number.** It found zero
overlap with the 24 cell manifests and concluded "the exclusion is upstream"; with 1,198 sampled out of
144,465 the **expected overlap with any 43 named households is 0.36**, so zero overlap alone would have been
unsurprising even with no exclusion at all. **The real proof is structural: a cell is named
`f"{archetype}__{city}"` over the four archetypes, so a household labelled literally `'8'` matches no cell by
construction.** The zero overlap is a consistency check that had to pass.
**SI sentence owed at WP10, verbatim:** *"43 of the 144,465 households (0.03 %) carry the Census code for an
unreleased structural dwelling type and therefore fall outside the four building archetypes; they are
excluded from every archetype-weighted figure."* Not dropped silently, not "fixed" — named.

**Item 34 CLOSED as a bounded footnote, same treatment as item 33. 5 households of 49,221 apartments
(0.010 %)**, all five confirmed MidRise; **5 of 144,465 = 0.0035 % of stock.** The `except -> 2` fallback
**never fires on this data**: 0 blank, 0 unparseable.
***Manager's cross-file closure, stronger than anything the report claimed for itself:*** the bedroom counts
come from the **person-level `_framev2.csv`** and the archetype labels from the **household-level
`BEM_Schedules_2022.csv`**, two separately built files. `BEDRM` 1 (17,422) + `BEDRM` 0 (1,083) =
**18,505 = exactly the HighRise count in the other file**, and `21,563 + 6,457 + 1,597 + 1,094 + 5 = 30,716
= exactly MidRise`. **The two files agree to the single household, and the closure only works if the five
unavailable-bedroom apartments sit inside MidRise — which is the finding.**
`BEDRM == '0'` ("No bedroom", 1,083 households) maps to **HighRise**; treating a studio as high-rise is a
deliberate consequence of the `<= 1` rule, defensible, and **left alone**.
**The bedroom-based description of the mid-rise/high-rise split is now permitted in the SI, provided the
five unavailable-bedroom apartments are footnoted.** No code is changed either way — the runs are delivered
against the code as it stands.

**Step 6 — T22 collector** (fires when `1328310` finishes; 21/24 at (br)). Fresh Sonnet. Score the
static-schedule arm, and in the same pass check the Nb-f SHEU design levels and household IDs against the
old file. That comparison decides whether any T22 cell must be re-run; say so explicitly either way.

**Step 7 — deep-research returns: CLOSED, all three pairs vetted.** dr_2J-12 (log (bf)), dr_2J-10 and
dr_2J-11 (Fable log (bm), Gemini log (bn)) are all fully vetted, nothing owed from the author. `NOT FOUND`
/ `NOT CONFIRMED` results were treated as valid, useful information throughout (dr_2J-11's system boundary,
its "7.1%" figure), never discarded or guessed at. Nothing further to do here except thread the CARRIED
items into `manuscript/prep/response_map.md` as WP10 assembles (step 13). **That threading is now DONE
(T42, log (bs)): 55 rows, dr_2J-12's items at Q10-Q16 and plan §5 items 16-21 at Q17-Q22, every one
WAITING/OPEN with its plan item cited.** `Qn` is not plan item `n` — check the row, do not assume. What is
left of this step is only to flip rows to ALREADY FIXED (citing the redraft line in `manuscript/`) as WP10
actually fixes them, and to take Q18's editorial decision when WP1 recalculates.

**Step 8 — Wave 4 re-derivations** (plan §10; can start before the cluster finishes, finishes after it).
Re-derive T06, T07 and T09/T15 on the rebuilt runs. **When T09 is re-derived, re-read the scope paragraph of
`manuscript/draft_S7_limitations.md`**: it describes the measured-data check as Toronto and Ontario electricity on
shoulder-season weekdays, sourced from the old T09 doc. No T09 number is quoted there, so ruling (b) is not
breached, but the description must still match the re-derived run (log (bb)). Under ruling (b), every number these produced on the old
campaign is replaced or dropped — check each against the T36 number trace table, which now marks the seven
OLD-CAMPAIGN / OLD-BUILD rows.

**Step 9 — WP6** (2030 and scenarios). **The clustering question is RULED and moves to WP8 (plan log (cs)); WP6 no longer owns it.** T62 flagged the bookkeeping mismatch — the Progress Log said WP6, the plan's own WP table says WP8, and the code lives in T03's tree, dispatched under WP8. **Resolved in favour of WP8.**

**Step 9b — plan §5 item 39, the clustering check is a STRATIFIED bootstrap and does not test clustering (WP8 owns the fix).** `draft_S2_framework.md:338-340` promises that "the consequence of that clustering is examined in the Supplementary Information". The check already exists (`impl/T03_scripts/ci_reproduction.py:67-83`, `method_b_cluster_bootstrap`) and reported the grouped interval **1.0 to 3.3 % narrower** than the plain pooled t. **That sign is wrong and the sign is the tell** — positive within-cell correlation makes an honest interval **wider**. Reading the code settles it: `cell_arrays` is built once at line 71 and **never resampled**; each replicate keeps all 24 cells at their exact original sizes and redraws households *inside* each one (lines 74-80). That is a **stratified** bootstrap; it removes between-cell variation rather than propagating it. A cluster bootstrap resamples **whole cells with replacement**, 24 drawn from 24.
**Rulings, all five binding:** (1) the sentence is **NOT cut** — delivering it costs one added cell-level draw in a script that already pairs the data and runs on frozen CSVs with a fixed seed; (2) **nothing from method B may be quoted in either direction, and the 1.0-3.3 % figure must never reach the SI as reassurance** — it is an artefact of the wrong resampling unit, and it was measured on an input CSV still carrying the defective 2030 rows; (3) **the function is renamed when it is fixed** — the name `method_b_cluster_bootstrap` is what would have made the wrong number believable to the next reader; (4) **WP8 owns it**; (5) it **reruns on corrected runs** and the SI states whatever it then shows — wider, narrower or indistinguishable. **No band moved, no outcome assumed.** If the honest interval comes back materially wider, the main-text separability claims are re-read against it before anything is quoted.

**Step 9c — the calendar-expansion path is ESTABLISHED (plan log (cs)); WP10 may write it.** The campaign used **`create_compact_schedule()` exclusively** — `Schedule:Compact` written into the IDF — traced from the entry point (`main.py:2065-2070`, `run_fixed_manifest.py`, `step9_idf_gen.py`, `step9_idf_gen_full.py`; none passes `use_schedule_file`, so all take the default `False`). `write_8760_schedule_csv()` is switched on in exactly one place repo-wide, a standalone regression test (`eSim/eSim_tests/task21_regression.py:285`). The two are **not** split between the building model and the plotting path. **Recorded caveat:** only the live tree and one archived snapshot were searched, **not the commit history** — adequate, because the SI describes what the campaign does and the live tree is the campaign.

**Step 10 — WP8**: confidence intervals recomputed on the corrected runs (pooled paired Student-t,
`08_simulation_val.py:951-1027`). **Step 11 — WP3**: the comparison table. **Step 12 — WP11**: figures — write
prompts only for schematic figures; matplotlib plots from frozen data are allowed and preferred. **Figure 1
is already done and verified** (log (bu)): insert `figures/Figure_01_workflow.png`, cite it under that name,
never `Figure_01_pipeline.png` (plan §5 item 23). The manager may write or replace a figure prompt on its
own judgement (author, 2026-09-17), but still never generates the image.

**Step 13 — WP10, the manuscript rewrite for Applied Energy.** Carry in: the response map (42 rows), the jargon
inventory, the SI move list, `draft_S2_framework.md`, `draft_SI_model_selection.md`, `draft_S7_limitations.md`,
`draft_SI_schedule_completion.md`, the Figure 1 prompt. **Plan §5 item 5 is already settled, do not redo it** (log (bc)): Saturday and Sunday are pooled into one
weekend pattern at the building-model interface, `07_aug_to_bem.py:34`, and the tenth limitation is already in
`draft_S7_limitations.md`. At assembly, confirm the SI appendix order and renumber S.5 to S.9 if this part does
not follow the model-selection part, and name which calendar-expansion path the campaign uses
(`create_compact_schedule` or `write_8760_schedule_csv`); no claim turns on it, but the SI should not be vague.
Order matching (2.4) before raking (2.3). Apply plan §5 items 20-21 to the new reference list (Motuzienė
et al. 2022 volume 76→77; Jalilian & Kamel 2025 restore the full subtitle). State plainly: the before/after comparison is **not household-paired
across stocks**; the one-envelope limitation; validator check 3.5; ruling (a)'s weekend limitation; and that **no measured
Canadian residential end-use split exists**, so the energy-intensity gap is attributed to no single end use
(plan §5 item 24 carries the wording, and forbids the "4 to 9 times space heating" sentence). Update
`writing/submission/tables/SI/Table_B1_B2.md` lines 9 and 59 ("sole model" wording). Re-derive or drop the seven
OLD-campaign SI numbers. The internal model label (J3) never appears in prose.

**Step 14 — WP13**: build the submission package, then run `submit_check.py` on the installed files until green.

**Step 15 — Wave 5**: write `deepResearch/dr_2J-08_presubmission_audit_prompt.md` **only after step 14 is green**.
The author runs it in Gemini and Fable 5; vet the return the same way.

After every step: append to the plan Progress Log, tick the plan §9 boxes that closed, republish the checklist
page (read live first, `node --check` the script), and **update §2–§3 of this prompt and its "Last updated" line**.
At session end, update memory `project_2j_paper_writing.md`.

## 4. First reply to the author

One plain headline on where things stand (how many cluster runs finished overnight, and whether anything failed),
3–5 plain bullets, `Evidence:`, `Next:` in 3–4 words. Nothing else.
