# T62 — two unblocked questions the cluster is not holding up

**Dispatched** 2026-09-18 by the manager. **Agent model: Sonnet.** Fresh agent, one task, never resumed.
**No cluster. Read-only. This task edits no manuscript file and runs no job.**

Both questions below are owed by the revision plan, neither depends on any running job, and both have sat
behind the cluster queue for no good reason. Your job is to **find out and report**, not to decide and not to
fix. The manager decides; you supply the evidence the decision needs.

---

## Question 1 — the clustering check that Section 2 promises

`writing/submission/rejection revision/manuscript/draft_S2_framework.md` contains a paired-interval section
that **promises a clustering check**. The plan's rule (manager prompt, Step 9 / WP6) is blunt: **either WP6
delivers that check, or the promising sentence is cut from Section 2.** It cannot stay unbacked.

Report, with file and line for every claim:

1. **Quote the promising sentence verbatim**, with its line number, and quote enough of the surrounding
   paragraph that the manager can see exactly what is being promised and to whom.
2. **State precisely what the sentence commits us to.** What would have to be computed, on what units, for
   the sentence to be true as written? Be concrete: what is the cluster variable, what is being pooled, what
   would the check output look like?
3. **Does that check already exist anywhere in this project?** Search the revision tree and the Step-9
   analysis code for anything that already clusters, groups, or adjusts intervals for non-independence —
   including under other names (grouped, blocked, repeated-measures, random effect, design effect, intra-class).
   Say plainly whether you found it, and if you did, give the path, the function and the line.
4. **If it does not exist, say what it would take** on data that already exists on disk, in one paragraph:
   which files, roughly how much work, and whether it needs a cluster job or could run on frozen CSVs.
5. **Does any number currently in any draft depend on that sentence being true?** Grep the drafts for
   interval/CI claims near it. If nothing depends on it, say so — that matters to the decision.

Do **not** edit `draft_S2_framework.md`. Do not cut the sentence. Do not write the check.

## Question 2 — which calendar-expansion path the campaign actually used

The plan records that the SI must name which calendar-expansion path the campaign uses —
**`create_compact_schedule` or `write_8760_schedule_csv`** — and notes that **no claim turns on it**, but the
supplement should not be vague. Nobody has ever established which.

Report, with file and line:

1. Where each of the two functions is defined, and what each actually produces (compact ruleset vs a full
   8,760-row file).
2. **Which one the 2J revision campaign actually called** — trace it from the campaign entry point, not from
   what looks likely. Name the call site.
3. Whether **both** are used on different paths (for example one for the building model and one for plotting or
   checking). If so, say which is used where. A partly-true answer stated as whole-truth is worse than
   "both, here and here".
4. If the evidence is ambiguous, **say it is ambiguous and say what would settle it.** Do not pick the
   likelier one and present it as found.

## Working rules

- **Read-only.** You may read, grep and search. You may not edit, create or delete any file except this one.
- **No cluster.** Submit nothing. This is a local codebase question.
- Cite everything as `path:line`. A claim without a line number is not evidence.
- **If you cannot establish something, write "NOT ESTABLISHED" and say what you tried.** A clean "I could not
  find it" is worth more than a confident guess, and a guess here would go into a supplement.
- Do not summarise the whole project back. Answer the two questions.

The project root is `C:\Users\o_iseri\Desktop\GSSCanada\GSSCanada-main`. The revision tree is
`2J_docs_occ_nTemp\writing\submission\rejection revision\`. Step-8/9 code lives under
`2J_docs_occ_nTemp\Step8_docs\` and the wider repo; search rather than assume paths.

---

## Findings (written by the agent)

Agent: T62, fresh Sonnet, 2026-09-18. Read-only. No file edited except this append.

---

### Question 1 — the clustering check draft_S2_framework.md promises

**1. The sentence, verbatim, with line number, and its paragraph.**

`writing/submission/rejection revision/manuscript/draft_S2_framework.md` section "2.11 Paired
difference and its confidence interval" (heading at line 315). The full paragraph containing the
promise, lines 327-340:

> "The reported interval is the standard pooled paired Student-t 95% confidence interval on the mean
> difference, [Eq. 16] where $s_d$ is the sample standard deviation of $d_i$ across the $n$ paired
> households (pooled across every simulated cell, not computed separately per cell), and a
> one-sample t-test of $H_0: \bar{d}=0$ is reported alongside it. A difference is treated as
> separable from zero only when this interval excludes zero. **This interval treats households as
> independent and does not account for households sharing a city or an archetype; the consequence
> of that clustering is examined in the Supplementary Information.**" (`draft_S2_framework.md:335-340`,
> promise sentence is `draft_S2_framework.md:338-340`.)

**2. What the sentence commits us to.**

The Methods text (lines 317-320, 327-336) describes: households are joined 2022-to-2030 on
`(archetype, city, household id)`, the per-household paired difference $d_i$ is taken, and a single
pooled Student-t interval is built over **all** paired households across **all** (archetype, city)
cells at once, with no per-cell step and no weighting (`draft_S2_framework.md:317-320, 335-336`). The
cluster/grouping variable named in the sentence is the **(archetype, city) cell** — the same 24-cell
grid used throughout the paper (6 cities × 4 archetypes in the original design; the 2J revision's own
WP2 scenario cells use the same key). "Households sharing a city or an archetype" means households in
the same cell are not statistically independent draws (they share the same building geometry/
calibration for a given archetype, and the same weather file for a given city), so the plain pooled
t-interval understates uncertainty if that correlation is real.

For the sentence to be literally true, the SI would have to show a **second interval, built by a
method that respects the (archetype × city) grouping**, computed on the same paired deltas, and
compare the two — i.e. exactly the pattern "plain pooled interval vs. a cluster-aware interval,
same input data, same metric" with the output being a width/point comparison (not a new number
substituted into the main text). What "examined" commits to, at minimum: (a) a named cluster-aware
method (block/cluster bootstrap, or a cluster-robust SE), (b) applied to the same paired deltas as the
main-text interval, (c) reported side by side so a reader can see whether the plain interval was too
narrow. It does not obviously commit to swapping the main-text number — the sentence only says the
"consequence... is examined," not "is corrected."

**3. Does that check already exist anywhere in this project? — YES, as a method-check script; NOT as
a finished SI section.**

Found. `writing/submission/rejection revision/impl/T03_scripts/ci_reproduction.py`, function
`method_b_cluster_bootstrap` (`ci_reproduction.py:67-83`): for each metric, groups the paired deltas
by `(arch, city)` (`ci_reproduction.py:70`, `d.groupby(["arch", "city"]).indices`), resamples
households **with replacement within each cell**, 10,000 replicates, fixed seed, pools the 24 cells'
bootstrap draws the same flat/unweighted way the submitted method pools the real data
(`ci_reproduction.py:74-80`), and reports a percentile [2.5, 97.5] interval (`ci_reproduction.py:82`).
This is run beside method (a), the plain pooled paired t-interval that reproduces
`08_simulation_val.py:951-1027` / `973-975` (per
`impl/2026-09-15_T03_wp8_confidence_intervals.md:64-86`). This is exactly the "cluster (cell-stratified)
bootstrap of households" the plan's WP8 step calls for (`00_REVISION_PLAN.md:322`), and it is grouped
by the same `(archetype, city)` key named in the draft_S2 sentence.

Task doc for this script: `impl/2026-09-15_T03_wp8_confidence_intervals.md` (WP8, dispatched
`00_REVISION_PLAN.md:315-328`). Results recorded there:
- On the current on-disk `agg_annual.csv` (job 1328238): cluster bootstrap width vs. plain t-interval
  width — `midday_share` 1.0% narrower, `load_factor` 3.3% narrower
  (`impl/2026-09-15_T03_wp8_confidence_intervals.md:116-121`).
- On the archived June-5 `agg_annual.csv` (job 1328253): `midday_share` ~0.2% narrower, `load_factor`
  ~0.6% wider (`impl/2026-09-15_T03_wp8_confidence_intervals.md:128-129`).
- In both cases the change from respecting the cluster structure is "a few percent, not a qualitative
  change" (`impl/2026-09-15_T03_wp8_confidence_intervals.md:120-121`).

**This was explicitly marked a method check, not a paper result**, by both the script itself
(`ci_reproduction.py:28-29`, "NOTE: this input contains the defective 2030 rows (WP1 finding). This
script is a METHOD check only -- outputs are NOT for the paper.") and the task doc
(`impl/2026-09-15_T03_wp8_confidence_intervals.md:31-32`), because part (a) also **failed to reproduce
the submitted manuscript CI numbers** from the current data (computed points were 1.5-5.8x the
submitted points; `impl/2026-09-15_T03_wp8_confidence_intervals.md:99-109`) — the file that produced
the originally-submitted intervals (`outputs_step8_v2/`) is no longer on disk
(`impl/2026-09-15_T03_wp8_confidence_intervals.md:91-94, 111-115, 130-137`). T03's own "Next" section
says "WP8 recomputes on rebuilt data" (`impl/2026-09-15_T03_wp8_confidence_intervals.md:154`), and
`manuscript/prep/response_map.md:67` (row R3-6) records status "DONE" for the *documentation* of the
method (found: plain paired interval, not clustered) but its Note ends "those numbers must be
re-derived from the corrected data" — it does not mention that a working cluster-bootstrap script
already exists.

**I searched and did not find any later task that reran this script on the WP1-corrected data, and did
not find any SI draft file containing this comparison.** Grep for `WP8` across the revision `impl/`
tree returns only `T03`, plus two files that reference T03's open item without adding new computation:
`impl/2026-09-15_T27_wave3_prep_reading.md:271` ("Q5's CI-source-file loss (T03) already flagged...
repeating here since WP8's rewrite depends on it") and `impl/2026-09-15_T10_number_provenance_audit.md:141-143`
(same open item, listed as the top follow-up). The only SI draft files that exist are
`manuscript/draft_SI_model_selection.md` and `manuscript/draft_SI_schedule_completion.md`
(confirmed by `Glob` on `manuscript/draft_SI*.md`); grepping both for "cluster" (case-insensitive)
returns no match. **NOT ESTABLISHED that the clustering check has ever been written into any SI
draft** — I searched every `.md` file under `manuscript/` for "cluster" and the only two hits in that
directory are `draft_S2_framework.md:339` (the promise itself) and `response_map.md:67` (the tracking
row, no computation).

Also searched for the check under other names ("design effect", "intra-class"/"ICC", "random effect",
"cluster-robust", "clustered standard error", "grouped bootstrap", "block bootstrap",
"repeated-measures") across `2J_docs_occ_nTemp` (`Grep -i`, case-insensitive) — no match anywhere in
that tree outside what is already reported above (T03's own bootstrap, which uses the word "cluster"
directly, not one of these synonyms).

**4. What it would take, on data that already exists on disk.**

The script is already written, already tested against real data, and already cheap:
`impl/T03_scripts/ci_reproduction.py` ran in `elapsed_s: 2.86` on the current `agg_annual.csv`
(`impl/2026-09-15_T03_wp8_confidence_intervals.md:48`) and needs only a CSV path argument
(`ci_reproduction.py:88-89`, `--agg-annual`, `--out-dir`). What is missing is not the check itself but
**paper-grade input**: a `agg_annual.csv` built from the WP1-corrected 2030 household frame (the
defective-rows problem T03 flagged, `00_REVISION_PLAN.md` WP1) with a confirmed, reproducible
provenance (T03's central finding is that the file that made the *originally submitted* numbers is
lost, `impl/2026-09-15_T03_wp8_confidence_intervals.md:130-137`). Once WP1's rebuild produces a frozen,
named `agg_annual.csv`, this is: (a) run `ci_reproduction.py` on it — no cluster job required, it is a
small CSV read plus a 10,000-replicate bootstrap in Python, so it can run on a frozen CSV locally or
on a trivial 1-CPU job as T03 itself did (`impl/2026-09-15_T03_wp8_confidence_intervals.md:41-49,
54-58`); (b) write the SI paragraph reporting the plain interval and the cluster bootstrap interval
side by side, citing `ci_reproduction.csv`. Rough scope: one small script run plus a short SI
paragraph — not a new campaign, not new EnergyPlus runs.

**5. Does any number currently in any draft depend on that sentence being true?**

Searched `manuscript/*.md` (all four draft files: `draft_S2_framework.md`, `draft_S7_limitations.md`,
`draft_SI_model_selection.md`, `draft_SI_schedule_completion.md`) for interval/CI-value patterns
(`0.367`, `0.0117`, `CI [`, `95% CI`, `confidence interval`, `midday_share`, `load factor`,
`load_factor`, `ramp`, `peak_hour`). Outside the Methods definitions themselves
(`draft_S2_framework.md:308-309, 315, 328, 414` — which define the metrics and the interval
*construction*, not any specific interval value), **no draft file currently quotes a specific CI
number** (no `[+0.208, +0.526]`-style figure, no point estimate) for midday share or load factor.
`draft_S7_limitations.md` and both SI drafts contain zero matches for any of the above patterns.
**Conclusion: as of this read, no live manuscript number is riding on the truth of the clustering
sentence** — the submitted paper's old CI numbers (`writing/submission/archive/2J_manuscript_submission.md:407`)
are in the archived, superseded submission, not in the active `manuscript/` draft tree, and T03 already
found those old numbers cannot be reproduced from current data regardless of clustering
(`impl/2026-09-15_T03_wp8_confidence_intervals.md:99-109`). That matters to the decision: cutting the
sentence would not orphan any currently-quoted number, and delivering the check would not need to
change any currently-quoted number either, because none exists yet in this draft.

**One bookkeeping note for the manager, not a decision:** the brief calls this a WP6 obligation
("manager prompt, Step 9 / WP6"), and `00_REVISION_PLAN.md:1314` (Progress Log entry (au)) does say
"WP6 must deliver it." But the plan's own work-package table assigns CI/clustering work to **WP8**,
not WP6 (`00_REVISION_PLAN.md:315-328`, "WP8 — How the confidence intervals were built... recompute
with a cluster (cell-stratified) bootstrap of households"; also `response_map.md:67`, row R3-6, WP8
via T03). WP6 (`00_REVISION_PLAN.md:273-291`) is the end-use × hour decomposition package and does not
mention clustering or CI intervals anywhere in its own section. The one existing implementation
(T03) is filed and labelled as WP8 throughout (`impl/2026-09-15_T03_wp8_confidence_intervals.md:1,4`).
I am reporting this mismatch, not resolving it — which work package "owns" finishing the SI writeup is
a manager call.

---

### Question 2 — which calendar-expansion path the campaign used

**1. Where each function is defined and what each produces.**

Both are defined in `2J_docs_occ_nTemp/Step8_docs/eSim_bem_utils_2J/integration.py` (the live,
non-archived module used by the campaign; archived dated copies exist under that folder's `archive/`
and are not the ones imported at runtime — see item 2 below):

- `write_8760_schedule_csv(weekday_vals, weekend_vals, csv_path, year=2025, design_day_dates=None)`
  (`integration.py:453-498`). Produces a **single-column 8760-row CSV**: one value per hour of a
  365-day year, stamping the 24-value weekday pattern on Mon-Fri and the 24-value weekend pattern on
  Sat-Sun, with `design_day_dates` forced to the weekday pattern (`integration.py:483-493`), written to
  disk (`integration.py:495-498`) and referenced from the IDF as a `Schedule:File` object.
- `write_8760_schedule_csv_monthly(monthly_data, csv_path, year=2025, design_day_dates=None)`
  (`integration.py:501-547`) — same 8760-row CSV output but with a **different weekday/weekend pattern
  per calendar month** (used for lighting's monthly daylight variation).
- `create_compact_schedule(name, type_limit, day_schedules)` (`integration.py:550` onward) produces a
  **compact ruleset, not a file**: a list of IDF field strings for a `Schedule:Compact` object —
  `"Through: 12/31"`, then `"For: Weekdays SummerDesignDay WinterDesignDay"` / `"For: Weekends Holidays
  AllOtherDays"` blocks each carrying 24 `Until:`/value pairs (`integration.py:563-579`). This is
  embedded directly in the IDF text, no external CSV.

**2. Which one the 2J revision campaign actually called — traced from the campaign entry point.**

Both functions are called only from inside one function, `inject_schedules()`
(`integration.py:1269-1989`), gated by its own boolean parameter `use_schedule_file: bool = False`
(`integration.py:1279`, default **False**; the sibling function `inject_setpoint_schedules()` has the
same parameter with the same default at `integration.py:1121`). Every call site inside
`inject_schedules()`/`inject_setpoint_schedules()` is wrapped in `if use_schedule_file:` /
`if use_schedule_file and sched_dir:` (`integration.py:1223, 1422, 1600, 1694, 1807, 1875`) — when the
flag is false (the default), the `else` branch calls `create_compact_schedule()` instead
(e.g. `integration.py:1447-1451` for occupancy/metabolic, `integration.py:1246-1254` for setpoints).

The campaign's real entry point: `impl/2026-09-15_T16_step8_run_machinery.md:57` states
`integration.inject_schedules()` "called once per (sample x year) from the campaign loop at
`main.py:2065-2070`" — confirmed directly: `Step8_docs/eSim_bem_utils_2J/main.py:2065-2070` calls
`integration.inject_schedules(idf_path, idf_out, hh_id, schedules[y][hh_id], epw_path=epw_path,
sim_results_dir=output_dir, batch_name=cell_label, run_period_mode=sim_mode,
output_frequency="Hourly")` — **no `use_schedule_file` keyword is passed**, so the default `False`
applies. I grepped the whole of `main.py` for `use_schedule_file` and found **no occurrence at all**
(the string appears nowhere in the file, at any of its four `inject_schedules(` call sites: lines
420, 836, 1756, 2065). Same result for the 2J revision's own scenario-campaign scripts:
`writing/submission/rejection revision/impl/T29_scripts/run_fixed_manifest.py:185` calls
`step8.integration.inject_schedules(...)` with **no `use_schedule_file`** (grepped the whole file, no
match), and Step 9's IDF generators `Step9_docs/step9_cluster/step9_idf_gen.py:166` and
`step9_idf_gen_full.py:170` likewise call `integration.inject_schedules(...)` with **no
`use_schedule_file`** anywhere in either file (grepped both in full, no match).

I also grepped the **entire repository** (both `2J_docs_occ_nTemp` and `3J_docs_occ_nTemp`, plus
`eSim/`) for the literal `use_schedule_file=True`. It occurs in exactly one place outside a docstring/
comment: `eSim/eSim_tests/task21_regression.py:285` (`run_inject(out_dir, use_schedule_file=True,
label="ScheduleFile")`), which its own module docstring identifies as a **regression test comparing
both paths** (`task21_regression.py:6`, "use_schedule_file=False (Compact path) and
use_schedule_file=True (Schedule:File)") — not a campaign script.

**Conclusion: the 2J revision campaign called `inject_schedules()` with the default
`use_schedule_file=False` at every traced call site, so it exercised the `create_compact_schedule()` /
`Schedule:Compact` path.** `write_8760_schedule_csv()` / `write_8760_schedule_csv_monthly()` exist in
the same module and are reachable code, but were not called by the campaign at any entry point I could
find; the only place in the repository that sets `use_schedule_file=True` is the standalone regression
test.

**3. Are both used on different paths (e.g. building model vs. plotting/checking)?**

No separate use found. Both `write_8760_schedule_csv*` and `create_compact_schedule` are called only
from inside the same two functions (`inject_schedules`, `inject_setpoint_schedules`) for the same
purpose — writing the building model's occupancy/metabolic/lighting/equipment/setpoint schedules into
the IDF — and are switched by the single `use_schedule_file` flag, never both active for the same
schedule at once (each `if/else` pair is mutually exclusive, e.g. `integration.py:1422-1451`). I
grepped the whole `2J_docs_occ_nTemp` tree for calls to either function name outside
`integration.py`/its archives and found only: `Step9_docs/prototype/run_prototype.py:198`, which calls
`integration.create_compact_schedule(...)` directly — this is a **5-household exploratory prototype**
script (`run_prototype.py:1-4`, "Step 9 Light — 1-cell activity-driven load prototype... n=5 HH,
seed=42"), not the campaign, and it uses the same Compact path, not the CSV path. No plotting or
validation script anywhere in `2J_docs_occ_nTemp` calls `write_8760_schedule_csv` — I grepped for both
function names across the whole tree (`Grep -n "create_compact_schedule\(|write_8760_schedule_csv\("`)
and every non-definition, non-archive hit is inside `integration.py`'s own `inject_schedules()` /
`inject_setpoint_schedules()`, plus the one prototype script above. **Both functions are used on the
same (single) path family — building-model IDF injection — not split between model-building and
plotting/checking.**

**4. Ambiguity.**

Not ambiguous for the traced call sites (`main.py:2065-2070`, `run_fixed_manifest.py:185`,
`step9_idf_gen.py:166`, `step9_idf_gen_full.py:170`): none pass `use_schedule_file`, so all inherit the
`False` default and all take the `create_compact_schedule()` path. I additionally grepped `use_schedule_file` inside the one dated archive snapshot with its own
`inject_schedules(` call sites, `Step8_docs/eSim_bem_utils_2J/archive/main.20260713_pre144465fix.py`
(four call sites at lines 417, 833, 1753, 2062) — **no match**, same result as the live `main.py`.
**NOT ESTABLISHED**: whether every single IDF-generation invocation across the entire 2J revision
campaign's full run history (any one-off or earlier-dated run not covered by the files checked above)
also omitted `use_schedule_file` — I did not do a repo-wide `git log`-style history search for every
historical version of every campaign driver script, which is out of scope for a read-only local task
with no version-control tooling invoked here. What would fully settle it: a search of every commit
touching `inject_schedules(` call sites for the keyword, not just the current tree plus one archive
snapshot.
