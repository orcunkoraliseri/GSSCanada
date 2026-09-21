# T78 — WP10 first task: new title + Section 1 (Introduction) — implementation state

Task doc:   this file. Plan: `../00_REVISION_PLAN.md` §3 WP10 (lines ~355-400), §2 triage rows, §5 items
            10, 16, 17, 18, 19 (Table 1 / Chen / 2030 definition / WFH trend). Map: `../manuscript/prep/response_map.md`.
Status:     DONE
Agent:      fresh Sonnet employee, text only. **No cluster, no compute, no literature search.**
Venue:      Applied Energy (author, 2026-09-15). Format limits are read at WP13, not now; aim for an
            Introduction of about 1,300-1,700 words (the archived one is longer; shorter is the point).

## Output
Write `../manuscript/draft_S1_introduction.md` (new file). It holds, in order:
1. **Title** — scenario-projection frame, no word "forecast". Start from the plan's candidate
   ("From 'how much' to 'when': occupancy-driven change in the Canadian residential load shape after
   COVID-19, with work-from-home scenarios to 2030") and offer it plus at most two alternatives; the
   author picks.
2. **Section 1. Introduction**, conventional order: background -> existing work -> gap -> objectives ->
   contributions. Then the end-of-file blocks listed under "Required trailer".

## Source text
- Start from `../../archive/2J_manuscript_submission.md` lines 57-132 (old §1.1-1.5). **Read only; the
  archive is frozen, never edit it.** Copy what still holds, rewrite the rest.
- Framework section already drafted: `../manuscript/draft_S2_framework.md` — use ITS names for stages and
  its section numbers (2.1-2.12) when the Introduction points forward. Do not contradict it.
- Limitations already drafted: `../manuscript/draft_S7_limitations.md`.
- Plain-term list: `../manuscript/prep/jargon_inventory.md` — no internal label may appear in the text
  (J3, True-Future-Test, paired frozen-frame, Tier-1/2/3, COLLECT_MODE, DDAY_STRATA, Step-8/9, occACT).

## Reviewer items this section must close (tick each in the trailer with the paragraph that closes it)
- R2-5: delete the "this introduction proceeds as a funnel" meta-paragraph. No self-description of the
  section's own structure anywhere.
- R2-3 / R3-2: no "forecast" anywhere; say "scenario-based projection". R3-3: no causal wording — "change
  associated with the pandemic and work from home", never "caused by".
- R1-D3: define C-VAE (conditional variational autoencoder) at first use. R1-D4: define "activity and
  end-use resolved" in one plain sentence at first use.
- R1-D6: one paragraph on why *when* energy is used matters (grid peak, evening ramp, demand response)
  and why 2030 (next survey cycle / planning horizon). **Any sentence that needs an outside source you
  do not already find cited in the archive gets `[CITATION NEEDED: <what>]` — never invent one.**
- R1-D5 + plan item 18 (Q19): one explicit paragraph on how this work differs from Chen et al. (2022),
  naming the ONE axis that separates it (future / post-COVID scenario column, C3). Do not claim the gap
  is wider than that. Facts about Chen: `../deepResearch/dr_2J-10_VETTING.md` §7.
- R1-D2: Table 1 gains rows for the authors' own prior work. The companion JBPS paper's publication
  status is NOT known — add its row marked `[STATUS TO CONFIRM BY AUTHOR]`.
- Plan item 10 (Q10): Motuzienė et al. (2022) row must not tick "forecast to future year" (or soften the
  citing sentence) — see `../deepResearch/dr_2J-12_VETTING.md`.
- Plan item 16 (Q17): write explicit scoring criteria for every Table 1 column (a short footnote per
  column), and score Chiou et al. (2011) and Yin et al. (2024) by that one rule.
- Plan item 17 (Q18): the Introduction must NOT state any 2030 number. Only qualitative aims.
- Plan item 19 (Q20): do not state that work from home persists unchanged; do not use the "7.1%" 2016
  figure. If the post-2022 decline is mentioned, use only the figures quoted in `../deepResearch/dr_2J-11_VETTING.md`
  and cite as that file names them.
- R1-D7: contributions rewritten as 2-3 scientific + 2 practical statements, plain words, no pipeline
  jargon, no numbers that have not been re-derived (put `[NUMBER FROM RESULTS]` placeholders instead).
- Plan item 13/14 spirit: never describe the SHEU comparison as validation — it is a fitted-target check.

## Rules
- Plain words. No em or en dashes (use commas, colons, or "to"). No symbols +, ±, ~, Δ in prose.
- **No number enters this section unless it is copied from a file you name in the trailer's number
  trace.** Numbers from the archive may not be carried over without a named source; placeholder instead.
- Citations: keep only references the archive already cites (list them in the trailer); new needs go to
  `[CITATION NEEDED: ...]`. No web search, no deep research (that is external, author-run).
- Do not edit any other manuscript draft, the plan, or `response_map.md` — the manager threads those.

## Required trailer in the draft file
- `## Reviewer-item closure` — one line per item above: item, CLOSED / PARTLY / OPEN, paragraph.
- `## Number trace table` — every number in the section, its source file:line.
- `## Citations used` and `## CITATION NEEDED list`.
- `## Open for the author` — title choice, JBPS status, anything else only the author can decide.
- `## WHAT I DID NOT VERIFY`.

## Ledger
(no cluster jobs in this task)

## Verified
- Output written: `manuscript/draft_S1_introduction.md` (title block + three title options, Section 1
  Introduction 1.1-1.5, and all five required trailer sections).
- Section 1 body (title block through the end of 1.5, including Table 1 and its six column-criteria
  footnotes) is about 1,750 words by `wc -w`, above the 1,300-1,700 aim but well under the archived
  Introduction's roughly 1,960 words (`sed -n '57,132p' archive/2J_manuscript_submission.md | wc -w`).
  Recorded as a known miss in the draft's own WHAT I DID NOT VERIFY, not silently accepted.
- Automated grep confirmed, on the Section 1 body only: zero occurrences of "forecast"; zero em/en
  dashes; zero of the banned symbols `+ ± ~ Δ`; zero occurrences of any jargon-inventory term (J3,
  True-Future-Test, frozen frame, Tier-1/2/3, FailSafe, COLLECT_MODE, DDAY_STRATA, Step-8/9, occACT,
  "gate"/"gates").
- Exactly 3 `[CITATION NEEDED: ...]` markers in the body (1.1 x2, 1.3 x1), matching the trailer's
  "CITATION NEEDED list" total.
- All 14 reviewer/plan items listed in this task doc are marked CLOSED in the draft's own
  "Reviewer-item closure" table, each pointing at the specific paragraph or footnote that closes it.
- Table 1's Motuzienė row corrected (C3 no longer ticked, footnote c explains why) and one combined
  row added for the authors' own prior work, the journal-manuscript component marked
  `[STATUS TO CONFIRM BY AUTHOR]` per R1-D2.
- No file other than the new draft and this task doc was edited. The archive
  (`archive/2J_manuscript_submission.md`) was read only, lines 57-132 plus the reference list context;
  never written to.

## Decisions
- Merged the two authors'-own-work rows the task doc implied (companion journal manuscript, companion
  conference study) into one combined Table 1 row to control length, since both share the same
  archived description and the same C1-C6 scores; the row text still names both works and the
  footnote paragraph explains the shared scoring. Flagged in the draft's own trailer.
- Did not insert the specific post-2022 work-from-home decline percentages found in
  `deepResearch/dr_2J-11_VETTING.md` §8 (Canada 22.4 to 18.7 percent, 2022-2024; a comparable US SWAA
  series), even though they are vetted and Crossref-checked, because they are not yet attached to a
  properly formatted citation the archive carries and because choosing Introduction vs. Discussion
  placement is a manuscript-design call. Used `[CITATION NEEDED]` instead and flagged this explicitly
  for the author/manager in "Open for the author."
- Dropped the archive's citation to Guo et al. 2026 (used there to support an unqualified WFH
  persistence claim) rather than reuse it for a claim the deep-research vetting found unsupported;
  recorded under "Citations used" in the draft as a deliberate omission, not an oversight.

## Next
Draft is DONE and ready for the manager's WP10 review. Two things need an author or manager decision
before this can move further: (1) pick one of the three title options (or ask for another), and (2)
confirm the JBPS companion manuscript's publication status so its Table 1 mark can be finalized. If the
~1,750-word length is judged too long once other sections are assembled, a further trim pass would need
to touch Table 1's footnotes or the transferability paragraph in 1.5, the two densest remaining spots.
