# T81 — WP10: Section 3 Results draft — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP10 (Structure item 3, Rule line ~399),
            plan log entries (ds) (four rulings, BINDING), (da), (db), (dh), (dk)-(dq).
Status:     DONE
Agent:      fresh Sonnet employee, text only. **No cluster, no computation beyond reading a value or a
            min/max range out of a local CSV, no literature search.**
Venue:      Applied Energy. Aim for about 2,500-3,500 words of Results text plus figure/table captions.

## Output
`../manuscript/draft_S3_results.md` (new file): Section 3 Results, subsections in this order:
3.1 Occupancy change (R1) · 3.2 The 2030 scenarios (R2) · 3.3 Annual energy by end use (R3) ·
3.4 Load shape: peak, load factor, midday share, ramp (R4) · 3.5 Comparison with an average-profile
model (R5, Figure 6) · 3.6 Independent measured check, Toronto/Ontario 2022 (R6, Figure 7) ·
3.7 Sample-size check (R7, brief, points to SI) · 3.8 Robustness of model selection and intervals
(R8, R9, one short paragraph each, point to SI). Then the trailer blocks below.

## Sources
- **The only number source: `../manuscript/prep/results_number_sheet.md`**, plus the plan-log rulings.
  Every number in prose must match a sheet row (or a file the sheet names) and appear in the trace table.
- Wording/style reference only: archive `../../archive/2J_manuscript_submission.md` lines 360-432 (old
  Results). Frozen: read only. Never carry an archived number; the sheet's Also-list says what replaced it.
- Names of stages/sections/equations: `../manuscript/draft_S2_framework.md`. Point to it (Section 2.x),
  do not repeat methods.
- Figure numbers: use the WP11 numbering the sheet uses (Figures 1-9); Figure 1 of the manuscript is the
  workflow diagram, so write figure references as `Figure [R1-athome]` etc. placeholders if unsure, and
  list them in the trailer. Do not invent a numbering.

## Binding rules (from the sheet header and entry (ds))
- Item 40: per-dwelling kWh only for SingleD and for equipment/lighting; others relative only.
  (ds) Ruling 1: WP5 per-dwelling Facility kWh only for SingleD (8,225.56).
- Item 30: every cross-scenario number on the 1,198 common households; say so once in 3.2.
- (cf): state the designed 2030 SHIFT in at-home share, never claim the absolute level was attained.
- A 2022-to-2030 change is called a change only if its interval excludes zero. S-Partial electricity and
  the S-None / S-Partial shape rows are "no detectable change at this sample size", never "increase" or
  "decrease".
- Item 39: midday-share interval = cluster-aware [0.616, 0.859] pp; never the plain one alone; never
  the retired "1.0-3.3 % narrower".
- Peak and ramp: point values only, with the words "no interval is available".
- (ds) Ruling 2: no "+/-2.7 %"; A5 described only by its own definition (read
  `2026-09-20_T66_A5_per_unit_correction_fix.md` and `2026-09-17_T48_A5_A6_fullgrid.md` for what A5 and A6
  test and their bands); A5 is a check against the fitted target, never "validation". Original 12/48 is a
  control, never a result. If an EUI value is needed, write `[NUMBER NEEDED: EUI]`.
- (ds) Ruling 3: no "17.0-17.7 h" band, no coincidence factor. Allowed peak-timing statements are listed
  in (ds) Ruling 3; confirm fig03's hour convention in `2026-09-21_T71_wp11_figures_wp6_set_IMPL.md`.
- (ds) Ruling 4: headline is "annual electricity nearly flat under the main scenario (+0.12 %), while
  timing and end-use mix move". Say it plainly; do not dress it up.
- Pre-pandemic at-home levels (2005/2010/2015) are being computed by T80: write
  `[NUMBER FROM T80: ...]` placeholders. **Do not state any "+2.2 to +3.9 pp" figure** (item 17 open).
- Model selection: "the candidate with the best combined score among the four that passed all checks".
- R7: the N=200 widening is a change of interval method, never "uncertainty does not shrink".
- Heatmap (R4 Figure 5) is descriptive; no single cell quoted as a change.
- max_kwh_per_premise is never compared across sim and measured.
- Non-causal wording: "associated with", never "caused by". "Scenario-based projection", never
  "forecast". No internal labels (J3, T21, S-Revert-std as a bare code: give each scenario a plain name
  at first use and keep the code in parentheses once). No em or en dashes; no +, ±, ~, Δ symbols in
  prose (write "plus or minus", "about", "change in"). Say "limitation", never "failure".

## Required trailer in the draft file
- `## Number trace table` — every number in the text: value as written, sheet row (R#, quantity), file.
- `## Figure and table references used`
- `## Placeholders left` (T80 numbers, EUI, anything else)
- `## Reviewer items touched` — which review rows this section speaks to (use
  `../manuscript/prep/response_map.md` row IDs; do not edit that file)
- `## Open for the manager` and `## WHAT I DID NOT VERIFY`.

## Rules
- Do not edit any other file except this task doc's sections below.

## Ledger
(no cluster jobs)

## Verified

- Read plan-log entry (ds) in full (`00_REVISION_PLAN.md:4092-4131`) -- four rulings used as binding:
  Ruling 1 (per-dwelling divisor: SingleD only, 8,225.56), Ruling 2 (A5 retired as "48/48 within
  +/-2.7%", quoted only in A5's own words/band, EUI gets `[NUMBER NEEDED]`), Ruling 3 (peak hour: no
  new aggregation; allowed statements are fig03's hour-17/18 max, the Toronto measured check, and
  per-cell circular-mean ranges from T77's table), Ruling 4 (headline "+0.12%, timing and mix move,"
  stated plainly in Section 3.3's opening sentences).
- Read `manuscript/prep/results_number_sheet.md` in full (all of R1-R9 plus the Also-list and header
  binding restrictions) -- every number in the draft traces to a row in this file; none copied from
  any other source.
- Read `manuscript/draft_S2_framework.md` in full for section names/numbers (2.1-2.12), the load
  factor/midday share/peak-hour/paired-CI/comparison-arm definitions (Eqs. 13-18), and confirmed no
  ramp-metric equation exists in the code that document traced (its own trace table row: "Ramp
  metric ... not found ... NOT VERIFIED (absent)") -- so Section 3.4's "evening ramp" is deliberately
  not tied to an equation number.
- Read `impl/2026-09-17_T48_A5_A6_fullgrid.md` (line 17-20) for A5's own definition ("SHEU +/-15%,
  report-only") and A6's own definition (stop rule, band 0 +/-1 h) -- A5's band wording is used in
  Section 3.3; A6 is not quoted anywhere in the draft since no rebuilt A6 number exists on the sheet.
- Read `impl/2026-09-20_T66_A5_per_unit_correction_fix.md` for the mechanism behind the 12/48 vs
  48/48 A5 counts (multi-unit broadcast bug, fixed by a per-cell unit-equivalent divisor) -- used only
  to phrase the one-sentence explanation in Section 3.3, no new number taken from this file.
- Read `impl/2026-09-21_T71_wp11_figures_wp6_set_IMPL.md` in full for the fig03 hour-convention
  question (ds) Ruling 3(a) asks the writer to confirm: the manager's collection independently
  grepped `T68/out/enduse_hourly_profile.csv` at "hour 17" and matched the plotted/reported value
  exactly, which is the only concrete evidence found that the hour column is clock-aligned; no
  document explicitly states 0-23 vs 1-24 indexing, so Section 3.4 words this cautiously ("the
  late-afternoon hour beginning around 5 p.m.") and flags it under Open for the manager.
- Read archive `../../archive/2J_manuscript_submission.md` lines 360-432 (old Results, 5.1-5.4) for
  wording/style reference only -- confirmed no archived number was carried into the new draft; every
  number in the draft was cross-checked against the sheet, not the archive.
- Grepped `manuscript/prep/response_map.md` for row IDs and one-line descriptions to fill "Reviewer
  items touched" -- not read in full (see WHAT I DID NOT VERIFY).
- Ran a plain-text search of the draft body (everything before "## Number trace table") for the
  banned characters `+ ± ~ Δ – —`: zero hits, confirmed with `grep -nF` per character, one at a time
  (locale issue blocked a single combined `-P` regex, so checked individually instead).
- Word count (`wc -w`): draft body (intro through Section 3.8, including inline figure captions) is
  3,181 words, inside the task doc's 2,500-3,500 word target; whole file including the trailer
  (trace table, figure list, placeholders, reviewer items, open items, this section) is 5,374 words.

## Decisions

1. Used bracket placeholder figure tags (`[R1-athome]`, `[R3-enduse]`, etc.) for every figure
   reference in the draft, not just the one the task doc's example names (`[R1-athome]`). Reasoning:
   the manuscript's Figure 1 is the workflow diagram, which does not exist in the WP11 sheet's own
   1-9 numbering at all -- so every WP11 figure number (fig01 through fig09) is one position behind
   wherever the workflow diagram lands as manuscript Figure 1, not only the one figure that
   nominally collides with "Figure 1." Using a real number for fig02-fig09 while placeholdering only
   fig01 would have been inconsistent and would likely need correcting again once the real figure
   list is fixed. All tags are listed in the trailer's "Figure and table references used" table
   against their current WP11 sheet number, so a future pass can renumber mechanically.
2. Converted several R2/R4 confidence intervals from "absolute fraction" units (e.g. 0.004943) to
   percentage points (0.49 pp) for prose readability, matching the units (ds) Ruling 4 itself already
   uses ("load factor +0.49 pp"). Treated this as a straightforward unit conversion (multiply by 100,
   relabel), not a new statistical computation, consistent with the task doc's "read a value ... out
   of a local CSV" allowance -- no new statistic, confidence interval, or aggregate was computed.
3. Placed the A5 SHEU-calibration check (48/48 pass) inside Section 3.3 (annual energy by end use)
   rather than creating a separate subsection, since the task doc's required structure (3.1-3.8) has
   no dedicated slot for it and (ds) Ruling 2 frames it as an energy-magnitude credibility check, the
   same territory as R3.
4. Quoted the single-detached-only circular-mean range in Section 3.5 rather than inventing ranges
   for the other three archetypes, since the number sheet's own R5 row is explicitly scoped to
   SingleD only ("per-city range, SingleD only shown") even though (ds) Ruling 3(c) says "across ALL
   archetypes." Flagged as item 1 under Open for the manager rather than silently either omitting the
   claim or fabricating the missing three ranges.
5. Did not create a separate subsection or paragraph for A6 (the peak-shift stop rule) anywhere in
   the draft, since the number sheet has no rebuilt A6 row (the Also-list entry for the archived
   "0 +/- 1 h" figure is marked "NO SOURCE FOUND in T70-T79 outputs") and neither Ruling 3 nor the
   task doc's R1-R9 structure asks for it.
6. Did not attempt to reconcile the "48/48 within +/-2.7%" vs "48/48 PASS" statistic-equivalence
   question the sheet itself flags as open -- stated the corrected-validator result only in A5's own
   words (a report-only check against a fitted target, band +/-15%), never implying it is the same
   statistic as the old figure. Left as Open-for-the-manager item 4, not resolved here.

## Next

Manager: (1) rule on Open-for-the-manager item 1 (SingleD-only circular-mean range vs Ruling 3(c)'s
"all archetypes" wording); (2) confirm or correct the hour-17/hour-18 clock-time wording in Section
3.4 once a firmer source for the 0-23 vs 1-24 convention is available (item 2); (3) assign real
Figure/Table numbers once the manuscript's figure list and order is fixed, replacing every bracket
tag listed in the trailer's "Figure and table references used" table (item 3); (4) fold T80's
pre-pandemic at-home numbers into Section 3.1 once that task lands, replacing the two `[NUMBER FROM
T80: ...]` placeholders; (5) decide whether the EUI placeholder in Section 3.3 stays open pending a
future task or gets closed as permanently out of scope for this rebuild.

## WHAT I DID NOT VERIFY

(Full list is in the trailer's own "WHAT I DID NOT VERIFY" section inside
`manuscript/draft_S3_results.md` -- not duplicated here in full. Summary: did not re-derive any
number from a raw cluster/local CSV file myself; did not open `T66/logs/t66_report.txt` or any other
raw cluster output; did not read `response_map.md` in full, only grepped it; did not view any figure
image (none exist yet, all are text placeholders); did not check the draft against Applied Energy's
own house style guide beyond this project's own plain-language/no-symbol rules; did not verify word
count by any method other than a plain `wc -w` on the whole file, not split into body vs caption vs
heading words beyond the one before/after "Number trace table" split reported in Verified above.)
