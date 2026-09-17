# Deep-Research Prompt dr_2J-10 (Fable version): close-reading audit of our own novelty argument, no external search

> SCOPE GUARD, READ FIRST. Assume you have no live web access and your training data may be stale or wrong
> for anything published after your cutoff. Your job is close reading of the manuscript text pasted below,
> not fact-finding: does our own novelty argument hold together on its own terms. Do not state or imply that
> you checked a citation, a competitor paper's actual content, or any external fact — you did not. Anything
> you are not sure of, mark UNCERTAIN rather than asserting it. Do not name, recall, or search for any study
> not already named in the text pasted below; if you find yourself about to cite a paper from memory, stop
> and write OUTSIDE MY SCOPE instead.

---

## Why this is a separate task from dr_2J-10's Gemini version

The Gemini version of dr_2J-10 uses live search to find a real published study that beats our novelty claim
(Table 1's six-dimension gap matrix). That is an external-fact task Fable cannot do reliably without search
— a no-search attempt at "find a paper that does X" would just invent plausible-sounding papers, which is
exactly the failure mode this project's deep-research vetting process exists to catch (the first round of
deep research done for this paper was about half fabricated). This version instead audits whether **our own
argument**, as written in the manuscript, is internally sound: does it contradict itself, does it overclaim
beyond what its own text supports, and is the six-column scoring scheme applied consistently to the
competitor studies it names.

The full manuscript text is pasted below this prompt (or attached) by the person running you. Do not
evaluate without it — if no manuscript was provided, say so and stop. Focus your reading on the
Introduction/novelty section (Table 1 and its surrounding paragraphs) and any other passage that discusses
prior work, but you may draw on the whole document for internal-consistency checks.

---

## The six columns our own scoring scheme uses (context, not manuscript text)

C1 time-series occupancy, C2 behaviour model grounded in survey data, C3 future year or scenario across the
COVID break, C4 activity and end-use resolved, C5 stock or multi-archetype scale, C6 load shape and peak as
the main result. (Defined in `dr_2J-10_novelty_matrix_search_gemini_prompt.md`, the companion live-search
task; not necessarily spelled out this way in the manuscript's own prose.)

---

## What to do

1. **Argument map.** State the paper's novelty claim (the "open cell" in the six-dimension gap matrix) in one
   sentence, quoting the manuscript. List every sub-claim that has to hold for it to survive (for example, a
   claim that a specific named competitor study lacks a specific dimension). For each sub-claim, quote the
   manuscript sentence that supports it and say SUFFICIENT or INSUFFICIENT **on the text's own terms** — do
   not judge whether the characterization of any competitor study is factually correct, since that requires
   reading that study (OUTSIDE MY SCOPE, that is the Gemini version's job); judge only whether the
   manuscript's own reasoning is internally coherent and not overstated relative to what it says elsewhere.
2. **Internal consistency pass.** Does the six-column scheme (or whatever informal version of it the prose
   uses) look applied consistently to every competitor study it names, or does the prose shift criteria
   between them? Does any "this paper does not re-claim X as novel" statement (for example, distinguishing
   this paper from the authors' own earlier related work) sit consistently with the six-column novelty claim,
   or does it risk describing two different, potentially overlapping novelty claims? Quote both sides for
   every mismatch found.
3. **Circularity and overclaiming check.** Is the scoring scheme constructed so specifically to this paper's
   own design that, by definition, only this paper (or something very close to it) could fill every column —
   i.e., is the novelty claim close to unfalsifiable by construction? A skeptical reviewer's standard
   objection to a "gap matrix" table is exactly this. State your judgment, with reasoning, not just yes/no.
4. **Structure and clarity.** Is the novelty claim asserted before or after the evidence that supports it is
   given? Does calling one study the "closest methodological precedent" sit consistently with also calling
   the paper's own cell "open" (none occupies it), or does "closest precedent" implicitly concede more
   overlap than "open cell" suggests? Quote both phrasings if both appear.
5. **Reviewer-style critique.** After 1-4, write the critique a careful reviewer working only from the text
   given (no outside lookups) would write about this novelty argument specifically: weaknesses ranked by how
   likely they are to trigger a "novelty not established" objection, each tied to a specific quoted sentence.

---

## Rules

- Do not claim to have verified that any named competitor study actually says what the manuscript attributes
  to it. Mark that OUTSIDE MY SCOPE every time it comes up.
- Do not invent, recall, or name any study not already named in the pasted manuscript. If a claim would
  require knowing what is or is not in the wider literature, mark it OUTSIDE MY SCOPE.
- Every finding must carry a quoted sentence and a section/paragraph pointer from the manuscript as given.
- Do not suggest rewritten sentences for the paper; describe the problem, not the fix.
- No em dashes and no en dashes in the report.

---

## Output format (follow exactly)

1. **Verdict, one line:** the novelty argument as written is INTERNALLY SOUND / HAS FIXABLE GAPS / HAS A
   STRUCTURAL PROBLEM, one sentence why.
2. **Argument map**, novelty claim plus each sub-claim with SUFFICIENT / INSUFFICIENT and quoted support.
3. **Internal consistency mismatches**, quoted from both sides, with section pointers.
4. **Circularity/overclaiming finding**, with reasoning.
5. **Structure and clarity issues**, one per issue, quoted, with section pointer.
6. **Ranked reviewer critique**, top 5 items, each with section pointer and severity (would-reject /
   would-request-major-revision / minor).
7. **What is OUTSIDE MY SCOPE**, in the first person, one line each.

Save the return as `dr_2J-10_novelty_matrix_search_fable_results.md`. It goes through the same 7-step
vetting as every other deep-research return before anything from it is acted on.
