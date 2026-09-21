# T82 — WP10: Section 4 Discussion + Section 6 Conclusion drafts — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP10, plan log (ds), (dt), (du) (BINDING).
Status:     DONE
Agent:      fresh Sonnet employee, text only. No cluster, no computation, no literature search, no web.
Venue:      Applied Energy.

## Outputs
1. `../manuscript/draft_S4_discussion.md`, about 1,200-1,600 words.
2. `../manuscript/draft_S6_conclusion.md`, about 350-500 words, prose (a short numbered list of
   findings is acceptable if each item is one or two plain sentences).
Section 5 is Limitations (`draft_S7_limitations.md`, already written; renumbered at assembly). Point to
it as "Section 5"; do not repeat its content, and do not contradict it.

## Sources
- **Numbers: only those already in `../manuscript/draft_S3_results.md`** (accepted with manager edits,
  entry (du)). Quote a number only if it appears there; cite the Results subsection it came from in the
  trace table. Never use a number from the archive.
- Framing: `../manuscript/draft_S1_introduction.md` (accepted, (dt)): aims and contributions. The
  Discussion answers the aim sentence in 1.5 and each contribution, in plain words.
- Limitations: `../manuscript/draft_S7_limitations.md`.
- Style reference only: archive `../../archive/2J_manuscript_submission.md` lines 433-450 (Discussion) and
  471-490 (Conclusion). Frozen, read only.
- Reviewer rows: `../manuscript/prep/response_map.md` (read; do not edit). Find every row whose target is
  the Discussion or Conclusion and close it or say why not.

## What the Discussion must do
1. Open with the answer: under the main scenario annual electricity is nearly flat, while the daily
   timing and the end-use mix move; the scenario spread (full reversion, partial, standardized
   reversion) is the main message about uncertainty, and only changes whose interval excludes zero
   are discussed as changes.
2. Say what this means for grid planning in plain words (midday share up, load factor up, peak and ramp
   point values only). Any outside claim: `[CITATION NEEDED: ...]` unless the archive already cites it.
3. The average-profile comparison: what the full model adds (household diversity in peak timing), and
   that the annual total differs less than the timing does.
4. The measured Toronto/Ontario check: where the simulated shape is close and where it is not (peak
   hour earlier than measured, peak-to-average lower); state it as a check, not a validation.
5. The survey end-use check is a check against a fitted target, never validation (plan item 14).
6. Lighting and equipment fall very slightly under the main scenario while at-home share rises: do not
   claim "more time at home means more plug load"; state the measured result.
7. Post-2022 work from home: the vetted evidence (`../deepResearch/dr_2J-11_VETTING.md`, only the figures
   it confirmed: 41.1 % April 2020 and 18.7 % May 2024 Canada) points to continued decline, so the
   partial and reversion scenarios are not less plausible than the main one. Mark the reference
   `[CITATION NEEDED: StatCan Daily, telework share]`; the author supplies it.
8. Position against Chen et al. (2022) on the one axis the Introduction names (future-year scenario),
   no wider claim.
9. Transferability: one short paragraph (other countries with a repeated time-use survey), consistent
   with Introduction 1.5.

## Conclusion
Findings (plain, numbers only from Results), the one practical message, and two or three future-work
items that match the limitations. No new claims. No "+2.2 to +3.9 pp", no "17.0-17.7 h", no "48/48
within 2.7 %", no EUI, no pre-pandemic energy numbers (all retired, entry (ds)). Pre-pandemic at-home
levels: `[NUMBER FROM T80]` only if you need them at all.

## Rules
- Non-causal wording ("associated with"); "scenario-based projection", never "forecast"; "limitation",
  never "failure"; no internal labels (J3, T-numbers, gate IDs, S-None etc. only in parentheses after a
  plain name); no em or en dashes; no +, ±, ~, Δ in prose.
- Edit no other file.

## Required trailer in each draft
`## Number trace table` (value, Results subsection), `## Reviewer items closed` (response_map row IDs,
paragraph), `## CITATION NEEDED list`, `## Open for the manager`, `## WHAT I DID NOT VERIFY`.

## Ledger
(no cluster jobs)

## Verified
- Read plan log (ds), (dt), (du) in full (`00_REVISION_PLAN.md:4092-4153`) before drafting; treated as
  binding per the task doc.
- Every number quoted in both drafts was read directly from `manuscript/draft_S3_results.md` (prose or
  its own Number trace table), not from the archive and not re-derived. Cross-checked each figure used
  against the exact wording in that file: main-scenario Facility change 0.1209 percent; S-None
  (full-reversion) 0.1225 percent fall; S-Partial 0.0117 percent (interval contains zero); S-Revert-std
  0.4408 percent fall; midday share 0.73 pp; load factor 0.49 pp; peak 47.207 to 46.332 kW; ramp 7.852
  to 7.768 kW; average-profile comparison 8,225.56 vs 8,951.40 kWh and circular standard deviation
  3.493 h vs 0.084 h (2022) / 3.255 h vs 0.053 h (2030); Toronto/Ontario measured check 0.3787 vs
  0.3513, 17.0 vs 18.69, 2.1367 vs 2.3231; SHEU/A5 48 of 48 cells, band plus or minus 15 percent;
  lighting -0.0157 percent, equipment -0.0066 percent; model-selection 4 candidates, 2 of 21 / 19 of 21
  threshold scenarios; clustering-aware interval widths (about 40 percent wider for midday share, about
  2 percent narrower for load factor).
- Read `draft_S1_introduction.md` in full: used Section 1.5's aim sentence and its three scientific plus
  two practical contributions as the structure the Discussion answers; used Section 1.2's Chen et al.
  (2022) C3-only differentiation; used Section 1.5's transferability paragraph as the basis for the
  Discussion's closing paragraph.
- Read `draft_S7_limitations.md` in full: confirmed no content is repeated or contradicted; used its
  scope (TMY weather, partial measured-check scope) to source two of the Conclusion's three future-work
  items.
- Read `manuscript/prep/response_map.md` in full (103 lines) and identified every row whose "Where in
  new manuscript" column names Discussion or Conclusion: M1, D1, D12, Q11 (Discussion); Q13, Q18, R3-1
  (Conclusion, shared with Results/Abstract). Closed each for the portion owed by this task; recorded in
  each draft's own "Reviewer items closed" section.
- Read archive `2J_manuscript_submission.md` lines 425-495 (old Discussion and Conclusion) for style and
  structure only; no number or claim from it was copied into either draft.
- Confirmed by direct search: neither draft contains the word "forecast", an em or en dash, or the
  symbols +, plus/minus, ~, or Delta in its body text (checked before the trailer sections). No banned
  internal label (J3, T-numbers, gate, S-None/S-Full/S-Partial/S-Revert-std, COLLECT_MODE, etc.) appears
  in either draft's body text; T-numbers appear only in each draft's own trailer sections (Open for the
  manager, WHAT I DID NOT VERIFY), which are not manuscript prose.
- Word counts (plain word count of body text only, above the horizontal rule): Discussion 1,481 words
  (within the 1,200-1,600 target); Conclusion 481 words (within the 350-500 target, after one revision
  pass that cut an initial 603-word draft and dropped a transferability paragraph judged redundant with
  the Discussion's own closing paragraph).

## Decisions
- Did not insert the post-2022 Canadian telework-share figures (41.1 percent, 18.7 percent) as bare
  numbers; tagged them `[CITATION NEEDED: StatCan Daily, telework share]` per the task doc's point 7,
  since the archive does not already carry a formatted citation for them.
- Kept the two grid-planning claims (why timing matters; why 2030) tagged `[CITATION NEEDED]` in the
  Discussion, matching the identical tags already left open in `draft_S1_introduction.md`, rather than
  inventing or reusing an unverified source.
- Used plain scenario names throughout both drafts (main scenario, full-reversion scenario,
  partial-persistence scenario, standardized-reversion variant) with no internal codes (S-Full, S-None,
  S-Partial, S-Revert-std) anywhere in body text, since the task's own point 1 describes the scenarios
  by plain name only and the codes were not needed for clarity.
- Cut the Conclusion's originally drafted transferability paragraph (present in the 603-word first pass)
  rather than shorten every other paragraph proportionally, since the same claim is already the closing
  paragraph of the Discussion draft and the task doc's Conclusion instructions ask only for findings,
  one practical message, and two or three future-work items, not transferability.
- Left the Conclusion's pre-pandemic at-home levels out entirely (no `[NUMBER FROM T80]` placeholder
  used), per the task doc's "only if you need them at all"; T80 (job 1341375, per plan log (du)) had not
  landed at the time of this task, and the five findings did not need those numbers to be complete.
- For each response_map row shared between Discussion/Conclusion and other sections (Q18, R3-1), closed
  only this task's portion explicitly in the draft's own trailer, and said in the same sentence that the
  Results/Abstract portions belong to other tasks, rather than marking the whole row closed.

## Next
Both drafts written and complete. Manager to: (1) supply the three CITATION NEEDED sources (grid-timing
rationale x2, StatCan Daily telework share) once available, matching them across
`draft_S1_introduction.md` and `draft_S4_discussion.md` consistently; (2) decide the three open items
listed in each draft's own "Open for the manager" section (model-selection paragraph placement, the
"may be closer to what actually occurs" ranking sentence, and whether a sixth Conclusion finding is
needed once T80 lands); (3) fold both drafts into assembly alongside `draft_S3_results.md` and
`draft_S7_limitations.md` (renumbered as Section 5) at Step 13.
