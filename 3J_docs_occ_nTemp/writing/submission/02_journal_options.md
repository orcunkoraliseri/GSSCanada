
# Three journal options for the 3rd paper - a decision sheet

**Manuscript:** *From One Channel to Four: A Jointly-Trained Time-Use Occupancy Model for Mixed-Use
Building Energy Simulation (Canada, 2005-2030)*
**Prepared:** 2026-08-08 · **Status:** 🟡 **DECIDED 2026-08-08 - Building and Environment (Option D), and reopen trigger (b) FIRED the same day - see the block under Option D**
**Modelled on:** `2J_docs_occ_nTemp/writing/submission/02_journal_options.md`

> **DECISION.** Target venue is **Building and Environment** (Elsevier). Taken by the authors
> 2026-08-08 after the reversal described immediately below.
>
> **Reopen triggers, written now rather than after the fact:** (a) a B&E desk reject, which sends the
> paper to **Option A, JBPS** - by then the 1J decision will most likely have landed and removed the
> collision that demoted it; (b) evidence that the 0J rejection at B&E was about *quality* rather than
> scope, which is not recorded anywhere in this project and has never been looked up.
>
> **What this decision commits the manuscript to** is not optional and is listed in full under
> "My recommendation": the uninjected-control result leads the cover letter, the abstract's
> "not model error" sentence is not softened, and the introduction and §6.1 get a framing pass that
> puts the behavioural claim ahead of the architecture.

> **Sequence of the decision, 2026-08-08, recorded because the reversal matters more than the
> conclusion.** The authors first chose **Option B, Journal of Building Engineering**, on the sheet as
> it then stood. Two things then arrived within minutes and both undercut that choice.
>
> 1. The unattributed Building and Environment rejection was attributed to **0J**, which **unblocked a
>    venue the sheet had parked without assessing** (now Option D).
> 2. The authors stated that **3J is the strongest paper of the line**, which changes what the sheet
>    was optimising for. Option B was recommended to *avoid a collision*, not because the paper needed
>    a forgiving venue - and a collision-avoidance argument is much weaker when the paper is the best
>    one you have.
>
> **The recommendation below has been rewritten accordingly. Option B is no longer first.**

---

## Read this first - what this sheet is and is not built on

**No search was run to produce this sheet, and none of it comes from a deep-research report.**
Deep research in this project is external; the assistant's deliverable is a prompt, not an answer.
Everything below is built from two things only: what the manuscript on disk actually is, and facts
already recorded inside this project.

**There are no impact factors, CiteScores or acceptance rates in this sheet, on purpose.** The 2J
round learned that the hard way: `dr_2J-05` found that **roughly half the citations in the returned
reports were fabricated**, and that every journal metric came back identical to the claim it was
supposed to be auditing, with a journal homepage as the only source. A verification column that never
moves is not evidence. The 2J *ranking* survived that purge because it rested on scope fit and
manuscript effort. This sheet rests on the same two things, so that it survives the same test.

**🔴 The structural fact that did not exist when the 2J sheet was written: two of the three natural
venues already hold a manuscript from this author line.**

| paper | venue | status |
|---|---|---|
| 0J | Building and Environment, then Energy and Buildings | **rejected at B&E**, then published at E&B; E&B is **author-excluded going forward** after four revision rounds |
| 1J | Journal of Building Performance Simulation | **under review** |
| 2J | Building Simulation | **submitted 2026-08-07, under review** |
| 3J | *this decision* | - |

That is not a disqualification of either venue - authors publish repeatedly in one journal all the
time - but it changes the calculus for both, and it is the single most important input to the choice.
It is stated under each option rather than hidden in a footnote.

**🟢 The unrecorded Building and Environment rejection is now attributed, by the author, 2026-08-08.**
It was **0J** (`2J_docs_occ_nTemp/examples/JournalZero/`), the paper that was subsequently **published
in Energy and Buildings**. So the sequence was B&E reject, then E&B accept, then four revision rounds
at E&B - which is also the origin of the E&B author exclusion below.

**Two consequences, both of which simplify this sheet.** The rejection belongs to an older, different
manuscript, so **there is nothing for the 3J cover letter to disclose**. And Building and Environment
is not a hidden blocker; it is simply a venue that once rejected a different paper, which carries no
weight for 3J either way. The question that was blocking Option B's ranking is closed.

> 🔴 **The second clause of that sentence is now known to be too comfortable.** Later on 2026-08-08
> the authors also stated **why** 0J was rejected: **insufficient quality, not scope.** Nothing is
> still owed to the cover letter, so the first clause stands. But "carries no weight either way" was
> written while the reason was unknown, and the reason turned out to be the one that says something
> about the venue's bar. See **REOPEN TRIGGER (b) HAS FIRED** under Option D.

---

## What this paper actually is, stated plainly, because the venue follows from it

Three things, and the third is the one that picks the journal.

1. **A methods contribution.** One jointly-trained conditional Transformer with three GSS decoder
   heads (residential, office, retail) plus a non-GSS SARIMA side-track for hotel, and a per-Space
   Tag-2 exact-match dispatch that injects all four into PNNL Tall and SuperTall prototypes. 56 cells,
   Montreal 6A and Calgary 7A, 2005-2030.
2. **A mixed-use / tall-building contribution.** Four uses driven independently *inside one stacked
   tower*, rather than four separate single-use buildings.
3. 🔴 **A negative result about reference benchmarks - and this is the headline.** Three of four
   channel EUI gates FAIL. The office gate fails on an **uninjected `Default_NECB` control** (85.45
   against a floor of 100), with two candidate mechanisms tested and **both refuted 56/56**. The hotel
   gate splits into two prototype clusters 84.64 apart with the 300 ceiling sitting inside the gap.
   Retail's median sits 5.47 % below its floor. The paper reports all three **at full strength, with
   no band widened to pass them**, and argues they are findings about *band applicability to mixed-use
   towers*, not model error.

Point 3 is unusual and it is the paper's real value, but it is also a submission risk. **An editor
who reads "three of four validation gates failed" as a weak paper will desk-reject it; an editor who
reads it as a benchmarking finding will send it out.** The options below are ranked substantially on
which culture the journal has.

---

## Option A - Journal of Building Performance Simulation (Taylor & Francis, IBPSA)

**The case.** This is the venue whose readership is *built* to read point 3 correctly. JBPS publishes
validation and inter-model-comparison work where the finding is that a reference, a protocol or an
assumption does not hold, and it does not require a paper to end in a success. The gated validation
ladder, the uninjected control, the refuted-mechanism reporting and the "no band widened to pass"
discipline are all house virtues here, not apologies. The multi-head occupancy generator is also
squarely a BPS methods contribution rather than an energy-systems one, which is what it actually is.

**What it costs the manuscript.** Least of the three on the science. The framing already matches:
§6.2 and §6.4 are written as band-applicability arguments, which is the argument this readership
evaluates. Expect to expand the model-description detail (a BPS reviewer will want the Transformer
and the injection fully specified, closer to reproducible than to summarised) and to strengthen §6.3,
which currently concedes the hotel gate has little resolving power.

**🔴 The blocking consideration.** **1J is under review at this journal right now.** Two concurrent
submissions from the same authors, on consecutive legs of one pipeline, land in the same editor's
queue. That is legitimate, and the papers are genuinely different - but it must be **declared in the
cover letter, naming 1J and stating what is different**, and it is worth accepting that an editor may
hold one until the other clears. Do not discover this on the editor's side.

**The honest downside.** The lowest reach of the three. A mixed-use tall-building result will be read
by simulation methodologists and largely missed by the stock-modelling and benchmarking communities
who would most benefit from the band finding.

---

## Option B - Journal of Building Engineering (Elsevier)

**The case.** The broadest safe landing of the three, and the only one with **no venue collision at
all**. Mixed-use and tall-building studies are ordinary submissions here; a paper that spans an
occupancy generator, an injection method, a 56-cell simulation campaign and a benchmark critique does
not have to be narrowed to fit, because the journal's scope is wide enough to hold all four. It was
already identified in the 2J sheet as the clean substitute at comparable breadth when Sustainable
Cities and Society fell to its conflict, so this is not a new idea in this project - it is the one
that was parked.

**What it costs the manuscript.** Moderate and mostly cosmetic: this venue expects the practical
engineering consequence stated explicitly, so §6.4's "common lesson across three failing gates" needs
to end in a sentence a practitioner can act on - which reference to use, or not use, when
benchmarking a stacked tower. One or two paragraphs, no new simulation.

**The honest downside.** Breadth cuts both ways. The reviewer pool is less specialised, so the
probability of drawing a reviewer who does *not* understand why an uninjected control failing its own
band is the strongest evidence in the paper is materially higher than at Option A. If that reviewer
is drawn, expect a "your model is not validated" report that has to be rebutted rather than answered.
Prepare for that in the cover letter by stating the control result in the first paragraph.

---

## Option C - Building Simulation (Springer / Tsinghua University Press)

**The case.** Two concrete advantages, both real. First, the fit is genuine for the same reasons it
was for 2J: a large, gated, validated simulation campaign is this journal's house style. Second, and
this is the practical one, **the submission kit already exists**. The verified requirements are on
disk at `2J_docs_occ_nTemp/writing/submission/JournalOfBuildingSimulation/00_REQUIREMENTS_verified.md`,
the two-file double-blind structure is already understood, and the title-page template is written and
was used a day ago. The formatting pass for 3J is a repeat of work already done once, not a discovery.

**What it costs the manuscript.** The blinding pass, which for this paper is **not** a delete. §1.4 is
titled *"The Authors' Prior Line: Leg-1 to 2J to Leg-2, the Departure Point"* and identifies the
authors in its own heading and prose. Blinding it is a rewrite of that subsection, exactly as it was
for 2J. Add double spacing, 600 dpi figures, `Fig. N` citation form, no line numbers.

**🔴 The blocking consideration, and it is heavier than Option A's.** **2J was submitted here on
2026-08-07 and is under review.** Sending 3J to the same journal one day later puts two manuscripts
from the same authors, from the same research pipeline, in front of the same editor simultaneously.
The risk is not rule-breaking - it is the **perception of salami-slicing**, which is exactly the
charge the 2J cover letter spent a full paragraph pre-empting against 1J. Making that argument twice
in two days, at one journal, invites the question rather than settling it. **If this option is
chosen, wait for the 2J decision letter first.**

**The honest downside beyond that.** Gold open access here is **not** covered by the CRKN Springer
agreement - Building Simulation is a Tsinghua title only co-distributed by Springer, and the gold APC
was reported at **$3,590 USD**. The subscription route is **$0**, as at both other options. Do not
tick an institutional-waiver box here expecting it to apply.

---

## Option D - Building and Environment (Elsevier) - added 2026-08-08, after the rejection was attributed

**Why it was missing, stated first.** This option is late because of a bookkeeping fact, not a
judgement: B&E sat behind an unattributed rejection at the top of this sheet and was parked rather
than assessed. Once the author attributed that rejection to **0J** - a different and earlier
manuscript - the block dissolved, and B&E has to be ranked on its merits like the others. **Ranking
it now moves it above Option B.** The original ordering is left unedited above so the change is
visible rather than silent.

**The case, and it is the strongest scope argument on this sheet.** Occupant behaviour and occupancy
modelling in buildings is one of Building and Environment's **core subjects**, not an adjacent one.
This paper's primary object is an occupancy generator; the EnergyPlus campaign is what tests it. At
Options A and C the occupancy model is read as an input to a simulation study, and at Option B it is
read as one component of a broad building-engineering paper. **B&E is the only venue on this sheet
where the occupancy model itself is the thing the readership came for**, and where a result about
four *behaviourally distinct* uses inside one structure is a behavioural finding rather than a
modelling detail. It also carries more standing than Option B.

**What it costs the manuscript.** The framing shifts from "simulation method" toward "what occupant
behaviour does across stacked uses". Concretely: §1.1's multi-use gap and §6.1 need to lead with the
behavioural claim - four uses whose occupancy is non-stationary *in different directions* - rather
than with the architecture of the generator. The Transformer becomes the instrument, not the subject.
No new simulation, but a genuine introduction and discussion pass, more than Option B asks for.

**🔴 The honest risk, and it is the real one.** This is the most selective venue on the sheet, and the
paper's headline is that **three of four validation gates failed**. A selective journal's reviewer is
more likely, not less, to read that as an unvalidated model. The defence is strong and already in the
manuscript - an **uninjected control** failing its own band cannot be a model error, and two candidate
mechanisms were tested and refuted 56/56 - but it has to be made in the cover letter's first
paragraph and in the abstract, not left for §6.2 to explain. If that argument does not land, the
rejection comes fast.

**The other thing to weigh honestly.** B&E rejected 0J. That carries no formal weight - different
manuscript, different content, years apart, and editors do not hold grudges - but it does mean this
author line has not yet cleared this journal's bar, and there is no evidence about why 0J was
rejected recorded anywhere in this project. **If the 0J rejection reason is known and was about
scope rather than quality, that is worth knowing before choosing this option.**

> ## 🔴 REOPEN TRIGGER (b) HAS FIRED - 2026-08-08, later the same day
>
> The paragraph immediately above asked the question. **The authors answered it: 0J was rejected by
> Building and Environment for insufficient quality, not for scope.** That is the exact condition
> written into this sheet's reopen trigger (b), so it is recorded here rather than absorbed quietly,
> and the sheet is not allowed to keep reading as if the question were still open.
>
> **What this changes.** The paragraph above says "there is no evidence about why 0J was rejected".
> There is now, and it is the worse of the two answers. This author line has been measured against
> B&E's bar once and did not clear it, on the dimension the venue is selective about. The line
> "that carries no formal weight" still holds for the editorial process; it does not hold for the
> estimate of how hard this venue is.
>
> **What this does NOT change, and the distinction matters.**
> - 0J is a different manuscript, and 3J is the paper the authors call the strongest of the line.
>   A quality rejection of the earliest paper is weak evidence about the latest one.
> - Nothing is owed in the cover letter. The `[confirm]` about a prior rejection was already
>   answered on 2026-08-08: the rejection was 0J's, and a previous, different, rejected manuscript
>   is not a disclosable fact about this submission.
> - The reasons B&E was chosen are untouched: it is the best scope fit available, JBPS and Building
>   Simulation both already hold a manuscript from this line, and E&B is author-excluded.
>
> **The decision is therefore NOT reversed here, and it is not the assistant's to reverse.** The
> trigger fired, the evidence is on the record, and the choice is put back in front of the authors
> with the bar restated. If it is reconfirmed, the three commitments listed under "My recommendation"
> become more load-bearing, not less: the uninjected-control argument in the cover letter's first
> paragraph is the single thing standing between "three of four gates failed" and a fast desk
> reject.
>
> **One thing worth knowing that nobody has looked up:** *why* 0J was judged insufficient. "Quality"
> from a decision letter can mean the contribution was thin, the validation was weak, or the writing
> was unclear, and those point at completely different fixes. If the 0J decision letter still exists,
> reading it is cheap and it is the only direct evidence anyone has about this venue's bar.

---

## Considered and dropped, with the reason

| venue | why it is not on the list |
|---|---|
| **Energy and Buildings** | **Author-excluded** after four revision rounds on 0J. Still the closest scope match on record, so it remains the benchmark the three options are measured against - not a candidate. Note the exclusion is about **process, not fit**. |
| **Applied Energy** | The fit that made it Option B for 2J does not carry. 2J had a load-shape headline in Applied Energy's native vocabulary; 3J's headline is a *failed reference band*, and the paper stops at EUI with no energy-system consequence at all. Desk-reject risk is high and the fix is not one subsection. |
| **Sustainable Cities and Society** | Two independent reasons. The Concordia editor conflict is **confirmed** (`dr_2J-05`: Prof. Fariborz Haghighat, founding EiC, Concordia BCEE - the authors' own department), and separately the scope fit is much weaker than for 2J: this paper is **one building**, not a city or a stock. |
| ~~**Building and Environment**~~ | **Promoted to Option D below on 2026-08-08.** It was dropped from this sheet only because the rejection was unattributed; once attributed to 0J it is unblocked, and on scope it beats Option B. Keeping the strikethrough as the record of the error. |

---

## Side by side

| | **A · J. Build. Perf. Simulation** | **B · J. Building Engineering** | **C · Building Simulation** | **D · Building and Environment** |
|---|---|---|---|---|
| Reads three failing gates as a *finding* | **Yes - its strongest argument** | Depends on the reviewer drawn | Probably | Only if led with; **see the risk** |
| Is the occupancy model the *subject*? | An instrument | One component of four | An input to the campaign | **Yes - the core subject** |
| Fit to the paper as written | Highest | Good, needs a practitioner takeaway | High | High, after a framing pass |
| Work before submitting | Model-detail expansion, §6.3 | 1-2 paragraphs in §6.4 | **Blinding §1.4 + formatting; kit already built** | Intro + §6.1 framing pass, more than B |
| Venue collision | **1J under review here** | **None** | **2J under review here, submitted yesterday** | **None** |
| Prior history at the venue | none | none | 2J pending | **rejected 0J**, a different paper; no disclosure owed |
| Desk-reject risk | Low | Low | Low | **Moderate - the real cost of this option** |
| Reach and standing | Lowest | High | Moderate | **Highest of the four** |
| Gold-OA cost | not established here - do not assume | not established here - do not assume | **$3,590 (not waived)** | not established here - do not assume |
| Subscription-route cost | $0 | $0 | $0 | $0 |

*The two "not established" cells are deliberate. The 2J round's OA-cost claims were wrong once
already, in the direction of optimism. Check each on the publisher's own page before relying on it.*

---

## My recommendation - rewritten 2026-08-08

**Submit to Building and Environment (Option D).**

**The superseded recommendation, and why it was wrong.** The first version of this section chose
Option B, Journal of Building Engineering, almost entirely on collision-avoidance: A and C each hold
a manuscript from this pipeline under review, and B was the only venue where 3J would be judged on
itself. That argument was sound as far as it went, but it was optimising for the wrong thing. It
treated "no complications" as the objective. **If 3J is the strongest paper of the line, the
objective is placement, and a venue chosen to dodge an awkward cover-letter paragraph is a poor trade
for a paper you believe in.** B&E was also absent from that comparison entirely, for a bookkeeping
reason rather than a substantive one.

**Why D rather than the others, on the merits.**

- **Over B.** Same absence of venue collision, no disclosure obligation, and a materially better scope
  match - the occupancy model is the subject at B&E rather than one component among several - at
  higher standing. B's one advantage over D was breadth, and breadth was only valuable because the
  paper spans four things; B&E's occupant-behaviour readership holds all four without the paper
  having to be broad.
- **Over A.** JBPS remains the best *cultural* match, because its readership reads a failed reference
  band as a finding. But it holds 1J under review, and its reach is the lowest here. For the paper
  you rate highest, reach matters.
- **Over C.** C's advantage was a pre-built submission kit and it is real, but it is an argument about
  half a day of formatting. It cannot outweigh placement, and the concurrent-2J problem is the worst
  on the sheet.

**What choosing D commits you to, and it is not optional.** The failing gates must be led with, not
explained later:

1. **The cover letter's first paragraph states the uninjected-control result** - `Default_NECB` scores
   85.45 against a floor of 100 *with no occupancy injected at all* - and says explicitly that a
   control with nothing injected cannot be failing because of the model.
2. **The abstract already does this** and must keep doing it. It currently reads *"These failures are
   findings about reference-band applicability to mixed-use towers, not model error, reported at full
   strength with no band widened to pass them."* Do not soften that sentence to look safer; it is the
   sentence that makes the paper publishable at a selective venue rather than merely honest.
3. **The introduction and §6.1 pass** described under Option D, moving the behavioural claim ahead of
   the architecture.

**Keep Option A as the deliberate next move if D rejects.** By then the 1J decision will most likely
have landed, which removes the collision that demotes A here, and JBPS is the venue least likely to
misread the paper's central result.

**Option B remains the safe floor** if reach stops mattering, and **Option C stays conditional on the
2J decision letter**.

**One caution against my own recommendation, stated because it is the honest risk.** Selectivity cuts
against a paper whose headline is a failed validation. If the uninjected-control argument does not
land with the handling editor, D produces a fast rejection and costs weeks. B would very likely have
taken the paper. That is the trade, and it is the authors' to make - the sheet's job is to make sure
it is made knowingly rather than by default.

---

## Before any of the three - venue-independent, and all of it is real work

1. 🔴 **Only 2 of the 15 figures are cited in the body prose.** Measured 2026-08-08: the live chapters
   contain 16 `Figure N` occurrences, of which 15 are caption placeholders and **two** are actual
   in-text references (Figure 1 in §1, and the §5.1 forward reference to Figure 8). Thirteen figures
   are placed and captioned but never pointed at from the text. **Every journal on this list requires
   figures to be cited in order in the text. Fix this before choosing anything.**
2. 🔴 **The `**DOI DISPUTED, DO NOT SUBMIT UNTIL RESOLVED**` banner is inside `readySubmission.md`**,
   on both competitor references. The two DOIs are still unresolved and the submission copy is
   supposed to be a plain paper.
3. **The front matter is now fillable.** Department, funding, CRediT and Iseri's ORCID
   (`0000-0001-7735-3363`) all transfer verbatim from the 2J title page. **Hachem-Vermette's ORCID is
   absent from the 2J submission too**, so it should be omitted here rather than invented.
4. **Abstract is 225 words.** Confirm the cap at the chosen venue and cut only if it is genuinely
   lower. The 2J round cut an abstract to satisfy a 200-word limit that **no source ever stated**.
5. **SI Tables B1 and C1 are being cut** per the authors' decision of 2026-08-08 - they are the
   project's internal sprint board, not supplementary material.
6. **95 occurrences of internal task IDs** (`dr_L3-06`, `V2-B3`, `OD-1`), the phrase "this task", and
   French `Defaut` labels survive in the submission copy. Cutting B1/C1 removes a large share of them;
   the remainder needs a sweep.
7. **15 figures is a lot.** Check the chosen venue's figure limit; the eight schematics are the ones
   that would move to SI if a cap forces a choice.
8. **The gap matrix in Table 1 has still never been tested against the real literature.** The 2J round
   established this precisely: no competitor was found there because **no search was ever run**. The
   same is true here. If Table 1's novelty claim is to be defended in review, that is a separate
   external search and it has not been done.

---

## Next artefact, if you want the search side done properly

The 2J equivalent of this decision lives in `2J_docs_occ_nTemp/writing/submission/deepReserchPrompts/`
as `dr_2J-01` through `dr_2J-05`. The lesson from that series is worth carrying over exactly: the
**verification prompt (`dr_2J-05`) was the one that paid for itself**, and it should be written and
run *before* anything from the earlier reports is used, not after.

If the search side is wanted for 3J, the deliverable is a prompt file, not an answer - say the word
and it gets written to `3J_docs_occ_nTemp/deepResearch_Resources/` in the house style, with the
verification arm built in from the start rather than bolted on at report 5.
