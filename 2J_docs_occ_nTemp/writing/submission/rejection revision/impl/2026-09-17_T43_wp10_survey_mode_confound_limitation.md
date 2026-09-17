# T43 — add the CATI-to-EQ survey mode confound as an eleventh limitation

Task doc: employee brief "2J revision EMPLOYEE (Sonnet) ... Add the survey-mode confound as the
eleventh limitation in `manuscript\draft_S7_limitations.md`", received 2026-09-17. Purely local,
no cluster, no new computation, no web search (deep research is external).

Status: DONE

## Verified

**Limitation count before and after.**
- Before: `manuscript\draft_S7_limitations.md:3` read "This work has ten limitations. The first seven
  bear directly on the results reported above; the last three are disclosed here although no reviewer
  raised them." Counted the section body: 7 individually-bolded paragraphs (Scope; before/after pool
  mismatch; one envelope; at-home level high; weekend harder to reproduce; 2030 scenario not forecast;
  Saturday/Sunday pooled) + 3 items bundled inside the "Three further limitations" paragraph (TMY
  weather; census-GSS conditional-independence assumption; metabolic heat not independently calibrated)
  = 10. The stated count (ten) already matched the actual list before this task touched it — unlike the
  two prior wrong counts the brief warned about (previously said six against nine listed).
- After: added one new bolded paragraph (the CATI-to-EQ confound), making 8 individually-bolded
  paragraphs + the same 3 bundled items = 11. Updated the opening sentence at
  `manuscript\draft_S7_limitations.md:3` to "This work has eleven limitations. The first eight bear
  directly on the results reported above; the last three are disclosed here although no reviewer
  raised them." Re-read the edited file after the change to confirm the count of bolded lead sentences
  is 8 before the "Three further limitations" paragraph and 3 inside it (11 total).

**Trace row added.** New row id `9` added to the claim trace table in
`manuscript\draft_S7_limitations.md`, citing:
- `00_REVISION_PLAN.md:550-558` — the plan's own "New, currently unassigned work" paragraph in §5,
  which states the confound, the `COLLECT_MODE` flag logic (0 for 2005/2010/2015, 1 only for 2022),
  and that it is "a real confound the manuscript does not currently rule out or disclose. Needs a
  limitations paragraph at minimum (candidate: WP10 Discussion/Limitations)."
- `deepResearch\dr_2J-12_VETTING.md:127-132` — the vetting file's "strong convergence" section 4, item 2:
  both the Gemini and Fable returns independently flagged the mode change; Gemini supplies outside
  survey-methodology literature for why self-administered diaries can report more at-home time; Fable
  supplies the internal `COLLECT_MODE` flag fact. Quote used directly: "Neither report alone would be
  as strong; together they show a real confound the manuscript does not rule out."
- `deepResearch\dr_2J-12_VETTING.md:195-197` — the CARRIED list entry: "CATI-to-EQ collection-mode
  confound with the COVID break (Gemini item 8, Fable S2/4.3). Verified real in both directions
  (outside literature plus internal flag logic); not currently addressed by WP1 or WP5 ... so this is
  new, unassigned work."
- `deepResearch\dr_2J-12_VETTING.md:39` also confirms the manuscript's own section 2.1 already names the
  CATI-to-EQ mode transition at 2022 as a fact (Gemini item 8, quote-verified against the archived
  submission), i.e. the transition itself is not new information, only its status as an undisclosed
  confound with the pandemic break is new.
No number was re-derived; per the brief, the vetting file's already-verified basis was used as-is and
no web search or manuscript re-read of §2.1 was performed (not required by the brief, and out of scope
for a purely local, no-search task).

**Overlap check against the existing ten.** Read all ten existing limitation paragraphs in
`manuscript\draft_S7_limitations.md` before adding the new one. None of the ten names the CATI-to-EQ
mode change or a survey collection-mode confound. The one paragraph that comes close is limitation 6
("The 2030 results are a scenario, not a forecast"), which says the 2030 shift is fitted "to real
respondents from 2005, 2010 and 2015 (the years before the survey was disrupted)" — this phrase gestures
at some kind of 2022 disruption but never names the mode change, never states it as a confound with the
pandemic break, and never says the design cannot separate the two effects. This is not a duplicate.
Action taken: did not merge; added the new item as its own paragraph, and added one explicit
cross-reference sentence inside the new paragraph pointing back at "the 2030 scenarios above" rather
than repeating limitation 6's content, so the two paragraphs each carry their own claim without
overlap.

**Source lines for every factual claim in the new paragraph.**
- "collected by telephone interview" for 2005/2010/2015 and "self-administered electronic
  questionnaire" starting 2022 — `deepResearch\dr_2J-12_VETTING.md:127-132` ("Survey collection-mode
  change (CATI to EQ)") and `00_REVISION_PLAN.md:550-558` (`COLLECT_MODE` flag description); CATI
  (computer-assisted telephone interviewing) and EQ (electronic questionnaire) are the vetting file's
  own shorthand, expanded here into plain words per the file's existing style.
- "`COLLECT_MODE` is 0 for 2005/2010/2015, 1 only for 2022" — `00_REVISION_PLAN.md:550-558` and
  `deepResearch\dr_2J-12_VETTING.md:130-131`, both stating this exact flag logic.
- "the two changes cannot be told apart with these data" / "the model cannot separate mode from
  behaviour" — `00_REVISION_PLAN.md:552` and `deepResearch\dr_2J-12_VETTING.md:131`, same wording.
- "outside survey-methodology literature reports self-administered modes can change recorded at-home
  time on their own" — `deepResearch\dr_2J-12_VETTING.md:128-129` ("Gemini supplies outside
  survey-methodology literature for why self-administered diaries report more at-home time"). Not
  re-derived or re-searched; attributed to the vetting file's characterization of Gemini's cited
  literature, not asserted as this session's own finding.
- "does not overturn the direction of the result ... independently supported by the wider pandemic
  literature" — this is the paragraph's own limiting statement, phrased to avoid overclaiming in either
  direction per the brief ("do not claim the mode change explains the jump"); it does not cite a new
  number, only states that the qualitative pandemic-related direction is not in dispute, consistent with
  `00_REVISION_PLAN.md`'s framing throughout (the plan never proposes reversing the qualitative finding,
  only correcting its provenance and framing, e.g. WP1/WP10).
- "the 2030 scenarios above ... extend a trend fitted partly across this same 2015-to-2022 boundary" —
  cross-reference to the existing limitation 6 paragraph already in the file
  (`manuscript\draft_S7_limitations.md`, "2030 results are a scenario" paragraph), which states the 2030
  shift is "eight times a linear trend fitted to real respondents from 2005, 2010 and 2015"; the new
  paragraph does not add a new number here, only points at the existing one.

## Decisions
- Placed the new paragraph after "Saturday and Sunday are simulated as one day" and before "Three
  further limitations, not raised by reviewers but disclosed here," so it sits with the reviewer-facing
  group rather than being folded into the reviewer-unraised bundle.
- Classified the new item as reviewer-adjacent (one of the "first eight," not the "last three, no
  reviewer raised them") because Reviewer 3's request 3 in `00_REVISION_PLAN.md` ("Distinguish more
  carefully between... post-pandemic/WFH-associated change and causally attributable COVID/WFH effect"
  → Action: "list other concurrent changes as a limitation") is the closest existing reviewer hook, and
  the survey mode change is exactly such a concurrent change. This is a judgement call the task brief
  left open; flagged here and in the file's own Decisions section rather than silently assumed.
- Did not claim the mode change explains the at-home jump. The paragraph states plainly that the design
  cannot separate the two effects and that neither cause can be ruled in or ruled out from the data used
  here, per the hard rule against overclaiming in either direction.
- Also appended a short dated note to `manuscript\draft_S7_limitations.md`'s own Decisions section
  (labelled "T43, 2026-09-17 addition") documenting the same count change, overlap check and
  classification call, since that file already carries its own append-only Ledger/Verified/Decisions
  record for prior tasks and the brief permits editing (not creating) that existing draft.

## Next
- None from this task. The eleventh limitation and its trace row are in place; the opening count
  matches the list. If a later task reclassifies the item (e.g. moves it into the "no reviewer raised
  them" bundle), the opening sentence's "first eight" / "last three" split must be re-checked again at
  that time.
- WP10 manuscript assembly should confirm this section's paragraph count against whatever numbering
  convention (if any) is used once S7 is merged into the full draft.

## WHAT I DID NOT VERIFY
- Did not re-open the archived manuscript's own section 2.1 to confirm in this session that it names
  the CATI-to-EQ transition; relied on `deepResearch\dr_2J-12_VETTING.md:39`'s statement that this quote
  was already checked verbatim against the archived submission. Per the brief, re-deriving this was out
  of scope (use the vetting file's basis, do not re-search).
- Did not verify the underlying outside survey-methodology literature Gemini cited (title, DOI, or
  content) — the brief instructs using the vetting file's already-verified basis rather than opening
  external sources; the vetting file itself (`dr_2J-12_VETTING.md`) does not print the specific
  citation(s) for this literature, only that Gemini supplied it and that the internal flag-logic side
  was independently confirmed by Fable.
- Did not check whether T39's earlier task (`impl/2026-09-16_T39_wp10_dr2j12_carried_items_threading.md`,
  which threads plan §5 items 10-15 and the confound into `manuscript/prep/response_map.md`) already
  drafted overlapping limitations-section language; this task only touched
  `manuscript\draft_S7_limitations.md`, not `response_map.md`, and did not cross-check the two for
  consistency.
- Did not verify whether the abstract, highlights, or Fig. 6 caption (flagged elsewhere in
  `00_REVISION_PLAN.md` §5 as also needing the WFH-attribution caveat, assigned to WP1 + WP10) have been
  updated to reflect this confound; this task's scope was the limitations section only.
- Did not re-verify the `COLLECT_MODE` flag logic against the pipeline code itself; took it from the
  plan and vetting file's own stated fact, consistent with the brief's instruction not to re-derive.
