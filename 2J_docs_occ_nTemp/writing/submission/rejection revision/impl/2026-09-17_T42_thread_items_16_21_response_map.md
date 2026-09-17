# T42 — thread plan §5 items 16-21 into response_map.md — implementation state

Task doc: employee prompt "2J revision EMPLOYEE (Sonnet) — T42", 2026-09-17. Purely local, no cluster,
no ssh, no jobs. Thread plan §5 items 16-21 (dr_2J-10/dr_2J-11 Fable + Gemini carried items, plus the
2026-09-17 reference re-verification) into `manuscript\prep\response_map.md`, continuing the numbering
after T39's Q10-Q16, matching that existing row format exactly. One file may be created (this doc); one
file may be edited (`response_map.md`).

Status: DONE

## Verified
- Read `00_REVISION_PLAN.md` §5 (lines 470-554), in particular items 10-21 (lines 482-538) and the
  routing notes at lines 540-548 (item 17 blocked on WP1; item 19 blocked on WP2; items 20-21 apply only
  at WP10's Step 13 reference-list assembly).
- Read plan Progress Log entry (br) (lines 1419-1426): confirms items 20/21 come from an independent
  2026-09-17 re-verification of all 52 references (50 clean, 2 real small errors, 0 fabricated) — there
  is no separate vetting file for this; the plan itself plus entry (br) is the source, and I cited both.
- Read the full existing `manuscript\prep\response_map.md` (94 lines) before editing, to match T39's
  Q10-Q16 row shape (8 columns: ID, plain paraphrase, class, what we change, where in new manuscript,
  evidence task(s), status, note) and its "Checked `<file>` in full: ..." note style.
- Read `deepResearch\dr_2J-10_dr2J-11_FABLE_VETTING.md` lines 47-138 for item 16 (Table 1 R2/M3:
  Chiou et al. 2011 scored X despite §1.5 calling it survey-grounded, Yin et al. 2024 scored check
  despite §1.2 saying it "stops at statistical analysis") and lines 55-241 for item 17 (Finding 5.1: two
  incompatible readings of "+2.2 to +3.9 pp", re-derived and confirmed).
- Read `deepResearch\dr_2J-10_VETTING.md` lines 35-246 for item 18 (Chen et al. 2022 scores 5 of 6
  columns, missing only C3; Table B "Total Y" undercounts 12 of 25 rows, corrected counts in section 7).
- Read `deepResearch\dr_2J-11_VETTING.md` lines 103-236 for item 19 (post-2022 WFH decline: Canada 22.4%
  to 20.1% to 18.7%; US SWAA 30.4% to 28.7% to 27.6% to 25.9%; the "7.1%" 2016 figure not confirmed
  against its StatCan source page).
- Opened all four existing redrafts and grepped each for the relevant terms (Table 1 novelty columns,
  Chiou, Yin et al., C3, Chen et al., "2.2 to 3.9", "persists with probability", reversion, Motuzienė,
  Jalilian, novelty):
  - `draft_S2_framework.md` — has its own, unrelated "Table 1. Datasets and their role in the framework"
    (D8's dataset-role table, line 15); no match on any of the six items' actual content.
  - `draft_S7_limitations.md` — no match on any of the six items.
  - `draft_SI_model_selection.md` — no match.
  - `draft_SI_schedule_completion.md` — no match.
  None of the four existing redrafts touch the Introduction (Table 1 novelty matrix), Abstract, Results
  §3.4/§5.1 (2030 figure), Results scenarios (WFH reversion), or the Reference list — those sections have
  no draft file to check at all, so none of the six items can be ALREADY FIXED.
- Added six new rows, Q17-Q22, to the "Quiet fixes and new items" table in `response_map.md`, immediately
  after the existing Q16 row, before "## Manager check". Table not restructured; no existing row renumbered.
- Updated the "## Coverage check" paragraph: 49 rows -> 55 rows (42 reviewer rows + 13 quiet fixes:
  Q10-Q16 (7) + Q17-Q22 (6)).
- Mapping used: Q17 = plan item 16 (Table 1 column criteria / Chiou-Yin inconsistency, `dr_2J-10`/
  `dr_2J-11` Fable), Q18 = plan item 17 (+2.2 to +3.9 pp two readings, Fable Finding 5.1), Q19 = plan
  item 18 (Table 1 real gap / C3 / Table B undercounts, `dr_2J-10` Gemini), Q20 = plan item 19 (WFH
  reversion grounding, do not repeat "7.1%", `dr_2J-11` Gemini), Q21 = plan item 20 (Motuzienė volume
  76->77), Q22 = plan item 21 (Jalilian & Kamel truncated title). All six are traceable to a plan §5
  line or a named vetting-file line, cited in each row's "Evidence task(s)" cell.
- All six new rows marked status WAITING (the table's own controlled vocabulary is DONE/RUNNING/
  WAITING/DECLINED; ALREADY FIXED would be recorded as DONE, and none qualified):
  - Q17 (item 16): WAITING. No Introduction/Table 1 draft exists to check, so cannot be ALREADY FIXED.
    Not yet assigned its own WP task; Note names it as belonging alongside item 8 in WP10's Table 1
    rewrite (plan line 502).
  - Q18 (item 17): WAITING. No Abstract/Results/Conclusion draft exists. Explicitly blocked, not just
    unstarted: plan line 545 says WP1 must settle the level-vs-step decision before this can be written.
  - Q19 (item 18): WAITING. No Introduction draft exists. Feeds the existing D5 row (Chen et al.
    comparison paragraph) already in the Reviewer 1 table, so not a new WP, but no work has started.
  - Q20 (item 19): WAITING. No scenario text drafted. Explicitly blocked: plan line 545 says WP2 needs
    this for the reversion scenario's numeric range; same evidence family as existing R3-2/R3-4/M5/D17
    rows (T26/T29/T32), which are RUNNING for the scenario build itself but not yet for this grounding.
  - Q21 (item 20): WAITING. No reference list has been assembled yet anywhere in `manuscript\`. Note
    states explicitly this applies only at WP10's Step 13 reference-list assembly, and that the frozen
    submitted file in `submission\archive\` is never edited — confirmed by not touching that archive.
  - Q22 (item 21): WAITING, same reasoning and same explicit archive-file caveat as Q21.
  Result: 0 of 6 ALREADY FIXED, 6 of 6 OPEN/WAITING. This matches the task brief's expectation that most
  items would legitimately be OPEN or WAITING because no target manuscript draft yet covers these
  sections — not a gap to paper over.

## Decisions
- Used status value "WAITING" (not a literal "OPEN" or "ALREADY FIXED" string) in the table itself, to
  stay inside the response_map.md's own documented controlled vocabulary (top of file, line 6-7:
  DONE/RUNNING/WAITING/DECLINED) and match T39's Q10-Q16 precedent exactly, as instructed. The
  OPEN/WAITING/ALREADY FIXED distinction the task brief asked for is reported here in ## Verified
  instead: all six are OPEN in the sense of "no work started, no WP yet owns it" except Q18 and Q20,
  which are WAITING in the stronger sense of "explicitly blocked on WP1 / WP2" per plan line 545 — I
  recorded that distinction in each row's Note cell so it is not lost.
- For items 20/21 (Q21/Q22), used the plan itself (§5 lines 529-538) and Progress Log entry (br) as the
  "source" citation, since no separate `deepResearch/` vetting file exists for the 2026-09-17 reference
  re-verification (confirmed by listing `impl\` and `deepResearch\`; only T40/T41 vetting docs from
  2026-09-16 exist there, covering dr_2J-10/dr_2J-11, not the reference re-verification).
- Did not touch the "## WHAT I DID NOT VERIFY" section at the bottom of `response_map.md` — the task
  brief only asked to add rows and match the existing format; that section is a whole-map disclosure,
  not scoped to this task, and editing it risked drifting outside "match the existing format exactly."

## Next
- When WP10 drafts the Introduction and its Table 1, action Q17 and Q19 together (both touch the same
  table) alongside the existing item-8/item-16 novelty-matrix rewrite.
- When WP1 settles the level-vs-step decision for "+2.2 to +3.9 pp", action Q18 across Abstract/§3.4/
  §5.1/Conclusion in one pass (four places, per plan line 504).
- When WP2 builds the reversion scenario, action Q20 using the Canada/US SWAA numbers already quoted in
  the row; do not carry forward the "7.1%" 2016 figure.
- When WP10 assembles the reference list at Step 13, action Q21 and Q22 together (both are reference-list
  corrections); do not edit `submission\archive\` under any circumstance.

## WHAT I DID NOT VERIFY
- Did not re-run or re-derive the Crossref/DOI checks behind items 16-21 myself; I read and cited the
  existing vetting files' own re-derivations (`dr_2J-10_dr2J-11_FABLE_VETTING.md`, `dr_2J-10_VETTING.md`,
  `dr_2J-11_VETTING.md`) and the plan's own account of the 2026-09-17 reference re-verification, rather
  than independently re-checking Motuzienė et al.'s real volume or Jalilian & Kamel's real title against
  Crossref myself — this is a local, no-external-lookup task, and the plan already records those as
  independently checked.
- Did not check whether any WP task doc (T05-T41) other than the four listed redrafts contains language
  that pre-empts these six items; the task brief named exactly four files to check for ALREADY FIXED, and
  I checked only those four, plus grepped the plan itself for routing context.
- Did not verify Table 1's actual current text (no such draft exists), so I cannot confirm whether the
  current, unwritten Table 1 rewrite (once WP10 starts it) will in fact need every one of the specific
  fixes named in Q17/Q19 — only that no fix exists yet anywhere in `manuscript\`.
