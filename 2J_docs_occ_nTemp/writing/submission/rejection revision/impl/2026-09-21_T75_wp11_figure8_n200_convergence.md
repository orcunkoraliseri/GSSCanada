# T75 — plot WP11 Figure 8 (N=200 sample-size convergence, supplementary information)

Task doc:   this file
Status:     IN PROGRESS — job `1341262` submitted, not yet collected (no-parking rule: this
            employee does not poll/wait; a fresh agent collects when `sacct` shows COMPLETED).

## Background

Plan entry (di) triaged the nine WP11 figures and left Figures 1, 8, 9 unscoped because their exact
source files had not been directory-confirmed. The manager has now confirmed candidate sources for
Figure 8 directly on the cluster (login-node `find`/`head`/`wc -l` only, no computation run):

- `/speed-scratch/o_iseri/2J_revision/T28/out/t28_b4_convergence.csv` (433 lines). Columns seen directly:
  `cell,metric,N,mean,halfwidth` — for each (cell, metric) this has multiple rows at different sample
  sizes `N` (200 seen, and at least one smaller N e.g. 10, in the first 3 lines read), with the mean and
  the confidence-interval half-width at that N. **This is almost certainly the main convergence data** —
  read the full file yourself to confirm the exact set of N values tested per cell/metric.
- `/speed-scratch/o_iseri/2J_revision/T48/pub_loadshape/peak_shift_summary.csv` and
  `loadshape_profiles.csv`, and `peak_hours.csv` — seen to exist, header not yet read by the manager.
  **Do not assume these belong to this figure just because entry (di) named T48 as a candidate** — read
  them and judge whether they are actually part of the "N=200 is enough" story or a different, unrelated
  check that happens to share a task number. If they are unrelated, say so plainly and use only T28/T54.
- `/speed-scratch/o_iseri/2J_revision/T54/logs/t54_t28_report.txt` and
  `/speed-scratch/o_iseri/2J_revision/T54/shadow/` (`b1fail/`, `b2fail/` sub-directories with
  `t28_b3.csv`, `t28_b4.csv`, `t28_check.json`) — this looks like a **checker that validated T28's own
  B3/B4 results** (shadow/seen-failing controls visible in the directory names). Read
  `t54_t28_report.txt` first — it should tell you in its own words whether T28's convergence numbers are
  trusted, and that trust-or-not verdict is a precondition for using `t28_b4_convergence.csv` in this
  figure at all.

## What to do

1. **Read `T54/logs/t54_t28_report.txt` FIRST**, in full (it is a report file, single-file read allowed).
   Confirm its verdict on T28's B4 convergence result before touching any number from
   `t28_b4_convergence.csv` — if T54 found a real problem with T28, do not build this figure yet; report
   that back to the manager instead and stop.
2. **Read `t28_b4_convergence.csv` in full** and identify: how many distinct cells, how many distinct
   metrics, what the full set of tested N values is (this is meant to show that N=200, the sample size
   used everywhere else in this paper, is "enough" — i.e. the halfwidth has already flattened out by 200,
   or is small relative to the mean, or however the underlying build script actually defines "converged").
   Find and read the script that produced this CSV (`T28/T28_scripts/` or similar) for its own definition
   of convergence — do not invent one.
3. **Read T48's three CSVs' headers and judge relevance** (see Background) before including or excluding
   them.
4. **Design the figure to match this project's established style** (T71/T73 precedent: dpi=600, PNG, flag
   anything without a real interval, state units). A reasonable default: halfwidth (or halfwidth/mean, a
   relative measure) on the y-axis, N on the x-axis, one line per cell or per metric-family, showing the
   curve flattening by N=200 — but confirm this makes sense against the actual data before committing to
   it, and pick a manageable number of lines/panels if there are many cells (aggregate or facet sensibly,
   state which you chose and why).
5. **Controls required:**
   - **Seen-working control:** independently re-read at least 2 (cell, metric, N) rows directly from the
     CSV and confirm they match the figure.
   - **Row-count/completeness control:** confirm every distinct cell/metric combination present in the
     source data appears in the figure (or state exactly what was aggregated/excluded and why).
6. Save the PNG under `/speed-scratch/o_iseri/2J_revision/T75/out/figures/fig08_n200_convergence.png`.
7. Write `T75/logs/t75_run_meta.json` (JobID, elapsed, figure metadata, controls, and T54's verdict on
   T28 that you relied on) following T71/T73's `run_meta.json` shape.
8. **Submit via `sbatch`, do not wait, do not poll.** Write the JobID into this file's Ledger section
   below, then end your turn. The manager collects when `sacct` shows COMPLETED and views the PNG via
   `scp` before accepting.

## Ledger

- **Precondition check — read `T54/logs/t54_t28_report.txt` in full first** (single-file `cat`,
  login-node allowed). Verdict block: `B0=PASS (1600/1600 delivered)`, `B1=PASS`, `B2=PASS`,
  `B3=REPORT (not a band...)`, `B4=REPORT (convergence curve, CSV only, no PASS/FAIL band)`,
  `B5=PASS`. All three of T54's own controls (hand-arithmetic control 4, B1 seen-failing shadow,
  B2 seen-failing shadow) fired exactly as intended (`outcome: ran and agreed` / `ran and fired`
  / `ran and did not fire`). **No FAIL anywhere. T28's B4 convergence CSV is trusted** — B4 is a
  REPORT type (no pass/fail band was ever defined for it, by t28_check.py's own design), not a
  gate that could have failed silently. Proceeded past this precondition.
- **Read `T28/out/t28_b4_convergence.csv` in full** (downloaded via `cat` over ssh to a local
  scratch file, then processed locally — only `cat`/`wc -l`/`head` ran on the login node): 433
  lines (432 data rows), matching T54's own report line `[B4] wrote 432 rows`. 4 cells (all
  Montreal archetypes: `SingleD__Montreal_6A, OtherDwelling__Montreal_6A, MidRise__Montreal_6A,
  HighRise__Montreal_6A`), 18 metric labels (6 base metrics x 3 variants each: `@2022`, `@2030`,
  `_delta_2022to2030`), 6 N values (`10, 20, 50, 100, 150, 200`). 4 x 18 x 6 = 432, exact.
- **Read `T28_scripts/t28_check.py` (`b4_convergence()`, `_paired_t_ci()`) for the script's own
  definition of convergence** — not invented. Found a load-bearing methodological split (see
  Decisions/FINDING below): the N=200 row is a parametric Student-t 95% CI half-width on the real
  full 200-household sample; the N=10..150 rows are a percentile (2.5/97.5) spread of 1000
  bootstrap-style subsample-mean draws (no replacement) from that same 200. Two different
  statistics sharing one column name.
- **Read T48's three CSV headers and their producing scripts** — judged NOT relevant to this
  figure (see Decisions). Confirmed by reading `T48/scripts/step9_validate_full.py`,
  `step9_loadshape_aggregate.py`, `t48_helpers.py` file names directly on the cluster; none of
  T48's three CSVs has an `N` or `halfwidth` column — they carry `n_hh` (fixed at 50) and
  equip/light building/zone peak-hour-shift columns for an `activity`-vs-`baseline` schedule
  comparison. This is the project's Step-9 peak-shift work (matches the project memory's T48
  entries), unrelated to sample-size convergence.
- Wrote `T75_scripts/t75_fig08_n200_convergence.py` (new file). `py_compile` clean both locally
  (`py -3.13`) and on the cluster with the project interpreter
  (`/speed-scratch/o_iseri/envs/step4/bin/python`). matplotlib 3.10.8, pandas 2.3.3, Pillow 12.1.1
  confirmed importable on that interpreter (single-file `python -c` checks, login-node allowed).
- **Ran a full functional smoke test locally against the REAL downloaded CSV and REAL downloaded
  T54 report** (not synthetic data — both files small enough to test directly), by rewriting only
  the three path constants (`T75_ROOT`, `T28_CSV`, `T54_REPORT`) to local paths and executing the
  unmodified script body. First run correctly caught a bug in my own precondition-parsing logic
  (matched the word "VERDICT" anywhere in the line, which also matched an unrelated line
  containing "see VERDICT block" and produced a false FATAL) — fixed to match lines starting with
  `VERDICT:` only, re-ran, passed cleanly. Ran to completion in 0.8s, produced a 144-row CSV, a
  PNG, and `run_meta.json`. **Visually inspected the PNG twice** — first pass had the title
  overlapping the method-note subtitle and the legend clipped at the bottom edge; fixed spacing
  (`tight_layout` rect + explicit suptitle/legend y-positions, taller figure), re-ran, second pass
  confirmed clean: title, 3-line method note, six panels (2x3), and the shared legend all readable
  with no overlap or clipping.
- CPU/queue check: `squeue -u o_iseri --format='%i %j %t %C'` showed `histnu` array (32 CPUs busy,
  1 each), a few `wp9_*`/`t72_v3fix` jobs at 1 CPU each — this job requests only 1 CPU / 8 GB, well
  within headroom.
- **JobID `1341262`** submitted from `speed-submit2`:
  `sbatch -p ps -c 1 --mem=8G -t 7-00:00:00 --job-name=T75_fig08
  --chdir=/speed-scratch/o_iseri/2J_revision/T75
  --output=/speed-scratch/o_iseri/2J_revision/T75/logs/t75_run.out
  --wrap='/speed-scratch/o_iseri/envs/step4/bin/python
  /speed-scratch/o_iseri/2J_revision/T75/T75_scripts/t75_fig08_n200_convergence.py'`
  Single `squeue -j 1341262` check immediately after submission: `R` (running), node `antenna1`,
  0:01 elapsed — not polled further, per the no-parking rule.
  Output paths (all under `/speed-scratch/o_iseri/2J_revision/T75/`):
  - `logs/t75_run.out` — stdout/stderr of the job
  - `out/figures/fig08_n200_convergence.png` — the figure
  - `out/figures/fig08_n200_convergence.csv` — the 144 plotted rows + a `ci_method` column
  - `logs/t75_run_meta.json` — dpi/pixel size read back via Pillow, T54 precondition record, T48
    relevance judgement, figure scope, row-count/completeness control, seen-working control,
    and the N=200 method-switch finding (counts + examples)

  **The job's own real cluster output has not been read by this employee** — only the LOCAL
  functional-test copy (same code, real downloaded CSV/report, run on this Windows machine, not
  the cluster) was inspected. A failed job stays in this ledger with the line that supersedes it —
  never dropped.

## Verified

- **T54's verdict on T28 (precondition)**: `B0=PASS`, `B1=PASS`, `B2=PASS`, `B3=REPORT`,
  `B4=REPORT` (no PASS/FAIL band was ever defined for B4), `B5=PASS`. No FAIL anywhere. Read
  directly from `T54/logs/t54_t28_report.txt`, in full.
- **Row-count/completeness control (local functional test, real data)**: expected 4 cells x 6
  delta-metrics x 6 N values = 144 rows for the plotted `_delta_2022to2030` scope; found 144;
  `missing_or_duplicate_combos = []`. All 432 rows in the source CSV accounted for: 144 plotted
  (delta variant) + 288 present-but-not-plotted (12 level labels x 4 cells x 6 N = 288, the
  `@2022`/`@2030` rows) = 432, matching the full file exactly.
- **Seen-working control (local functional test, real data, independent boolean-mask read, not
  the plotting code path)**:
  - `SingleD__Montreal_6A, elec_facility_kWh_delta_2022to2030, N=200` -> `mean=12.029615887146749,
    halfwidth=4.2046006657626025` — matches the raw CSV row read separately during reconnaissance.
  - `MidRise__Montreal_6A, mean_peak_hour_delta_2022to2030, N=100` -> `mean=-0.1514731474096963,
    halfwidth=0.2667642666595441` — matches the raw CSV row read separately during reconnaissance.
- **FINDING (load-bearing, real data, all 24 of 24 combos, not a sample): every one of the 4
  cells x 6 delta-metrics combinations shows `halfwidth(N=200) > halfwidth(N=150)`** — the
  bootstrap-percentile curve is still shrinking at N=150, then jumps back up at N=200 because
  N=200 switches to a different statistic (parametric Student-t CI on the real full sample vs.
  percentile spread of 1000 bootstrap-subsample means for N<200). Confirmed by reading
  `t28_check.py:353-380` (`b4_convergence`) and `t28_check.py:288-300` (`_paired_t_ci`) directly,
  and by computing the comparison on all 24 real (cell, metric) pairs in the local functional
  test — 24/24 show the jump, universally, not sporadically.
- **Units, read directly from `t28_check.py`'s `household_metrics()` (lines ~111-125)**:
  `elec_facility_kWh` = annual kWh (sum of hourly kW), `mean_daily_peak_kW` = kW, `mean_peak_hour`
  = hour-of-day (circular mean, 0-23), `load_factor` = unitless mean/max ratio (0-1),
  `midday_share` = unitless fraction of annual kWh in hours 9-17, `evening_ramp_kW_mean` = kW
  (hour17 minus hour14 daily load, averaged over 365 days).
- **T48 exclusion, read directly**: `peak_shift_summary.csv` columns
  `cell,year,equip_bldg_shift,equip_zone_shift,light_bldg_shift,light_zone_shift`;
  `loadshape_profiles.csv` columns `cell,year,arm,hour_of_day,equip_bldg_W,equip_zone_W,
  light_bldg_W,light_zone_W,facility_W,n_hh`; `peak_hours.csv` columns
  `cell,year,arm,equip_bldg_peak_h,equip_zone_peak_h,light_bldg_peak_h,light_zone_peak_h,n_hh`.
  No `N`/`halfwidth` column in any of the three. Producing scripts confirmed on the cluster:
  `T48/scripts/step9_validate_full.py`, `step9_loadshape_aggregate.py`, `t48_helpers.py`.
- **Local functional-test PNG**: dpi read back via Pillow = `(599.9988, 599.9988)` (the same
  harmless PNG pixels-per-metre rounding artifact T71/T73 already documented — effective 600 dpi
  to 4 decimal places, not a shortfall), pixel size `6900x4920` at the `figsize=(11.5, 8.2)`,
  `dpi=600` setting.

**Everything in this section came from the LOCAL functional test against the real (downloaded,
read-only) CSV and T54 report, or from direct file/script reads — none of it is from the cluster
job's own output, which is unread as of this write (see WHAT I DID NOT VERIFY).**

## Decisions

1. **T48 EXCLUDED entirely from this figure**, not just its three files judged irrelevant in
   passing — confirmed by reading both the CSV headers and the scripts that produced them. This
   is the project's Step-9 activity-vs-baseline peak-hour-shift check (`n_hh` fixed at 50 per row,
   `arm` = `activity`/`baseline`), sharing only the task NUMBER "48" with plan entry (di)'s earlier
   unconfirmed guess, not the content. No column in any T48 file resembles a sample-size sweep.
2. **Figure plots only the `_delta_2022to2030` metric variant (6 of the CSV's 18 metric labels)**,
   not the `@2022`/`@2030` level variants. This project's own established "quotable" convention
   (2J plan log, entries (cg)-(cs), 2026-09-18) scores and quotes the 2022->2030 CHANGE, not the
   raw levels — so the convergence question that actually matters for the manuscript is "is the
   change estimate's CI narrow enough by N=200", not the level's. The 288 level rows remain
   untouched in the source CSV and in `run_meta.json`'s scope record, not silently dropped — just
   not the headline of this figure.
3. **6-panel grid (2 rows x 3 cols), one panel per base metric, 4 lines per panel (one per cell)**
   — the natural facet given 6 metrics and only 4 cells (all Montreal, so city is not a facet
   dimension here — this project's B4 convergence check only ever covers Montreal_6A cells, not
   the full 3-city set used elsewhere in the paper; not this employee's choice, inherited from
   what T28 actually scored). Native units kept per-panel (not normalized to a relative
   halfwidth/mean ratio) because several delta means sit very close to zero (e.g.
   `mean_peak_hour_delta` around -0.03 to -0.23 hours), which would make a relative measure
   explode or be uninterpretable for those metrics — an absolute halfwidth in each metric's own
   unit is the honest, comparable-within-panel choice.
4. **N=200 drawn with a visually distinct marker (star, not a circle-line point) plus a vertical
   dashed guide line, and the figure's own subtitle states the method switch in three sentences**
   — this is the single most important design decision, forced by the FINDING above. Silently
   connecting N=150 and N=200 with the same line style would visually claim the curve "keeps
   converging" through N=200, which the underlying statistic does not actually show (it switches
   methods and, for every metric tested, gets slightly WORSE, not better, in absolute
   half-width). Never smoothed over, per this project's rule against presenting a misleading
   picture even when the underlying numbers are individually correct.
5. **PNG at dpi=600, figsize (11.5, 8.2) inches** — matches T71/T73's PNG-for-checkable-dpi
   convention. Taller than T71/T73's figures because 6 panels plus a 3-line method subtitle needed
   more vertical room; first draft (8.2->6.8 in height, see Ledger) had visible title/legend
   overlap on inspection and was corrected before the cluster job was submitted.
6. **No confidence interval is invented anywhere** — every plotted half-width is read verbatim
   from T28's own CSV; this script performs zero new statistical computation, only aggregation
   (subsetting to the delta rows) and plotting, consistent with the brief's "do not invent a
   convergence definition" instruction.

## Next

- Manager collection (fresh agent, later): `sacct -j 1341262` first for state/exit code, then
  `logs/t75_run_meta.json` (`t54_precondition`, `t48_relevance_judgement`, `figure_scope`,
  `controls.row_count_completeness`, `controls.seen_working`,
  `finding_n200_method_switch` — confirm these read the same on the real cluster run as they did
  in this employee's local functional test against the same input files), then the PNG and CSV
  themselves (visual inspection of the PNG, same as T71/T73's manager-collection style).
- If the cluster job's `seen_working`/`row_count_completeness`/`finding_n200_method_switch` numbers
  differ AT ALL from the local-test numbers recorded above (same input files, so they should match
  exactly), that is a new finding needing diagnosis before the figure is trusted — do not assume
  environment parity.
- scp the PNG + CSV + `run_meta.json` back to `impl/T75_out/` for manager/author viewing (not yet
  done as of this write for the CLUSTER job's own outputs — only the local-test copies exist in
  this employee's scratch temp directory, not in the repo, and must not be confused with the real
  cluster output).
- This is WP11's Figure 8 (N=200 sample-size convergence). Remaining WP11 work per T71/T73's own
  "Next": Figure 6 (blocked on T30), Figure 9 (T74, in progress separately), Figure 1 (T76, in
  progress separately).

## WHAT I DID NOT VERIFY

- **Any number produced by the actual cluster job (`1341262`).** Everything numeric in
  `## Verified` above comes from a LOCAL functional test of the exact same script against the
  downloaded (real, unmodified) CSV and T54 report, plus direct file/script reads — not from the
  cluster job's own execution. `logs/t75_run.out`, `logs/t75_run_meta.json`, the CSV, and the PNG
  on the cluster are all unread as of writing this doc.
- Whether the cluster job completes within a reasonable time or hits any environment difference
  (different matplotlib/pandas version rendering behavior). The local test ran in 0.8s on a 40 KB
  CSV with no chunking, so the cluster job (same tiny input) is expected to be similarly fast, but
  this is an expectation, not a measurement of job `1341262`.
- **Whether the N=200-vs-N<200 method-switch finding, and the "N=200 is enough" story more
  broadly, changes the manuscript's own trust in its N=200 sampling choice.** This employee flags
  the methodological mismatch clearly (both in the figure and in this doc) but does not judge
  whether the manuscript's existing convergence language needs revision — that is a manager/author
  call, not made here.
- Whether T28's B4 convergence check (Montreal-only, 4 archetypes) is representative of the other
  two cities used elsewhere in the paper — not evaluated; T28 itself only ever scored Montreal_6A
  cells (inherited scope, not a choice made in this task).
- Whether Applied Energy's own figure guidelines would prefer a different metric selection,
  relative-vs-absolute halfwidth axis, or panel layout than the 6-panel grid chosen here — not
  read for this task (same caveat T71/T73 already logged for their own defaults).
