# P16 — Madrid incomplete-cells number check (840 vs 170)

Task doc: prompt given directly by manager, 2026-09-23 (no separate task file).
Status: DONE — CORRECTED by manager 2026-09-23 (see "Manager correction" below; the employee answer
"840 is right" is SUPERSEDED).

## Manager correction (2026-09-23) — 170 cells / 17 buildings is right; 840 / 84 was an earlier run
Read directly from the final Madrid run tree `_local_runs/4J_ES_local/out/ES-MAD-BERRUGUETE/`:
- `cells/` holds 11,340 result files over 1,134 buildings (5,670 caseA + 5,670 caseB) — the 11,340 in S9.
- `cells_failed/` holds 170 files over 17 buildings; `campaign_results.json` has 170 `"completed": false`
  (ENERGYPLUS_FAILED) in the last session. 11,340 + 170 = 11,510 planned. Closes exactly.
- The failure log `C2_ES_failure_progress_log.csv` (84 buildings, 840 cells) is from the EARLIER campaign:
  of its 84 buildings, 76 completed in the final run and 8 are among the final 17 failures.
- The employee's "670-cell gap" came from mixing the earlier log with the final count; it does not exist.
- Bologna check: 11,710 planned - 11,680 completed = 30 = the three courtyard buildings x 10. Consistent.
**Applied:** SI S9 (line 466) and S12 (line 620) now say "170 cells in 17 buildings". Backup:
`writing/submission/previous/4J_supplementary_material.md.pre_madrid170_20260923` (cmp-verified).
The proposed "not reconciled" sentences below were NOT used (process notes are not allowed in the paper).

## Question

SI sections S9 and S12 (`writing/submission/4J_supplementary_material.md`) say "840 cells in 84
Madrid buildings did not complete", next to "35,090 completed cells" (Madrid share 11,340). A
planned Madrid figure of 11,510 minus the 11,340 completed gives 170, not 840. Which number is
right, and what should the sentence say?

## Verified

1. **Current SI text, exact wording** — `writing/submission/4J_supplementary_material.md:461,466`
   (S9): "...with 35,090 completed simulation cells (Madrid 11,340, Bologna 11,680, London
   12,070)... In Madrid, 840 cells in 84 buildings did not complete and were not repaired." And
   `:620-621` (S12): "In Madrid, 840 cells in 84 buildings did not complete, and three courtyard
   buildings in Bologna are outside the subdivision method." Read directly.

2. **The figure 11,510 does NOT appear anywhere in the current submission.** Checked with
   `grep -n "11,510\|11510\|35,290\|35290" 4J_manuscript_submission.md 4J_supplementary_material.md`
   inside `writing/submission/` — zero hits in either live file. It exists only in
   `writing/submission/archive/*/4J_manuscript_submission.md` and
   `writing/submission/previous/*/4J_manuscript_submission.md` (superseded backups) and in
   `writing/submission/IMP/prep/results_number_sheet.md` as a *rejected* historical figure. So the
   "840 vs 170" comparison in the question is built by importing a number (11,510) that the current
   SI text never states — it is not an internal contradiction of the document as it stands today.

3. **840 / 84 is independently verified against the campaign's own failure log**, not derived by
   subtraction. `Step10_docs/impl/C2_ES_failure_progress_log.csv` — read in full (85 lines, 23,931
   bytes). Every one of the 84 data rows (one row per distinct `building_id`) carries
   `n_failed_cells=10`. Checked the arithmetic directly:
   `awk -F',' 'NR>1{sum+=$2; n++} END{print n, sum}'` → `84 rows`, `sum=840`. The last row
   (`way-987123378`, line 85) is explicitly logged "at ES completion" with the note
   "830->840 failed cells at ES completion, **cells_finished==cells_planned==11510**" — i.e. this
   is the campaign's own final tally, not a preflight estimate, and 11,510 (not 11,340) was the
   runner's own live planned/finished counter for Madrid at that moment.

4. **The 11,340 "completed" figure is a separate later count, from a separate method, of a
   separate campaign artefact.** `Step10_docs/4thJ_10_nocoreRealStock_val.md:128` (dated
   2026-09-16, "THE SUITE IS SCORED IN FULL"): "35,090 real, completed `C2` cells (`es` 11,340 /
   `uk` 12,070 / `it` 11,680)... read directly from
   `_local_runs/4J_{ES,UK,IT}_local/out/<DISTRICT>/cells/*.json`" — i.e. 11,340 is a count of
   result JSON files on disk, not `(planned − failed)` arithmetic. The same doc states explicitly,
   in caps: "NO ENERGYPLUS WAS INVOKED, NO CELL WAS RE-RUN" between the failure log (above) and this
   scoring pass — ruling out a repair/rerun between the two readings as the explanation for any gap.

5. **The two verified numbers do not arithmetically close, and I found no file that reconciles
   them.** If cells_planned = cells_finished = 11,510 (from the failure log, item 3) and 840 of
   those failed, the implied successful count is 11,510 − 840 = 10,670 — not the 11,340 actually
   used in the paper (item 4). That is a 670-cell gap between what the failure log implies should
   have survived and what the final JSON-file count actually shows. I searched
   `Step10_docs/*.md`, `Step10_docs/impl/*.md` for "floor-averaging", "courtyard", "repaired",
   "re-run/rerun" and found no document describing a change to the Madrid planned/eligible building
   count, or a repair pass, between the failure log's "ES completion" event and the 2026-09-16
   scoring. **NOT FOUND: an artifact explaining the 670-cell gap.**

6. **`results_number_sheet.md` (P9, `writing/submission/IMP/prep/results_number_sheet.md`)**
   already carries this exact material, checked today (2026-09-23), as two separate rows:
   `B15b` (line 239) flags planned-vs-final Madrid counts (11,510 planned vs 11,340 final) as
   MISMATCH, with the fix recommendation to use the final completed numbers (already done in the
   live SI — see item 2). `B16` (line 240) independently checks "840 cells... across 84 buildings"
   against the failure log and marks it MATCH (exact). Neither row cross-checks B15b's gap (170)
   against B16's count (840) against each other — the sheet's own note only says 840 is "correctly
   attributed to the LARGER (35,290/35,090) campaign", not that it reconciles to 170. So the P9
   audit did not itself catch or resolve the inconsistency in item 5; it verified each number
   separately and correctly, but never combined them.

7. **The "320 collision cells" exclusion is a different, later step and is not the same
   population.** `grep -n "320 collision\|collision" writing/submission/4J_supplementary_material.md`
   returned zero hits — the word "collision" does not appear in the current SI at all. Confirmed
   these are unrelated: the 840 Madrid failures are EnergyPlus geometry/construction failures
   caught by `Step10_docs/impl/C2_ES_failure_progress_log.csv` (signature classes (a)/(b1)/(b2)/(c)/(d)
   and several unclassified vertex-mismatch/zero-area buckets); nothing in that file or in S9/S12
   mentions a cache-key collision. Not merged.

## Answer

840 is the right number and should stay: it is read directly, and confirmed by re-summing, from
the project's own per-building EnergyPlus failure log for Madrid, logged at the campaign's actual
completion (not a preflight estimate). 170 is not an independently measured failure count at all —
it is just 11,510 minus 11,340, and 11,510 is a stale preflight figure that has already been
removed from the current manuscript and SI (it appears only in old backups), so it should not be
used or implied anywhere in the live text. That said, the two verified numbers do not fully add
up: the failure log's own "11,510 planned, 840 failed" statement implies 10,670 successful Madrid
cells, but the completed-cell count actually used in the paper (11,340, from a separate later
file-count method) is 670 higher, and no document I found explains that gap or shows a repair/rerun
that would close it. The current SI sentence is not internally self-contradictory (it never states
11,510), but the underlying campaign accounting has an unresolved 670-cell gap that should be
flagged to the author, not silently smoothed over.

## Proposed SI sentence (exact replacement text; NOT applied)

For S9 (`4J_supplementary_material.md:466`), replace:
> In Madrid, 840 cells in 84 buildings did not complete and were not repaired. Three courtyard
> buildings in Bologna are outside what this subdivision method can simulate.

with:

> In Madrid, a separate build-time failure log records 840 cells (all ten diaries in each of 84
> buildings) that failed during EnergyPlus processing and were not repaired; this count is drawn
> from the campaign's own per-building failure record, not from the planned-versus-completed cell
> totals given above, and the two have not been fully reconciled. Three courtyard buildings in
> Bologna are outside what this subdivision method can simulate.

For S12 (`4J_supplementary_material.md:620-621`), replace:
> In Madrid, 840 cells in 84 buildings did not complete, and three courtyard buildings in Bologna
> are outside the subdivision method.

with:

> In Madrid, a separate failure log for the campaign records 840 cells in 84 buildings that did not
> complete (not reconciled against the completed-cell totals in S9), and three courtyard buildings
> in Bologna are outside the subdivision method.

(No number was changed — only a clarifying clause added, since 840/84 is the verified figure and
170 is not a real measured quantity.)

## WHAT I DID NOT VERIFY

- The cause of the 670-cell gap between "10,670 implied surviving from the failure log's own
  11,510/840" and "11,340 actually completed per the JSON file count" — no reconciling file found;
  did not attempt to re-derive from raw run trees (`_local_runs/4J_ES_local/out/ES/cells/*.json`)
  since that would mean counting a live/large output directory not committed to this checkout in a
  way I could `wc -l`; this needs the author or a fresh employee task with access to that directory.
- Whether the Madrid "eligible building" count itself changed between the 2026-09-08 preflight
  (1,151 eligible, per `Step10_docs/impl/2026-09-08_C2-runner-built-refusals-seen-failing.md:1579`)
  and the final campaign — I did not find a later re-preflight document and did not compute this
  from raw data.
- Whether any of the 84 failed buildings were later fixed in a campaign the repo does not document
  (e.g. a run outside the tracked `Step10_docs/impl/` log). The val doc's "NO CELL WAS RE-RUN"
  statement covers only the interval between the failure log and the 2026-09-16 scoring pass, not
  any possible earlier repair.
- Did not re-derive Bologna/London completed-vs-planned gaps (30 and 0 respectively per
  `results_number_sheet.md:239`) against their own failure logs — out of scope of this task
  (Madrid only).
