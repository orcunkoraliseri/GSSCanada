# T89 — bring the reviewer response map up to date against the revised manuscript — implementation state

Task doc:   this file. Plan log (eg).
Status:     DONE
Agent:      fresh Sonnet employee, text only. No cluster, no web, no python.

## Goal
`../manuscript/prep/response_map.md` was built on 2026-09-15 and most Status/Where cells are stale.
Make every row say where and how the request is answered in the CURRENT manuscript, so the author
can later write the response letter from it.

## Inputs (read only, except the one output file)
- `../manuscript/prep/response_map.md` (the file you edit)
- `../manuscript/2J_manuscript_AE_revised.md` and `../manuscript/2J_SI_AE_revised.md` (source of truth
  for what is actually in the paper; use their section/figure/table numbers)
- `../00_REVISION_PLAN.md`: section 5 items 10 to 39 (carried findings) and the plan log entries from
  (ec) onward.
- `impl/*.md` Status lines only when a row names a task.

## Steps
1. For every row: re-check against the manuscript text (grep for the change, read it). Set Status to
   DONE (quote the section, figure or table where it now lands), PARTIAL (say what is missing),
   WAITING ON AUTHOR (only the three author-owed items: companion paper status, the two
   `[NUMBER FROM RESULTS]` counts in Section 1.5), or DECLINED (only where the plan records a rule).
   Update "Where in new manuscript" to real section numbers. Keep the Note short.
2. Add a section "## Carried findings (plan section 5, items 10 to 19)" with one row per item in the same
   columns: plain paraphrase, where the manuscript now handles it, status. If an item is not visibly
   handled in the manuscript, say PARTIAL or OPEN, do not invent a fix.
3. Do not edit the manuscript, the SI, or the plan. Do not write response-letter prose.
4. Rules for anything you write: plain words; no em or en dashes; never the word "failure" (say
   limitation); never quote "1.0-3.3" percent; do not copy reviewer sentences verbatim.
5. Update the file header line to "Updated 2026-09-21 by T89 against the revised manuscript."

## Output
The edited `../manuscript/prep/response_map.md`. Then fill Verified (row counts: DONE / PARTIAL /
WAITING ON AUTHOR / DECLINED / OPEN), Decisions, Next, WHAT I DID NOT VERIFY below, set Status DONE,
end the turn.

## Ledger
(no cluster jobs)

## Verified
- Read `manuscript/2J_manuscript_AE_revised.md` in full (1,154 lines) and `manuscript/2J_SI_AE_revised.md`
  in full (497 lines), plus `00_REVISION_PLAN.md` section 5 (items 10 to 39, lines 470 to 800) and the
  plan log from (ec) to (eg) (lines 4277 to 4303).
- Re-checked all 55 original response-map rows against the current manuscript text (grep plus direct
  reading), not against the old task-doc notes. Row-count tally after this pass: DONE 43, PARTIAL 10,
  WAITING ON AUTHOR 2, DECLINED 0.
- Added the "Carried findings (plan section 5, items 10 to 19)" section with 10 rows: DONE 9, OPEN 1
  (item 15, the 3x cohort-size question, is open on different numbers than when it was raised, because
  the household-frame rebuild changed the underlying counts).
- Confirmed by grep: "forecast" appears 4 times in the main manuscript (the title plus three negated
  uses, "not a forecast"), 0 times in the SI; "calibration closure" and "credibility anchor" 0 times;
  no em or en dash in the running text (only the title and reference page ranges); "1.0 to 3.3" percent
  0 times; the internal jargon strings "J3", "True-Future-Test", "FailSafe", "occACT", "DDAY_STRATA",
  "COLLECT_MODE" and "Tier-1" all 0 times in the main text.
- Confirmed by reading: Table 5 (the old EUI-versus-SHEU-range table) no longer exists anywhere in the
  rebuilt manuscript, which closes Q11 and Q13 by restructuring rather than by a targeted fix; the old
  "+2.2 to +3.9 pp" figure (item 17 / Q18) is gone and replaced by one consistent set of rebuilt numbers.
- Confirmed by reading: the reference list still prints "Sustainable Cities and Society, 76" for
  Motuzienė et al. (2022) (should be 77, Q21) and still truncates the Jalilian and Kamel (2025) title
  (missing its subtitle, Q22); neither fix has been applied yet.

## Decisions
- Split M1 from D1/D12: M1 asked for both a fixed-schedule arm and an average-profile arm; only the
  average-profile arm reached the Results (Section 3.5 states the fixed-schedule arm is excluded from
  the comparison), so M1 is PARTIAL while D1 and D12 (which only need the average-profile evidence) are
  DONE.
- Q11, Q12 and Q13 are marked DONE because the sentences and the table they were attached to (old
  Table 5, and the section 3.6 forward reference) no longer exist in the rebuilt manuscript, not because
  a targeted citation or wording fix was applied to them. Recorded as "resolved by restructuring" in the
  Note column so nobody mistakes this for a deliberate fix that could regress if a similar table returns.
- R2-3 (drop the word "forecast") is marked PARTIAL, not DONE and not DECLINED: the body text is clean,
  but the title still reads "Forecasting..." by the author's own explicit order (plan log (dz)), which is
  a standing decision, not an unfinished task. Noted plainly rather than silently upgraded to DONE.
- D19 and D20/R2-7 (figure prominence, ramp ordering, figure legibility) are PARTIAL. For D19, flagged a
  wording inconsistency between Section 2.10 ("No ramp metric is defined anywhere in the plotting code...
  none is reported here") and Section 3.4 (which then reports specific evening-ramp kilowatt values).
  This task recorded the inconsistency in the Note column only; it did not edit the manuscript to resolve
  it, per the task's own rule against editing the manuscript.
- Q15 (3x cohort size) is OPEN in the carried-findings table because the old counts it was built on
  (37,008 households, 12,336 diaries) do not appear anywhere in the rebuilt manuscript; the stock frame
  is now 144,465 households. The question was not re-derived on the new numbers, since that would be a
  new computation, out of scope for a text-only task.
- D13 (an at-home-versus-office-energy system-boundary limitation) is still PARTIAL; nothing was found
  anywhere in Section 4 or Section 5 addressing it, and no fix was invented.

## Next
- Author or a following task should close the two reference-list rows (Q21 volume number, Q22 full
  title) at the WP10/Step 13 reference-list assembly step the plan already calls for.
- Author to resolve the three WAITING ON AUTHOR items: the companion paper's publication status (Table 1,
  Section 1.4) and the two `[NUMBER FROM RESULTS]` placeholders in Section 1.5 (architectures searched;
  total simulation runs).
- A later pass should look at the Section 2.10 versus Section 3.4 ramp-metric wording inconsistency
  flagged under D19, and decide whether to add the D13 system-boundary limitation sentence.
- WP13 (venue and resubmission package) is next per plan log (eg).

## WHAT I DID NOT VERIFY
- Figure legibility and panel layout at print size (rows D20, R2-7): a visual check, out of scope for a
  text-only task; treated the same way the plan already treats Figure 1 legibility (plan item 23), the
  author's own eye.
- Whether the `.docx` builds match the `.md` source; only the Markdown source files were read.
- DOI or citation accuracy beyond what earlier vetting already recorded in the plan.
- The individual `impl/*.md` Status lines for every task named in the Evidence task(s) column; this task
  checked rows against the manuscript text directly, which is the source of truth the task doc asked for,
  rather than re-opening every task doc.
- Whether the three WAITING ON AUTHOR items have been answered since this read; they were open at the
  time this task read the files.
