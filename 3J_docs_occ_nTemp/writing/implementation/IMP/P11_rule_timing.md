# P11 — Retail rule timing and checkpoint-selection story

Scope executed: plan Section 5 "P11", steps 1 and 3. Read:
`improvements/v2/3rdJ_L3_v2_implementation.md`, `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md`,
`Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_gates.json`, `writing/fullSet/readySubmission.md` §3.2/§5.2.
Every claim below is quoted with file, line and date; "not found" is stated where the record does
not say.

## Dated order — retail median-in-band rule

1. **2026-08-03 to 2026-08-04 (evening) — the retail numbers that drove the decision already
   existed.** `improvements/v0/investigation/investigation_v2/3rdJ_L3_backward_audit_2026-08-04.md:5`
   header: "Opened: 2026-08-03 - Last updated: 2026-08-04 (evening)". Its finding text, `:176`:
   "`S9-EUI-retail` FAILs on two cells short of the 80.00 floor by 0.23% and 0.06%" — this is the
   "Arm R" run, 54/56 in band, referenced by name at
   `improvements/v2/3rdJ_L3_v2_implementation.md:567` and `:1894`. No earlier date for Arm R itself
   was found in the files searched (searched `improvements/v2/*.md`, no run date attached to "Arm
   R" beyond its use in this 08-04 finding); **not found** beyond "documented by 08-04 evening".

2. **2026-08-04 (night) — the rule was decided, and the record states plainly it was NOT
   pre-registered.** `improvements/v2/3rdJ_L3_v2_implementation.md:1892`, entry header "2026-08-04
   (night) - V2-B3 - The retail gate rule - DECIDED, with its weakness stated". The rule: "The
   median across the 56 cells must lie within the band" (`:1902-1903`). The document's own
   admission, `:1924-1928`: "**This rule was chosen with our numbers already known** — they are on
   the face of this plan. It is therefore **not pre-registered and is weaker evidence**, and the
   write-up must say so." Applying the new rule to the numbers on hand that night flips retail from
   FAIL (2/56 out) to PASS at a reported median of ~86.57 (table at `:1916-1922`), while leaving
   office FAIL under the same rule — offered as the "uniformity" defence (`:1922`, "It does not
   rescue office. A rule invented to erase failures would have.").

3. **2026-08-05 — the rule is implemented as code and pre-registered against a DIFFERENT (not yet
   read) file.** `improvements/v2/3rdJ_L3_v2_implementation.md:3477-3481` ("2026-08-05 - V2-D4
   PRE-REGISTRATION - written before any number was read"): "V2-B3 replaced the retail gate's
   56-of-56 rule with median-in-band. A rule that changes the verdict on the same data is
   indistinguishable from a band widening unless the prediction is fixed first. So it is fixed
   here, before `step9_eui_by_channel.csv` is opened." Code change at `:3525-3528`: "`rule` is now a
   per-channel field of `BENCH`" in `3rdJ_09_activityDrivenLoads_4split.py`, `"all_cells"` for
   office/hotel, `"median"` for retail. The shipped scorecard,
   `Leg3_4-split/Step9_docs/outputs_step9_deliverable/step9_gates.json:10-12`, records the same
   attribution: `"RULE = median-in-band (V2-B3, 2026-08-05)"`, and on THIS arm's numbers (median
   75.6, range 63.6-96.8) the gate still FAILs (`:11`) — the deliverable run's retail median (75.63)
   differs from the Arm R exploration median (~86.57) that motivated the rule change; the rule was
   pre-registered relative to the deliverable numbers but not relative to Arm R.

4. **Manuscript claim vs. the record — a discrepancy to flag, not resolve here.**
   `writing/fullSet/readySubmission.md:662`: "Retail fails under the gate rule actually in force,
   median-in-band rather than all-cells (**decided in advance of the numbers**)". This is true only
   for the frozen deliverable's own numbers (item 3 above); it is contradicted, for the numbers that
   actually motivated the rule choice (Arm R), by the project's own record at
   `3rdJ_L3_v2_implementation.md:1924-1928` ("chosen with our numbers already known ... not
   pre-registered"). The manuscript sentence should either drop "decided in advance of the numbers"
   or qualify it to the deliverable arm specifically; both are quoted above for the manager to
   choose.

Also found, previously in force: the retired all-cells rule and its sensitivity, cited at
`step9_gates.json:12`: "V2-E3 moved the median by -0.05% and that alone flipped a cell" — matching
`3rdJ_L3_v2_implementation.md:3442-3443`.

## Checkpoint selection and the 0.0218 Retail-F1 difference

`writing/fullSet/readySubmission.md:313-336` (§3.2) already carries this story in full and is
largely the target end-state for P11 step 3 (move to SI, one Methods sentence). Key facts as
currently written: the specified rule is "gate-first then lexicographic: discard every checkpoint
failing a hard gate, then maximize Retail F1 among survivors, with no composite score" (`:314-315`);
the shipped checkpoint was instead chosen by `val_score = mean(JS) + 0.5 * mean(three presence-rate
gaps)` (`:318-321`), "which contains neither PR-AUC nor F1"; "the shipped seed ranks first of five
on the composite and fourth of five on the metric the specification names, **0.0218 Retail F1**
below the specified rule's winner, 5.6% in relative terms and 0.16 standard deviations of the
cross-seed spread" (`:323-326`). Reasons given for not re-selecting (`:328-336`): both rules use
teacher-forced validation columns shown "blind to person-level Retail skill" by a separate
person-level probe, and the specified rule's hard-gate clause is inert on the observed range in any
case (worst epoch still clears every gate). No separate dated record of WHEN this checkpoint was
chosen was found in the files searched for this task (`improvements/v2/`, `Step9_docs/`); **not
found** — a P11-scoped follow-up would need to search the training-stage Progress Log directly.

## Plain-words rewrite, §5.2 rule sentence

Draft replacement for `readySubmission.md:662` first clause: "Retail is scored against its
reference band using the median of all 56 cells, not a pass/fail count of every individual cell.
That scoring rule was adopted after seeing an earlier run's numbers, not before, which the project
record states plainly; it was then locked in writing before the specific numbers reported here were
read, and it produces the same failing verdict as the count-of-cells rule would."

## One Methods sentence, checkpoint

"The delivered model was selected by a composite validation score rather than by the pre-specified
rule of gate-passing then highest Retail F1; on that specified rule it would rank fourth of five
seeds, 0.0218 Retail F1 (5.6%) below the top-ranked seed, a difference the paper does not treat as
decisive because both rules use validation columns shown to be blind to person-level Retail skill."
