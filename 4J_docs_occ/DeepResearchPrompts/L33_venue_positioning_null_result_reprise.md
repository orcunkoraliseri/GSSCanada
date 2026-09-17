# L33. Venue positioning, re-run for a null-result paper: AI/data-driven venue versus building-science venue, and where Software X fits

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.
Sections C and E used, same as `L14`.

## Why this prompt exists

`RL14` (2026-08-14) recommended *Energy and Buildings* as primary target and *Building and Environment*
as co-equal secondary, on the grounds that building-science venues already have LLM precedent while
machine-learning venues "do not prioritize building occupancy." That advice was written **before** the
paper's headline result was known. The manuscript as it now stands
(`writing/submission/4J_manuscript_submission.md`) is not a positive transfer-learning claim; it is a
**pre-registered, hardened null** — the raked-donor-pool baseline beats the fine-tuned model on every
band of every fold, by design of the pre-registration, and the paper's contribution has been relocated
to the method and the negative-result findings themselves (`4J_docs_occ/writing/4thJ_crossStep_analysis.md`).
A null result about an LLM's transfer failure is a different pitch than a positive occupancy-modelling
result, and it may fit a different shelf.

The author has separately ruled, this session, that the target should be **an AI/data-driven-methods
venue, not a broad energy-and-buildings journal** — the opposite of what `RL14` recommended — and named
one candidate to check by name: ***Software X*** (Elsevier), a venue the author has direct reviewing
experience with (a completed peer review, unrelated manuscript, confidential and out of scope here).
🔴 **Do not treat `RL14` as settled and do not treat the author's stated preference as settled either.**
This prompt asks for an independent re-assessment of both, against the paper as it now exists, not a
rubber stamp of either.

## What we need

### Item 1. Does the null-result framing change the venue calculus at all?

Answer directly, before anything else: does a paper whose finding is "the simple baseline beats the
fine-tuned model, and here is why that is itself informative" fit *better* or *worse* at an
AI/data-driven-methods venue than a positive result on the same topic would? Consider that some venues
explicitly welcome rigorous negative/null results (registered reports, replication-focused sections) and
some do not review them at all. Name which of the candidate venues below have any track record publishing
a paper whose headline finding is that a proposed method **failed to beat** a simpler baseline, and cite
the paper if one exists.

### Item 2. AI/data-driven-methods candidates, assessed on `RL14`'s own template

Use the same row format `RL14` used (scope fit, LLM/ML publication precedent — cite a real example if one
exists, typical review turnaround, article-processing charge and fee-waiver status under the Concordia
CRKN agreement if applicable, open-access policy, typical length/structure for a methods-heavy paper).

Candidates to check: *Energy and AI* (Elsevier), *Data-Centric Engineering* (Cambridge), *Machine
Learning: Science and Technology* (IOP), *Patterns* (Cell Press), *Expert Systems with Applications*,
*Applied Intelligence*, and *Scientific Reports* (Nature Portfolio, multidisciplinary, has a documented
null-result track record). Add any venue you find that is a closer fit than these six and say why. For
each, answer explicitly: has occupancy modelling, building-stock energy simulation, or a similarly
building-adjacent application ever appeared there? If never, say so as a risk (reviewer pool may not
know EnergyPlus or HETUS and could bounce the paper on domain grounds even if the method is sound).

### Item 3. Software X — assessed on content fit, not on the author's familiarity with it

Independently verify Software X's Aims and Scope from Elsevier's own guide for authors. Software X
publishes short papers (typically under 6 pages) whose primary deliverable is a **piece of original,
reusable software**, with the manuscript itself substantially a description of the software's design,
capability, and how to obtain and run it — not an empirical-findings paper reporting an experiment's
result. Confirm or correct that characterisation against the actual current guide for authors.

Given that characterisation: does the present manuscript, which reports a pre-registered null result from
a cross-country transfer-learning experiment (its main deliverable is a finding, not the code), fit
Software X's scope, or does it not? Answer plainly, do not hedge. Separately, and only if the answer above
is "does not fit": would a **short, separate** paper describing just the occupancy-generation pipeline
itself (the codebase, not this experiment's result) be a credible future Software X submission, and what
would that require (a public repository, a maintained release, documentation, a worked example) that this
project does not yet have? Answer this second question only for the record; it does not bear on where the
present manuscript goes.

### Item 4. Direct comparison and one recommendation

Weigh the AI/data-driven-methods candidates from Item 2 against `RL14`'s original building-science
candidates (*Energy and Buildings*, *Building and Environment*, *Applied Energy*), **as they stand now**,
for this specific paper (null result, LLM method, building-occupancy application, method contribution
already relocated to the pipeline and the findings). Give one direct recommendation: primary target and
one secondary, with the reasoning stated as a decision, not a survey. If the honest answer is that
`RL14`'s original recommendation still holds despite the null-result reframing, say that plainly — do not
manufacture a change just because this prompt asks the question differently. If the honest answer is that
the author's AI/data-driven preference is right, say that plainly too, and name which one candidate from
Item 2 is the strongest single fit and why.

## What NOT to do

- Do not re-litigate or second-guess the null result itself; it is pre-registered and closed. This prompt
  is about where the paper is submitted, not whether the finding is right.
- Do not invent a DOI, an impact factor, a review-turnaround figure, or a precedent paper. `NOT FOUND`
  beats a plausible guess, every time — same rule as every prior round in this series.
- Do not recommend a venue based on prestige or impact factor alone; scope fit and null-result precedent
  matter more here than in `RL14`'s original framing.
- No em dashes or en dashes anywhere in your answer.

---

## Registration

Written 2026-09-16, Wave 14. Not yet sent externally. When it returns, vet it under the seven-step
protocol (`DeepResearchPrompts/README.md`, "Vetting a returned report") before treating any of its
recommendation as settled, and record the vetting verdict as `VETTING_RL33.md`, same convention as
`VETTING_RL32.md`. Its verdict directly supersedes or confirms `RL14`; do not read `RL14` alone as current
guidance once `RL33` exists.
