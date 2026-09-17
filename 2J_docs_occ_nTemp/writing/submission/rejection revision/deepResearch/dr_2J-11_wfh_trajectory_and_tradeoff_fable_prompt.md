# Deep-Research Prompt dr_2J-11 (Fable version): close-reading audit of our own WFH-scenario argument, no external search

> SCOPE GUARD, READ FIRST. Assume you have no live web access and your training data may be stale or wrong
> for anything published after your cutoff. Your job is close reading of the manuscript text pasted below,
> not fact-finding: does our own 2030 work-from-home scenario argument hold together on its own terms, and
> does the manuscript disclose what it does and does not cover about the home-versus-office energy trade-off.
> Do not state or imply that you checked any external number, survey, or study — you did not. Anything you
> are not sure of, mark UNCERTAIN rather than asserting it. Do not name, recall, or search for any external
> statistic or study not already in the text pasted below; if you find yourself about to cite a number from
> memory, stop and write OUTSIDE MY SCOPE instead.

---

## Why this is a separate task from dr_2J-11's Gemini version

The Gemini version of dr_2J-11 uses live search to find real published numbers on home-working trends to
2030 and the residential-versus-commercial energy trade-off. That is an external-fact task Fable cannot do
reliably without search. This version instead audits whether **our own argument**, as written in the
manuscript, is internally sound: is the single-scenario-versus-bracketed-range framing consistent across the
document, are the reported percentage-point figures used consistently, and does the manuscript disclose (or
silently omit) the fact that it only models residential energy while the work-from-home shift it describes
also has an office/commercial-energy side.

The full manuscript text is pasted below this prompt (or attached) by the person running you. Do not
evaluate without it — if no manuscript was provided, say so and stop. Focus your reading on every passage
that discusses the work-from-home scenario, the 2030 forecast, and its stated limitations, but you may draw
on the whole document for internal-consistency checks.

---

## What to do

1. **Argument map.** State the paper's central WFH-scenario claim in one sentence (what persistence
   assumption the 2030 forecast uses and why), quoting the manuscript. List every sub-claim that has to hold
   for it to be a defensible scenario design (for example: that a single high-persistence scenario is
   appropriate, or that the magnitude is bounded by a stated sensitivity analysis). For each sub-claim, quote
   the supporting sentence(s) and say SUFFICIENT or INSUFFICIENT **on the text's own terms**.
2. **Single-scenario versus range check.** The manuscript's own conclusion should be checked for whether it
   describes one scenario or a bracketed range. Quote every place the text calls the 2030 number a "forecast",
   a "projection", a "bound", an "upper bound", or a "scenario", and check whether these are used consistently
   or whether the manuscript sometimes reads as claiming more certainty (a single predicted number) than a
   one-sided high-persistence scenario can support. This matters because a reviewer explicitly asked for at
   least two work-from-home paths (stay-home versus partial return) rather than one trend, so check whether
   the text's own wording already anticipates that critique or is exposed to it as currently written.
3. **System-boundary disclosure check.** Search the pasted manuscript (do not search anything external) for
   any sentence that states, limits, or acknowledges that the paper models residential energy only, and that
   a rise in at-home energy may be offset (fully, partly, or not at all) by a fall in office or commercial
   energy that the paper does not model. Report exactly what you find, quoted, or report plainly that no such
   statement exists in the text provided. This is a factual presence/absence check of the pasted text, not an
   external-literature check.
4. **Internal consistency of the reported percentage-point figures.** The manuscript reports several distinct
   WFH-related magnitudes (for example a raw weekday shift, a demographically standardized shift, and a
   2022-to-2030 forecast range). Check whether these are used consistently every time they recur, whether any
   sentence conflates two of them, and whether the provisional/calibration-pending caveat (if the manuscript
   states one) is repeated everywhere the number is used or only in one place.
5. **Reviewer-style critique.** After 1-4, write the critique a careful reviewer working only from the text
   given (no outside lookups) would write about the WFH-scenario argument and system-boundary disclosure
   specifically: weaknesses ranked by how likely they are to trigger a scenario-robustness or
   undisclosed-limitation objection, each tied to a specific quoted sentence.

---

## Rules

- Do not claim to have verified any external number (Statistics Canada figures, SWAA figures, any cited
  study's actual content) against a source. Mark that OUTSIDE MY SCOPE every time it comes up — it is the
  Gemini version's job.
- Do not invent, recall, or state any external statistic not already quoted in the pasted manuscript.
- Every finding must carry a quoted sentence and a section/paragraph pointer from the manuscript as given.
- Do not suggest rewritten sentences for the paper; describe the problem, not the fix.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict, one line:** the WFH-scenario argument as written is INTERNALLY SOUND / HAS FIXABLE GAPS / HAS A
   STRUCTURAL PROBLEM, one sentence why.
2. **Argument map**, central claim plus each sub-claim with SUFFICIENT / INSUFFICIENT and quoted support.
3. **Single-scenario versus range finding**, quoted examples of each wording used, with section pointers.
4. **System-boundary disclosure finding**: quoted statement if one exists, or "NOT FOUND in the text
   provided" if none does, with a note on where such a statement would naturally belong (for example,
   Limitations).
5. **Percentage-point consistency findings**, one per mismatch, quoted, with section pointers.
6. **Ranked reviewer critique**, top 5 items, each with section pointer and severity (would-reject /
   would-request-major-revision / minor).
7. **What is OUTSIDE MY SCOPE**, in the first person, one line each.

Save the return as `dr_2J-11_wfh_trajectory_and_tradeoff_fable_results.md`. It goes through the same 7-step
vetting as every other deep-research return before anything from it is acted on.
