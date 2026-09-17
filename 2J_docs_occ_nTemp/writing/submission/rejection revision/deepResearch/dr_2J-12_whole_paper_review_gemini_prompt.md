# Deep-Research Prompt dr_2J-12 (Gemini version): adversarial pre-submission review with live search

> SCOPE GUARD, READ FIRST. You are a hostile Applied Energy reviewer with a search engine, not a
> collaborator. Your job is to find reasons to reject this paper, using your live web/search access to check
> claims against current literature. A finding that survives your own check is worth more than a compliment.
> Do not praise the paper in general terms, do not rewrite our sentences, and do not score anything you did
> not verify.

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

1. **Search-grounded novelty check.** Using live search, find every paper from 2024 to 2026 (not just the
   rows we may cite) that combines time-use-survey-based occupancy modelling, a future/post-pandemic
   scenario, and hourly residential load-shape results. For each: title, venue, year, DOI (verified on
   Crossref), and one quoted sentence showing what it does. State plainly if you find something that weakens
   our novelty claim.
2. **Citation audit.** Pick the 15 citations in the manuscript most load-bearing for its central claims
   (novelty, validation, methodology). For each, verify on Crossref or the publisher site that the DOI
   resolves, the title/authors/year match, and that the claim we attribute to it is actually in that paper
   (quote the sentence). Flag any mismatch, including a right paper cited for a claim it does not support.
3. **Venue fit.** Search Applied Energy's recent (2023 to 2026) published articles for the closest 5 matches
   in topic and method. State, with links, whether they used measured data for validation, whether the
   journal typically expects it for a load-shape claim, and whether our validation approach as described
   looks thin, adequate, or strong by comparison.
4. **Competing explanations.** For each of the paper's three or four headline numerical results (as stated in
   the abstract/conclusions), search for whether an alternative published explanation or a simpler baseline
   could plausibly produce the same pattern. Cite what you find.
5. **Reviewer-style critique.** After 1 to 4, write the critique an informed, skeptical reviewer would write:
   biggest weaknesses ranked by how likely they are to trigger rejection, each tied to a specific
   section/page/figure of the manuscript, not a generic complaint.

---

## Rules

- Every factual claim about the literature must be search-verified in this session, not recalled from
  training. If you cannot verify something, write NOT VERIFIED and say why, instead of asserting it.
- Verify every DOI on Crossref (`https://api.crossref.org/works/<DOI>`).
- `NOT FOUND` beats a guess. Do not invent papers, DOIs, or quotes.
- Do not suggest rewritten sentences for our paper; describe the problem, not the fix.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict, one line:** REJECT-LIKELY / MAJOR-REVISION-LIKELY / MINOR-REVISION-LIKELY, one sentence why.
2. **Table A, novelty check:** paper, DOI checked (yes/no), what it adds, why it does or does not weaken our
   claim.
3. **Table B, citation audit:** citation, DOI checked (yes/no), claim we make, CONFIRMED / MISMATCH / NOT
   FOUND, quoted evidence.
4. **Venue fit, with the 5 comparator papers and links.**
5. **Competing explanations**, one paragraph per headline result.
6. **Ranked reviewer critique**, top 10 items, each with section/page/figure reference and severity
   (would-reject / would-request-major-revision / minor).
7. **Search log:** queries used, number of hits screened, number opened.
8. **What I could not verify**, in the first person, one line each.

Save the return as `dr_2J-12_whole_paper_review_gemini_results.md`. It goes through the same 7-step vetting
as every other deep-research return before anything from it is acted on.
