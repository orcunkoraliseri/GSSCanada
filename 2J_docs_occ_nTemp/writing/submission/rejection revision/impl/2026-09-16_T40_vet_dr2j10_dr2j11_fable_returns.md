# T40 — vet the dr_2J-10 and dr_2J-11 Fable returns — implementation state

Task doc: this file (no separate prompt doc; instructions below)
Status:     DONE

## Task

Two deep-research returns came back today, both UNVETTED, both verdict "HAS A STRUCTURAL PROBLEM":
- `deepResearch/dr_2J-10_novelty_matrix_search_fable_results.md`
- `deepResearch/dr_2J-11_wfh_trajectory_and_tradeoff_fable_results.md`

Both are Claude Fable, no web access, close-reading audits of our own submitted manuscript
(`archive/2J_manuscript_submission.md`, 653 lines). Nothing from either return may be acted on
(no plan edit, no manuscript edit, no claim repeated to the author as fact) until vetted.

Follow the exact method used in `deepResearch/dr_2J-12_VETTING.md` (read it first, it is the
template). Since these are Fable no-search returns, not Gemini live-search returns, most of the
README's 7-step vetting list does not apply (no DOIs, no external sources, no journal-policy
quotes). What applies:

1. **Quote verification.** Both returns claim every finding carries a direct quote with a section
   pointer from the archived manuscript. Spot-check at minimum 15 quotes per report (more if time
   allows), including every quote used to support the top-line "STRUCTURAL PROBLEM" verdict and
   every item in the "Ranked reviewer critique" section. Open `archive/2J_manuscript_submission.md`
   and confirm each quote appears verbatim (or state exactly how it differs if it does not) at the
   cited section. Flag any quote that does not match, is paraphrased but presented as a quote, or
   whose section pointer is wrong.
2. **Arithmetic/consistency claims.** Both reports make claims that are checkable from the text
   alone without external knowledge (e.g. dr_2J-11 Finding 5.1's "if +2.2 to +3.9 pp is the level
   above pre-pandemic then 2030 sits below the 2022 level of +5.2 pp" — check this arithmetic;
   dr_2J-10's SC8 stock-scale N=50 per cell arithmetic). Re-derive each one from the quoted numbers
   and confirm it is correct arithmetic, not just correctly quoted.
3. **Cross-check against the plan and drafts.** Read `00_REVISION_PLAN.md` in full and the four
   partial redrafts in `rejection revision/manuscript/` (`draft_S2_framework.md`,
   `draft_S7_limitations.md`, and the two SI drafts). For every top-5 ranked critique item in both
   Fable returns, state whether it is: (a) already a known open item in the plan or already fixed
   in a redraft, or (b) genuinely new information not yet in the plan. Note: dr_2J-11's own final
   section already does part of this cross-check against `draft_S2_framework.md` and
   `draft_S7_limitations.md` — read it, then verify its claims about those two drafts yourself
   rather than trusting it, and extend the same check to dr_2J-10 (which has no such note) and to
   `00_REVISION_PLAN.md` for both.
4. **Positive-control-style sanity check.** dr_2J-10 M6 and dr_2J-11 Finding 5.6 both note overlap
   with prior dr_2J-12 findings (the Conclusion-item-1/Table-5 contradiction, the CI-bearing-deltas
   are 2022-to-2030-not-the-break point). Confirm these really do match what `dr_2J-12_VETTING.md`
   already recorded as CARRIED findings, or say if they diverge.

## Output

Write `deepResearch/dr_2J-10_dr2J-11_FABLE_VETTING.md`, same structure as `dr_2J-12_VETTING.md`:
what text was reviewed, quote verification results (which spot-checks passed/failed, with line
numbers), arithmetic verification results, the known-vs-new cross-check table for both reports'
top-5 critiques, and a final verdict per report: SURVIVES VETTING / PARTIALLY SURVIVES / DISCARD,
with one line why. No em dashes or en dashes anywhere in the output.

Then fill in this doc's Ledger/Verified/Decisions/Next/WHAT I DID NOT VERIFY sections below and
set Status to DONE. Do not edit `00_REVISION_PLAN.md` or any manuscript draft — that is the
manager's job once vetting is back.

## Ledger
- No cluster jobs. Read-only local vetting task, done in one session.
- Read in full: `deepResearch/dr_2J-10_novelty_matrix_search_fable_results.md` (151 lines),
  `deepResearch/dr_2J-11_wfh_trajectory_and_tradeoff_fable_results.md` (203 lines),
  `deepResearch/dr_2J-12_VETTING.md` (method template, 246 lines), `archive/2J_manuscript_submission.md`
  (654 lines, read in two chunks), `manuscript/draft_S2_framework.md` (421 lines),
  `manuscript/draft_S7_limitations.md` (135 lines).
- `00_REVISION_PLAN.md` (1312 lines): not read end to end; read via a keyword grep sweep (novelty,
  Table 1, C-VAE, persistence, WFH, system boundary, office, commercial, calibration provenance,
  scenario, Chen et al., matrix) plus three targeted `Read` calls covering lines 1-200 (reviewer triage
  and work packages), 460-529 (quiet-fix list and rules), and 1230-1320 (manager log entries
  commissioning and receiving both Fable returns).
- Output written: `deepResearch/dr_2J-10_dr2J-11_FABLE_VETTING.md`.

## Verified
- dr_2J-10: 21 quotes spot-checked against the archived manuscript by line number, plus all nine Table 1
  competitor rows checked cell by cell against the manuscript's own table (lines 79-87). 21/21 MATCH, 0
  FAIL. SC8 arithmetic (4 archetypes x 6 cities x 50 households/cell = 1,200) re-derived and correct.
- dr_2J-11: 19 quotes spot-checked against the archived manuscript by line number. 19/19 MATCH, 0 FAIL.
  Finding 5.1's two readings of "+2.2 to +3.9 pp" re-derived (3.9 < 5.2 under the level reading; 5.2+2.2
  to 5.2+3.9 = 7.4 to 9.1 under the step reading), both correct arithmetic. Finding 5.7's Table 5 pointer
  mismatch confirmed: Table 5 (manuscript lines 391-398) has no percentage-increment column.
- dr_2J-11's own closing note on `draft_S2_framework.md` section 2.7 and `draft_S7_limitations.md`:
  independently re-read and confirmed accurate in all three of its claims (the lambda-scenario
  definitions and "not a forecast" sentence in S2 section 2.7; the "scenario, not a forecast" sentence
  and absent system-boundary paragraph in S7; the new 8x-slope-vs-compositional-drift tension between the
  redraft and the submitted section 5.1).
- Both reports' top-5 ranked critique items cross-checked against `00_REVISION_PLAN.md`'s reviewer
  triage tables, work-package list, and "weaknesses the reviewers did not raise" list: full table in the
  output file section 3. Result: dr_2J-10 has 3 known items (R1, R3, R4-facts), 1 new item (R2), 1
  partially known item (R5); dr_2J-11 has 4 known items (1, 3, 4, 5) and 1 new item (2, the two
  incompatible "+2.2 to +3.9 pp" definitions).
- Positive-control check (task step 4): dr_2J-11 Finding 5.6's self-noted overlap with `dr_2J-12`
  confirmed correct against `dr_2J-12_VETTING.md` section 6. dr_2J-10's "M6" does NOT make an equivalent
  overlap claim in its own text; the task doc's step-4 description of "dr_2J-10 M6" appears to conflate
  dr_2J-10's own finding numbering with dr_2J-12 Fable's M1/M4/M9 labels. Flagged as a task-doc
  discrepancy, not a dr_2J-10 fabrication (see output file section 4).

## Decisions
- Followed `dr_2J-12_VETTING.md`'s structure but adapted section 2 (DOI spot-check) into an
  arithmetic/consistency-verification section, since these are no-search Fable returns with no DOIs to
  check, per the task doc's own instruction that "most of the README's 7-step vetting list does not
  apply" here.
- Did not open the two SI redrafts (`draft_SI_model_selection.md`, `draft_SI_schedule_completion.md`):
  neither report's top-5 items intersect with model-selection thresholds or weekend-completion
  mechanics, so nothing in this vetting pass depends on them. Recorded as a scoping choice, not a gap.
- Both reports get SURVIVES VETTING (no PARTIALLY SURVIVES or DISCARD): every checked quote matched, all
  arithmetic re-derived correctly, and both reports' own self-cross-checks (dr_2J-11's redraft note; both
  reports' overlap claims) held up under independent re-checking. Lower-confidence items (severity
  labels, dr_2J-10's "unfalsifiable by construction" framing, dr_2J-11's self-flagged-uncertain Finding
  5.4) were downgraded to "argument, not fact" within the SURVIVES verdict rather than triggering a lower
  overall verdict, matching how `dr_2J-12_VETTING.md` handled its own STRUCK/DOWNGRADED items.

## Next
- Manager to fold the genuinely NEW items into the plan: dr_2J-10 R2 (Table 1 has no stated column
  criteria; Chiou vs Yin inconsistently scored on "Calibrated behavioural model") into WP10's Table 1
  rewrite; dr_2J-11 item 2 (the "+2.2 to +3.9 pp" figure is defined two incompatible ways, level vs.
  step) into WP1, since it needs an explicit editorial decision before the recalibrated 2030 numbers are
  reported.
- Two Gemini returns (dr_2J-10, dr_2J-11) are still owed by the author; this vetting covers only the two
  Fable returns per this task's scope.
- Do not act on either Fable return's KNOWN items as if they were new to the author; they are already on
  the WP1/WP2/WP10/WP12 critical path per the cross-check table in the output file.

## WHAT I DID NOT VERIFY
- Neither report's characterization of any external study (the nine Table 1 competitors, Barrero et al.,
  Guo et al., Cicala) was checked against that study's actual content; both reports mark this OUTSIDE
  THEIR SCOPE themselves, and it is outside this task's scope too (that is the paired Gemini returns'
  job).
- Severity labels ("would-reject," "would-request-major-revision," "minor") on both reports' ranked
  items were not independently re-argued, only checked for whether the quotes underneath them are real.
- The two SI redrafts were not opened (see Decisions above).
- Figures, SI tables, and the companion C-VAE manuscript were not available as text and were not checked,
  the same gap both reports disclose themselves.
- The Fable findings not named in either report's top 5 or explicitly cited in the output file (most of
  dr_2J-10 sections 3 and 5; dr_2J-11's S1/S2/S8) were read in full but not individually re-verified
  quote by quote; a full read found nothing inconsistent with the manuscript text already checked, but
  this is a skim-level check, not an exhaustive one.
- Did not re-verify `00_REVISION_PLAN.md`'s own cited numbers (e.g. the 70.2%/78.5%/+8.3pp WP1 figures);
  used the plan's text only to classify known-vs-new, not to re-derive its own arithmetic, which is
  outside this task's scope.
