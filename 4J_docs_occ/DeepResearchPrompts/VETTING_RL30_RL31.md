# Vetting record — `RL30` and `RL31`

#### Vetted 2026-09-13, before any value entered the manuscript or any Step 6 document.
#### Procedure: `README.md` § *Vetting a returned report, BEFORE any value enters a document* (7 steps).
#### Prompts: `L30_negative_transfer_precedent.md`, `L31_transfer_repair_alternatives.md`
#### Responses: `RL30_negative_transfer_precedent.md` (27,583 B), `RL31_transfer_repair_alternatives.md` (28,377 B), both returned 2026-09-13.

---

## VERDICT

| Round | Verdict | Carried into our documents | Rejected |
|---|---|---|---|
| `RL30` | **ACCEPTED on its two `NOT FOUND`s and on one reviewer objection. REJECTED on every specific number, author list and URL.** | *No published like-for-like LLM vs raked-donor comparison exists*; *no published numerical floor on the number of source populations exists*; the marginals-starve-the-generator objection in its Section G6 | the `K = 2` invariance theorem as an explanation of our failure; the RecSys "11 of 12"; every "read full text" claim; the fabricated author list and repository for the CFG paper |
| `RL31` | **ACCEPTED on one sentence and one question. REJECTED on its admissibility sort, which is the one thing the prompt called mandatory.** | *plain raking has not been beaten by a learned hybrid in the published record*; its Section G7 question and its own honest answer to it | the "8 or more countries" number; the "slope 0.45 to 0.85" prediction; the Box 1 / Box 2 sort as returned; the whole of Section D |

🔴 **Both reports were produced in one external session whose tool transcript we hold.** That transcript
shows CrossRef, OpenAlex, arXiv and Semantic Scholar **metadata** calls and two arXiv **abstract**
scrapes. It shows no retrieval of any paywalled full text. Both reports nevertheless claim **"Opened in
full (full text examined): 8 documents"**, including Deville and Sarndal (JASA 1992) and Beckman et al.
(Transportation Research A 1996). **The negative control that exists to catch this failure is itself the
failure.** Treat the opened/inferred split in both documents as unusable.

---

## 1. Checks run, and what each returned

All checks below are offline. None required opening a paper, and none depends on trusting either dossier.

### 1.1 The identity neither report can fake — `RL31`'s own floor arithmetic

`RL31` Section A and Section C both recommend widening the corpus to **"eight or more HETUS member
states"**, and both justify it with **one** source: Rosenfeld, Ravikumar and Risteski (ICLR 2021), whose
condition the reports state themselves, twice, in the same words:

```
|E_tr| > d_s          (number of training environments must exceed the spurious-feature dimension)
```

Both reports also state `d_s` for our problem themselves: `RL30` Finding 7 says **"across twenty
demographic covariates"**, and `RL30` Section G6 says **"spans twenty or more"**. Substituting the
report's own two numbers into the report's own inequality:

```
|E_tr| > 20   =>   floor >= 21 source countries
```

🔴 **The report recommends 8. Its own cited condition implies at least 21.** The recommended number is
short of its stated justification by a factor of about 2.6, and no derivation of 8 appears anywhere in
either document.

⚪ **Eight is, however, roughly the number of HETUS countries we could plausibly obtain**, and the prompt
told it so: *"we hold a documented route to widen the corpus from three to a larger set of HETUS
members"*. This is README vetting step 7 exactly — the recommendation moved to the number that happens
to be reachable. **The corpus-widening route may still be right, but it is not evidenced by this report,
and "eight" must never be written down as a literature-derived threshold.**

### 1.2 Internal contradiction — `RL30` answers the prompt's most important question twice, oppositely

The prompt marked one line 🔴 as *"the single most important line in this report for us, because it
decides whether our result is a fact about language models or a fact about our corpus size."*

| Where | Claim | Type declared | Confidence declared |
|---|---|---|---|
| `RL30` Finding **7** | invariant transfer **provably requires** `|E_tr| > d_s`; at `K = 2` it fails | **Fact** | **H** |
| `RL30` Finding **9** | *"Universal numerical floor on source populations: **NOT FOUND**. The survey and spatial statistics literature states no universal numerical threshold"* | **Fact** | **H** |

Both are typed `Fact` at confidence `H`, and they contradict each other on the same question.

🔴 **The resolution is in our favour and against the report's own framing.** Rosenfeld et al. proves a
property of **Invariant Risk Minimization**, a specific estimator with an explicit invariance penalty.
**We do not run IRM.** We run LoRA fine-tuning of an autoregressive backbone with the conditioning
carried in the prefix and no invariance objective anywhere. A theorem about when IRM fails to recover an
invariant predictor **does not bind an estimator that never attempted invariance**. Finding 7 is a
category transfer, not a finding about us.

⚪ **Finding 9 is the honest answer, and it is a usable one.** It means two things at once, and the
manuscript needs both: nobody can dismiss our negative result by citing a published rule that three
countries was always too few, **and** we cannot claim such a rule in our own defence. The corpus-size
question is open in the literature, and our three-fold result is a data point in it.

🔴 **Consequence for drafting:** `RL30` Section E instruction 4 and `RL31` Section E instruction 5 both
tell us to put Rosenfeld et al. in the discussion as the mathematical explanation of our failure.
**Do not.** A reviewer who opens that paper will see we invoked an IRM identifiability result against a
model that does no IRM, and the limitation section is the worst place in a paper to be caught
overreaching.

### 1.3 The metadata column gives the round away — `Section F`, "Confirmed reachable?"

README vetting step 3 says to check the provenance columns before the value columns. Two rows fail on
their own text.

| Report | Row | URL asserted | State |
|---|---|---|---|
| `RL30` F5, and `RL31` F2 (same URL, both reports) | "CFG for Language Models Codebase", "Official PyTorch implementation" | `github.com/tony-sanchez/cfg-lm` | 🔴 the author of that paper is **Guillaume** Sanchez, not Tony. The username is built out of the report's own invented initial. |
| `RL31` F4 | "Official code for contrastive decoding" | `github.com/XiangL1999/ContrastiveDecoding` | 🔴 one character wrong (`XiangL1999`, not `XiangLi1999`). |

**Every row in both `Section F` tables is marked "Confirmed reachable".** At least two of them cannot
have been opened. 🔴 **The "Confirmed reachable?" column was filled in as a formality, so no row of it in
either document is evidence of anything.** If we want any of these artefacts, we fetch them ourselves.

### 1.4 Author lists — two of the three machine-learning citations are wrong

| Cited as | What the citation is | State |
|---|---|---|
| *"Sanchez, T., Kirchman, M., Riedel, S., and Mitchell, J. (2023). Stay on topic with Classifier-Free Guidance."* (`RL30` H13, `RL31` H3) | the **load-bearing** source for `RL31`'s only real amplitude recommendation | 🔴 author list does not match the paper. The correct first author is Guillaume Sanchez and the author list includes Stella Biderman. The surnames Kirchman and Mitchell appear to be invented. |
| *"Li, X. L., Holtzman, A., Schick, T., Sisman, B., West, P., and Zettlemoyer, L. (2023). Contrastive Decoding"* (`RL31` H4) | the source for rejecting contrastive decoding | 🔴 partially invented. Li, Holtzman and Zettlemoyer are right; the middle of the list is not. |

⚪ **The two papers are real and the arXiv identifiers `2306.17806` and `2210.15097` look right.** The
findings may well survive. **The citations do not, and neither may be pasted into a bibliography.**

### 1.5 `RL31`'s CFG prediction contradicts `RL31`'s own Finding 1

| Where | Claim |
|---|---|
| Finding 1 (the evidence) | CFG *"increas[es] prompt steering adherence by **15 % to 35 %** in language tasks"* |
| Section C (the recommendation) | *"slope moves from ~0.45 toward **0.85**"* |
| Section E (the write-up instruction) | *"improves the slope of the fictional-country diagnostic from ~0.45 to ~**0.80**"* |

0.45 to 0.85 is **+89 %**, between two and six times the effect size the same document cites as its
evidence. 🔴 **And the fictional-country slope diagnostic is ours.** `RL30` Finding 1 says, correctly,
that no published study runs this comparison at all. **A numeric prediction for an unrun experiment on a
diagnostic that exists only in our repository is fabricated by construction**, whatever the mechanism's
merits. It must not appear in a plan, a gate band, or a sentence.

### 1.6 The mandatory sort was performed as a formality — `RL31` Section C

The prompt said, marked 🔴: *"Sort every recommendation you make into one of those two boxes, explicitly,
in Section C. An answer that does not sort is not usable to us."* Box 1 was defined as **"a method change
that improves our numbers against the frozen bands"**.

| Row | Box returned | Action returned | Consistent? |
|---|---|---|---|
| Classifier-free guidance with conditioning dropout | Box 1 | design change | ✅ |
| Post-sampling generalised raking of generated diaries | Box 1 | design change | ✅ |
| Contrastive decoding | **Box 1** | **"Stop: do not allocate engineering time"** | 🔴 no |
| Auxiliary moment-matching loss | **Box 1** *("would be admissible if functional")* | **"Stop: reject"** | 🔴 no |
| Distributional PPO / RLHF | **Box 1** *("would be admissible if functional")* | **"Stop: reject"** | 🔴 no |
| Relaxing the MAPE band | Box 2 | stop | ✅ |
| Replacing the raked-donor null | Box 2 | stop | ✅ |
| Widening to 8+ countries | **Box 1** | design change | 🔴 no: it cannot improve *this* paper's numbers against *these* bands at all. It is a different study and belongs in neither box. |

🔴 **Six of eight rows are labelled Box 1, three of which the report itself then rejects.** "Admissible
against frozen bands" was used to mean "not forbidden", which is not what the prompt defined and not
what we need. **Two genuine Box 1 candidates survive the re-sort: guidance with conditioning dropout,
and post-sampling raking.** Everything else is a rejection or out of scope.

### 1.7 `RL31` Section D judged the wrong machine, and the prompt said Section D was load-bearing

The prompt's Section D states: *"All computation for this paper now runs **locally on a single machine**.
The institutional cluster is **fetch and read-only** for this project."*

`RL31` Section D opens: *"judged strictly against local execution on a single workstation / **single-node
SLURM GPU partition (MIG slice** ... maximum 7 days walltime)"*, and then every one of its seven rows
answers the column **"Do we meet it on a shared single-node SLURM GPU?"**, assuming an **A100 80 GB**.

🔴 **It answered the cluster question we explicitly withdrew, on hardware we did not state, for the one
section the prompt called load-bearing.** Every feasibility verdict in that table is about a machine this
project is not allowed to compute on. The verdicts are not necessarily wrong for our local box, but none
of them was actually addressed to it. **Re-derive any cost we care about against the local machine.**

### 1.8 Both reports invented our plan, then recommended what we had already decided

`RL30` Section C row 1, column *"What we currently plan"*: **"Present fine-tuned LLM as a successful
cross-national generator for European building occupancy."**

That is false, it was contradicted by the prompt the report was answering, and it is the opposite of
author decision 4 of 2026-08-14, which made the hardened raked-donor null *the objective of the paper,
stated as such in the introduction*. The report then issues, as a **"Design change"** at **"Medium"**
effort, the instruction to *"reframe the paper as a pre-registered empirical falsification study"* and to
*"relocate contribution to the experimental apparatus"*.

⚪ **We did both of those things a month before the prompt was written** (decision 3 relocated the
contribution to the method; decision 4 pre-registered the bar). This is README vetting step 1 and step 2
together: the report's headline recommendation is our own decision handed back to us as a finding.
**It is not corroboration. It is an echo.**

### 1.9 The reference lists were padded from the session's own connectivity test

Both reports carry **Iseri, Gursel Dino and Kalkan (2026), *Energy and Buildings* 357, 117155** in the
reference list and in the CrossRef-resolved list. **Neither report cites it in support of a single
finding**, in any section, in either document.

🔴 The executing session's transcript shows that this exact DOI, `10.1016/j.enbuild.2026.117155`, was the
**first CrossRef call of the session, used as an API connectivity test**. It then appears in both
bibliographies marked *"Read full text"*.

⚪ `RL28` was rejected in part for *"its citation of our own paper as evidence"* (`VETTING_RL28_RL29.md`).
**The same tell has now appeared in three rounds.** Here it is inert, because the reference supports
nothing, but it shows how the bibliographies were assembled.

### 1.10 One arithmetic claim about a paper we can check cheaply

`RL30` Finding 12: *"11 of 12 published neural recommendation models failed to outperform simple,
non-neural baselines"* (Ferrari Dacrema et al., RecSys 2019).

⚪ Those counts do not match that paper, which examined **18** papers from top venues, found **7**
reproducible with reasonable effort, and beat **6 of those 7** with simple baselines. **The qualitative
precedent is real and useful to us; the numbers are not.** 🔴 **Do not quote a count from this paper
without opening it.**

---

## 2. What survives, and is carried

### 2.1 The two `NOT FOUND`s, which are the round's actual product

| Question the prompt asked | Answer returned | Status |
|---|---|---|
| `L30` Item 1. Is our result already published, by anyone, in any domain? | **NOT FOUND.** No published study compares a fine-tuned or prompted LLM against an IPF-raked donor pool on an unseen population. | 🟢 **Carried, as an absence.** Written as *"we found no published like-for-like comparison"*, never as *"none exists"*. |
| `L30` Item 2 🔴. Is there a published floor on the number of source populations? | **NOT FOUND.** No universal numerical threshold is stated in the survey or spatial statistics literature. | 🟢 **Carried, as an absence**, and it is the most consequential line of the round. See §1.2. |
| `L31` Item 2. Has any learned hybrid beaten a plain raked donor pool? | **NOT FOUND.** *"Plain raking of empirical survey donor pools has not been beaten by any learned hybrid."* | 🟢 **Carried, as an absence.** The prompt named this in advance as the most useful sentence it could return, and it returned it. |

🔴 **All three are absence claims resting on a literature sweep we cannot audit**, from a session whose
provenance columns we have just shown to be unreliable. **They are strong enough to shape how we frame
the paper. They are not strong enough to be asserted as facts about the literature.** Every one of them
goes into the manuscript in the first person: *we searched and did not find*, with the date.

### 2.2 The reviewer objection we must pre-empt — `RL30` Section G6

The report's strongest paragraph is the one arguing against us, which the prompt forced it to write:

> *"conditioning solely on published demographic marginals starves the generator of essential
> macro-level explanatory variables: differences in national time-use between Spain and the UK (such as
> meal hours, school schedules, and shop opening hours) are driven by national labor laws, institutional
> norms, daylight hours, and climate, none of which can be inferred from age and employment marginals
> alone."*

🟢 **Carry this, and answer it in the manuscript.** It is the objection a good reviewer reaches first,
and it is sharpened rather than weakened by our own positive result: the appliance peak lands six hours
apart across the three countries (`es` 14:00, `it` 18:00, `uk` 20:00) from **one** appliance set and
**one** calibration, with only the diary differing. That spread is exactly the institutional signal the
objection describes, and our conditioning vector does not carry it. **The honest reading is that the
model was asked to reconstruct from demographic marginals a pattern that demographic marginals do not
encode** — which is a statement about the conditioning design, ours, not about the backbone.

⚪ It does not rescue the result. The raked donor pool had **the same marginals and no more**, and still
won two to six times over. Whatever the conditioning lacks, it lacked it for both sides.

### 2.3 The question `RL31` was not asked, and its own answer — `Section G7`

> *"If the raked donor null is superior in fidelity, structural validity, compute cost, and empirical
> realism, what is the legitimate scientific justification for using a 7B parameter neural generator at
> all?"*
>
> *"In an operational engineering pipeline where donor microdata from adjacent European countries is
> accessible, there is no technical justification. ... The LLM is justified solely as an object of
> academic investigation into generative transfer boundaries, not as a superior engineering tool."*

🟢 **Carry it.** It is the sharpest sentence in either document, it is the question a practitioner
reviewer will ask, and answering it in the discussion rather than being asked it in review is worth more
than any citation in this round.

### 2.4 The two surviving method candidates, re-sorted by us

| Candidate | Our sort | Condition |
|---|---|---|
| Guidance at generation time, with conditioning dropout during adapter training | **Box 1: admissible as a NEW, separately pre-registered experiment**, original failure kept and reported alongside | 🔴 Bands for it must be pre-registered **before** it is run, exactly as `G6.x` were. No number from `RL31` may seed those bands, in particular not 0.80 or 0.85. |
| Post-sampling raking of an over-generated candidate pool (`RL06` Candidate 8) | **Box 1**, same condition | ⚪ Note what it concedes: it wins on marginals **because raking wins on marginals**. It cannot be reported as the LLM closing the gap. |

Everything else `RL31` returned is a rejection, an out-of-scope study, or unsorted.

---

## 3. What this round changes about the manuscript

* **Nothing in the result changes. No gate moved, no band moved, no verdict changed.** This round was
  reading, not measurement.
* **`G6.1`'s 9 of 9 failure stands, and is now known to be without published precedent either way.**
* 🔴 **The "three countries was always too few" defence is NOT available to us**, because no published
  floor exists to invoke, and the one theorem offered is about an estimator we do not run.
* 🔴 **The corpus-widening route is NOT evidenced by this round.** It may still be the right next study.
  The number 8 is not evidence and must not be written.
* 🟢 **Two absences and one reviewer objection are the deliverable.** That is a thin but honest round,
  and thin-and-honest is the outcome this series has learned to prefer.

---

## 4. Round-level verdict against the README's seven steps

| Step | Result |
|---|---|
| 1. Check its claims about our own work first | 🔴 **FAILED.** `RL30` invented our plan (§1.8). |
| 2. Agreement with what we supplied tells us nothing | 🔴 **FAILED.** Its headline design change is author decisions 3 and 4 handed back (§1.8). |
| 3. Check metadata columns, not value columns | 🔴 **FAILED.** Every `Section F` row says "confirmed reachable"; at least two cannot be (§1.3). |
| 4. Make it obey an identity it cannot fake | 🔴 **FAILED.** Its own floor inequality gives 21, it recommended 8 (§1.1). Its own effect size gives 15-35 %, it predicted 89 % (§1.5). |
| 5. Version and date rot | ⚪ **Not the failure mode here.** Little in this round is version-sensitive. |
| 6. Expect the answer to inherit the prompt's framing | 🔴 **FAILED**, and the reports say so themselves: `RL30` negative control 1 concedes every number about us is quoted from us. |
| 7. Recommendations moving in the rescuing direction | ⚪ **PARTIAL PASS.** It did answer *"nothing will fix the standalone transfer claim within `K = 2`; report the negative result and move on."* That is the non-rescuing answer, and it is the round's most credible sentence. Its one rescuing recommendation, the hybrid, it flagged itself and kept the original failure primary. |

🔴 **Five of seven vetting steps failed, and the round is still worth keeping**, because the three
`NOT FOUND`s and the two adversarial paragraphs are exactly what a prompt built out of negative controls
is supposed to extract. **What failed was everything the report asserted. What held was everything it
was forced to concede.**

---

## 5. Actions

1. 🔴 **No value, count, slope, threshold, author list, URL or effect size from `RL30` or `RL31` enters
   any document without being re-derived or re-opened by us.** The single exception is the three
   `NOT FOUND`s, which enter in the first person as our own failed search, with today's date.
2. 🔴 **Rosenfeld et al. (2021) does not go in the limitations section** as the explanation of our
   failure. See §1.2.
3. ⚪ **"Eight or more HETUS countries" is struck.** If the corpus-widening study is proposed, it is
   proposed on our own reasoning, with no number attributed to the literature.
4. ⚪ Guidance with conditioning dropout, and post-sampling raking, are the only two candidates that
   survive the re-sort, and both require their own frozen pre-registration before a single run.
5. ⚪ The marginals-starve-the-generator objection (§2.2) and the why-use-a-7B-at-all question (§2.3)
   are both drafted into the discussion.
6. ⚪ `L28` and `L29` remain unregistered in `README.md`. Still flagged, still not fixed.
