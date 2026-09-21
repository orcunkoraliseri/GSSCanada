# T79 — WP10: Results number sheet (every quotable number, with its source) — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP10 "Rule" (line ~399: every number is re-derived
            from its artifact, never copied from the archived manuscript), plan Progress Log entries
            (cd)-(dq), §5 items 10-40.
Status:     DONE
Agent:      fresh Sonnet employee. **Reading only. No new computation, no python on the login node.**
Why:        the Results section cannot be written until one sheet says which numbers may be quoted,
            from which file, and under which restriction. This task builds that sheet; it writes no prose.

## Output
`../manuscript/prep/results_number_sheet.md` (new file). One row per quotable quantity, grouped by the
new Results order (plan WP10 Structure item 3):
  R1 occupancy change (2015/2022/2030, at-home by hour) -> R2 2030 scenarios -> R3 annual energy by end
  use -> R4 load shape, peak, load factor, midday share, ramp -> R5 full model vs average-profile arm ->
  R6 measured vs simulated check (Toronto/Ontario 2022) -> R7 sample-size check -> R8 model-selection
  threshold sensitivity (SI) -> R9 clustering-aware intervals (SI).
Columns: quantity (plain words) · value · unit · interval if any · source file (path) · row/column or
line where read · accepting plan-log entry · restriction (e.g. "relative only", "1,198 common
households", "not quotable") · figure it appears in.

## Where the numbers live (confirm each path yourself; do not trust this list blindly)
- Local, accepted: `T71_out/fig02..fig05*.csv` (+ `run_meta.json`), `T73_out/*.csv`, `T74_out/`,
  `T75_out/`, `T70_out/`. Their accepting entries: plan log (dk), (dm), (do), (dj).
- On the cluster (`/speed-scratch/o_iseri/2J_revision/`): T68/out (`grid_metrics.csv`,
  `enduse_annual.csv`), T69 outputs (`cross_scenario_common_basis.csv` and change tables), T77 outputs
  (`fig06_comparison_table.csv`, `household_peak_spread_both_arms.csv`), T76 outputs, T67 output.
  **Allowed on the login node: `ls`, `wc -l`, `head`, `grep`, `cat` of ONE small file, and `scp` of
  files under ~2 MB to `impl/T79_in/`.** Never read a multi-MB file into context; never run python there.
  If a needed file is large, record it as "not read, too large" and move on.
- Already-written SI drafts with their own trace tables: `../manuscript/draft_SI_*.md`, and
  `../manuscript/draft_S2_framework.md`. Reuse their numbers only if the trace table names a source.

## Binding rules from earlier rulings (every row must respect them; cite the entry)
- Item 40 / (da): absolute per-dwelling kWh only for SingleD and for equipment/lighting meters; every
  other meter is relative-only. Rows marked NOT_EVALUABLE in T77/T68 files are never quotable.
- Item 30 / (cd): cross-scenario comparisons only on the 1,198 common households.
- (cf): claim the designed 2030 SHIFT, never the absolute LEVEL of the at-home share.
- (cg)-(cs): per-cell 2022->2030 load-shape changes are a "change" only if their own interval excludes
  zero. Annual electricity per cell resolves to better than +/-0.6 % at 50 homes.
- Item 39 / (db): midday-share interval must be the cluster-aware one (wider); never the retired
  "1.0-3.3 % narrower" figure.
- Item 29: no target-attainment claim from gate P2.
- T04 / R3-7: the model was "chosen among four passing candidates", never "the only one that passed".
- A5 is reported as the corrected validator's result; the original's 12/48 is a control, never a result.
- No peak or ramp CI exists (T71): mark "no interval available".

## Also list (separate section at the end)
- Every number the ARCHIVED manuscript's Results/Abstract/Conclusion quoted (`../../archive/2J_manuscript_submission.md`
  lines 1-30 and 360-490) with its status now: REPLACED BY <row>, RETIRED (why), or NO SOURCE FOUND.

## Rules
- Plain words in the "quantity" column. "NOT VERIFIED" rather than a guess. No rounding beyond what the
  source file gives; record the raw value and the rounding the manuscript should use.
- Do not edit any other file.

## Ledger
No cluster jobs run (reading only). Login-node reads used: `ls`/`head -1` on T68's `grid_metrics.csv`
to confirm its column list only (body not read). 21 files scp'd (all < 2 MB) from Speed into
`impl/T79_in/` -- full list with sizes and cluster source paths is in the output sheet's own
"Ledger" section (`../manuscript/prep/results_number_sheet.md`), not duplicated here. Files skipped
as too large (not read): `T68/out/enduse_annual.csv` (2.1 MB), all `enduse_hourly_profile.csv` files
(~510 MB each, T68/T69 x3/T77 would all be this size), `T69/out/*/enduse_annual.csv` (~2.2 MB each),
`T77/out/enduse_annual.csv` (2.2 MB).

## Verified
See the output sheet's own "Verified" section. In summary: every R1-R9 table value was read directly
from its cited file this session; household counts (S-Full 1200/S-None 1198/S-Partial 1200/
S-Revert-std 1199, four-way common basis 1198) and `controls_all_fired=true` on T68/T69/T77 were each
re-read from their own `run_meta.json`/`controls.json`, not assumed from a plan-log summary.

## Decisions
See the output sheet's own "Decisions" section (4 items): sheet granularity = one row per headline
quantity, not per CSV row; per-cell-only metrics are stated as such, never presented as a stock
figure; two divisor/statistic-equivalence conflicts found and left open for a ruling rather than
resolved silently; no new aggregation (stock-weighted peak hour, coincidence factor) was computed.

## Next
Output sheet is built and complete (`../manuscript/prep/results_number_sheet.md`, Status: DONE).
Manager/WP10 next: rule on the open items in the sheet's own "Decisions" #3 and its "Next" section
(divisor conflicts, peak-hour aggregation gap, household-circular-mean stock aggregate), then
dispatch Results (Section 3) drafting from this sheet in the R1-R9 order.

## WHAT I DID NOT VERIFY
See the output sheet's own "WHAT I DID NOT VERIFY" section (7 items) for the full list -- not
duplicated here. Headline items: no multi-MB file was opened; no PNG was viewed by this task (numeric
files only); `draft_S2_framework.md`/`draft_S7_limitations.md`/`draft_SI_schedule_completion.md` were
not read in full; the T48/Step-9 activity-vs-baseline files behind several archived §5.4 numbers were
not located or read (out of this task's T66-T79 file scope).
