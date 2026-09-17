# Deep-Research Prompt dr_2J-12 (Fable version): close-reading pre-submission review, no external search

> SCOPE GUARD, READ FIRST. Assume you have no live web access and your training data may be stale or wrong
> for anything published after your cutoff. Your job here is close reading, not fact-finding: logic, internal
> consistency, statistical soundness, and what a skeptical reviewer would flag in the text as given. Do not
> state or imply that you checked a citation, a number, or a claim against an outside source — you did not.
> Anything you are not sure of, mark UNCERTAIN rather than asserting it.

---

## Context (so you can judge fit, not so you repeat it back to us)

The paper generates household occupancy and activity schedules from a national time-use survey with a
trained generative model, links them to census households, builds scenario schedules for a future year
(2030) crossing the COVID-19 work-from-home change, and runs them through EnergyPlus for four dwelling
archetypes across six Canadian climate zones. The main result is hourly residential load shape (peak hour,
load factor, midday share, by end use), compared against simple fixed schedules and against measured hourly
utility data. It was rejected once already at a different venue (reasons are confidential and are not
reproduced here) and is being revised for **Applied Energy**.

The full manuscript text is pasted below this prompt (or attached) by the person running you. Do not evaluate
without it — if no manuscript was provided, say so and stop.

---

## What to do

1. **Argument map.** State the paper's central claim in one sentence, then list every sub-claim that has to
   hold for the central claim to survive. For each sub-claim, quote the sentence(s) in the manuscript that
   support it and say whether the support given in the text is sufficient, on its own terms, to carry that
   sub-claim.
2. **Internal consistency pass.** Check numbers, units, and terms against themselves across sections: does
   the abstract's number match the results section's number; does a figure caption match what the figure
   axis/legend implies; does the methods section actually describe what the results section reports doing;
   do the limitations in the discussion match weaknesses visible in the methods. List every mismatch found,
   quoted from both sides.
3. **Statistical and methodological soundness.** For each quantitative comparison (model vs. baseline, model
   vs. measured data, across climate zones or archetypes), check: is the comparison like-for-like (same
   period, same units, same normalization); is uncertainty or variability reported or silently dropped; is a
   difference described as meaningful without a stated basis for that judgment. Quote the relevant sentence
   for each finding.
4. **Structure and clarity.** Where would an editor's desk-reject or a reviewer's "unclear" land: sections
   that assert a result before the method that produces it is explained, terms used before they are defined,
   figures referenced before or without being described, claims in the abstract not mirrored in the
   conclusion. List each with a section/paragraph pointer.
5. **Reviewer-style critique.** After 1 to 4, write the critique a careful reviewer working only from the
   text (no outside lookups) would write: biggest weaknesses ranked by how likely they are to trigger
   rejection, each tied to a specific section/page/figure, not a generic complaint.

---

## Rules

- Do not claim to have verified a citation, a dataset, or an external fact. If a claim in the manuscript can
  only be judged by checking an outside source, mark it OUTSIDE MY SCOPE, not confirmed or refuted.
- Every finding must carry a quoted sentence and a section/paragraph pointer from the manuscript as given.
- Do not invent numbers, quotes, or section names that are not in the text provided.
- Do not suggest rewritten sentences for our paper; describe the problem, not the fix.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict, one line:** REJECT-LIKELY / MAJOR-REVISION-LIKELY / MINOR-REVISION-LIKELY, one sentence why.
2. **Argument map**, central claim plus each sub-claim with SUFFICIENT / INSUFFICIENT and the quoted support.
3. **Internal consistency mismatches**, quoted from both sides, with section pointers.
4. **Statistical/methodological findings**, one per issue, quoted, with section pointer.
5. **Structure and clarity issues**, one per issue, with section pointer.
6. **Ranked reviewer critique**, top 10 items, each with section/page/figure reference and severity
   (would-reject / would-request-major-revision / minor).
7. **What is OUTSIDE MY SCOPE**, in the first person, one line each — every place you would have wanted to
   check an external fact and could not.

Save the return as `dr_2J-12_whole_paper_review_fable_results.md`. It goes through the same 7-step vetting as
every other deep-research return before anything from it is acted on.
