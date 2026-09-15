# IMP-01 - Gemini / Antigravity: outward-facing evaluation of the 4J manuscript

**Written 2026-09-14. Paste Section 3 and nothing else.** Sections 1 and 2 are for the person running
the prompt, not for the model.

---

## 1. What this prompt is for

Gemini is the **outward-facing** evaluator of the pair. It is the tool that can reach the literature,
resolve a DOI, and read a venue's scope page, so it gets the jobs that need the outside world: is the
claim defensible against what is already published, is the related work honest, does every citation
exist, and would a hostile reviewer accept the negative result.

The **inward-facing** evaluation - does every number in the paper trace to a file on disk, do the tables
and the prose agree, is the numbering sound - is `IMP_02_FABLE_manuscript_evaluation.md` and is
deliberately **not** asked for here. Running both and comparing the two returns is the point. If they
agree on a defect, it is real. If only one finds it, that is information too.

## 2. What to attach, and what to say when you paste

Attach all three files:

| File | Path |
|---|---|
| Manuscript, Word | `4J_docs_occ/writing/submission/4J_manuscript_submission.docx` |
| Manuscript, markdown master | `4J_docs_occ/writing/submission/4J_manuscript_submission.md` |
| Supplementary material | `4J_docs_occ/writing/submission/4J_supplementary_material.md` |

The markdown is the master and the Word file is built from it. Where they differ, the markdown wins and
the difference is itself a defect worth reporting.

🔴 **Do not paste the project's own list of known problems.** The first pass must be blind, so that the
return can be used to check our list rather than repeat it. The prompt asks for the reconciliation in its
own section, at the end, from a list the model is given only after it has committed to its own findings.

🔴 **Vet the return under the seven-step protocol before any of it is acted on.** `RL30` and `RL31` failed
five of seven steps on 2026-09-13 and several of their citations had to be struck. Treat every citation
this return offers as unverified until it has been resolved independently.

---

## 3. PASTE-READY PROMPT

```
You are an objective evaluator, not a co-author and not an editor. You are reading a manuscript that is
finished in draft and is being prepared for submission. Your job is to judge it, find what is wrong with
it, and say so plainly. You are not asked to improve the writing, to rewrite any passage, or to produce
a revised version of any part of it. Do not return edited text.

Three files are attached. The markdown file is the master and the Word file is built from it; the
supplementary material is a separate document that ships alongside. Read all three in full before you
write anything.

WHAT THE PAPER IS. It reports a pre-registered leave-one-country-out test. Harmonised national time-use
diaries from Spain, Italy and the United Kingdom, 73,254 diaries and 2,024,068 episodes, are used to
fine-tune a 7.30 billion parameter open-weight language model with a low-rank adapter. Two countries
train the model, the third is held out, and the model must generate 5,200 synthetic diaries for the
held-out country from that country's published census marginals alone. It is scored against the held-out
country's published time-budget tables, in minutes per day, mean absolute error, lower being better. The
competitor is a null: real diaries from the two training countries, raked to the same published
marginals. Both sides are given exactly the same inputs. The result is that the null wins nine of nine
country-by-age-band cells, and the closest the model comes is 2.70 minutes per day. The generated diaries
are then pushed through building energy simulation to see what survives downstream.

The paper reports this as a negative result and says so in its title. That is deliberate and it is not
a defect for you to correct. Your job is to judge whether the negative result is argued well enough to
publish, not to suggest making it sound more positive.

HOW TO JUDGE. Be hard on it. A reviewer who wants to reject this paper is the reader you are simulating.
At the same time, be fair: a criticism you cannot tie to a specific line is not a criticism, it is a
mood. Every point you raise carries a pointer to where in the document it lives, written as the section
number and, where you can, the first six words of the sentence. Do not invent line numbers.

Say NOT FOUND rather than guessing. If you cannot verify something, write that you could not verify it
and say what you tried. A confident wrong answer costs three rounds of work; an honest NOT FOUND costs
none. This applies with particular force to citations: if a DOI does not resolve, say it does not
resolve. Never repair a broken reference by supplying a plausible one.

RETURN EXACTLY THESE EIGHT SECTIONS, IN THIS ORDER, WITH THESE HEADINGS.

A. VERDICT IN FIVE LINES
   One line: is this publishable as it stands, publishable after specific repairs, or not publishable
   in this form. Then four lines, each naming one thing, no more: the single strongest part of the
   paper; the single weakest; the one defect most likely to cause a desk reject; the one defect most
   likely to cause a reviewer reject after peer review. No hedging, no summary of the paper.

B. THE CLAIMS AUDIT
   List every claim the paper makes that a reviewer could challenge. For each one, one row: the claim in
   your own words in under fifteen words; where it is made; what evidence the paper offers for it; and
   your verdict from SUPPORTED, UNDER-SUPPORTED, or CONTRADICTED BY THE PAPER'S OWN EVIDENCE. Sort the
   list so that the worst verdict is first. Include the claims in the abstract and the highlights, which
   are where over-claiming usually hides. If the paper claims something in the abstract that the results
   section does not deliver, that is the most important row in this table and it goes at the top.

C. THE NEGATIVE RESULT, ON ITS OWN
   A negative result has to clear a bar that a positive one does not: the reader has to believe the
   method was given a fair chance. Answer these five, each in two or three sentences.
   1. Does the paper eliminate the possibility that the model simply did not have enough capacity? It
      claims to eliminate this three ways. Are the three ways independent of each other, and does any
      one of them do the work on its own?
   2. Does the paper eliminate the possibility that three countries was too few? Is that defence
      available to it, and does it try to use it?
   3. Is the null a fair competitor, or is it secretly advantaged? Look for anything either side is
      given that the other is not.
   4. Could the result be an artefact of the scoring measure rather than of the model? What would a
      different measure have shown, and does the paper say?
   5. Is the pre-registration credible as described, or does it read as having been written after the
      numbers were known?

D. RELATED WORK AND POSITIONING
   The reference list is short: thirteen formatted references plus a block of five things cited in the
   text and not yet formatted. Judge the coverage, not the count.
   1. Name the specific published work this paper must cite and does not. Give author, year, title and
      DOI for each, and resolve every DOI before you list it. Mark any you could not resolve as NOT
      RESOLVED and leave it in the list with that mark rather than dropping it.
   2. Is there published work that already reports what this paper reports, in whole or in part? If a
      negative transfer result like this one exists in the literature, this paper's contribution changes
      shape and it needs to know now.
   3. Is there published work that CONTRADICTS this paper's result, that is, a learned model beating
      plain raking or reweighting on a cross-population transfer task? If so, the paper must engage with
      it and currently does not.
   4. Does the paper's account of its own lineage, in the positioning table near the start, describe
      that lineage accurately?

E. CITATION INTEGRITY
   Go through every reference in the list. For each: does the work exist, does the DOI resolve, do the
   author list, year, title, journal, volume and pages match the record, and is the claim it is cited
   for actually in it where you can check. Return one row per reference with a verdict of VERIFIED,
   MISMATCH with the field that is wrong named, or NOT RESOLVED. One entry is already flagged in the
   paper as not read by the author. Say whether that flag is handled honestly in the text.

F. WHERE THE READER GETS LOST
   Read it once as a reader who knows building energy modelling but has never used a language model, and
   once as a reader who knows language models but has never opened an energy simulation. Name the exact
   places, at most six, where each of those two readers stops being able to follow. Give the section and
   the first six words of the sentence where each one breaks down. Do not propose replacement wording.

G. WHAT IS MISSING THAT A REVIEWER WILL ASK FOR
   At most eight items, each one sentence, each one thing a reviewer will demand before accepting. For
   each, say whether it is an analysis that must be run, a passage that must be written, or a piece of
   evidence that must be shown. Do not include anything you have already raised in B, C, D, E or F.

H. RECONCILIATION - ANSWER THIS SECTION LAST AND ONLY AFTER A TO G ARE WRITTEN
   Do not revise A to G in the light of this section. The list below is what the authors already know is
   wrong with the paper. For each of the eight items, say one of: I FOUND THIS INDEPENDENTLY, and which
   of my sections it is in; I DID NOT FIND THIS, and whether I agree it is a defect now that I see it;
   or I DISAGREE THAT THIS IS A DEFECT, and why. Then add one final line: which of my own findings are
   NOT on this list, by section letter and row.
     1. Tables are numbered 1, 2, 5, 6, 7, 8, 9, 10. There is no Table 3 and no Table 4, and Section 3
        says the complete gate set is given in Table 4.
     2. Thirteen references are formatted, and five further works are cited in the text but not
        formatted: a building typology documentation set, three national survey user guides, a
        methodological guidelines document, and the author's own earlier paper.
     3. The methodological guidelines behind the harmonisation have not been read by the author, and
        Section 2.1 says so.
     4. Table 9 presents numbers measured at one scale under a caption that names a different scale, and
        one of the three countries has no cell in it at all.
     5. Section 5.1 describes the rows of a table as activity bands where the table's rows are age
        bands.
     6. Three goodness-of-fit values quoted for a steering check come from a smaller pilot model, not
        from the model the paper reports, and the paper says so in the prose rather than removing them.
     7. Figure 2 has a caption but no sentence in the body of the paper points the reader to it.
     8. Two arguments that used to appear inside Figure 2 were removed from the picture and were never
        written into Section 4: that giving the null weaker marginals would turn a null into a handicap,
        and that the raking starts from a flat seed so the donor surveys' own weights are discarded.

RULES THAT BIND THE WHOLE RETURN.
  Do not rewrite the paper. Not one sentence of replacement prose anywhere in your answer.
  Do not change, round, recompute or reinterpret any number in the paper. If a number looks wrong, say
    which number and why it looks wrong, and stop there.
  Do not propose loosening any threshold, band or acceptance criterion because the paper's model fails
    it. That the model fails is the finding.
  Do not suggest reframing the negative result as a positive one.
  Use no em dash and no en dash anywhere in your reply. Plain hyphens only.
  If a section has nothing to report, write the heading and the word NONE under it. Never drop a
    heading.
  Length: as long as it needs to be, but every sentence must carry a fact. No preamble, no summary of
    what you are about to do, no closing paragraph about how interesting the work is.

BEFORE YOU REPLY, CHECK THESE SIX AND SAY IN YOUR REPLY WHAT EACH ONE CAME OUT AS.
  1. Did you read all three attached files in full, including the supplementary material?
  2. How many references did you check in Section E, and how many of them resolved?
  3. Did you write any replacement prose for the paper anywhere in your reply? You must not have.
  4. Did you write Section H only after A to G were complete, without going back to change them?
  5. Did any citation you offer in Section D come from memory rather than from a resolved record? Name
     any that did.
  6. How many of the eight reconciliation items did you find independently?
Answer all six honestly, including where the answer is wrong. A wrong answer reported is one round trip;
a wrong answer reported as correct is three.
```

---

## 4. What to do with the return

1. **Vet it before acting on it.** Seven-step protocol. Every DOI it offers gets resolved independently
   against CrossRef. Anything that does not resolve is struck, not repaired.
2. **Compare it against the Fable return** (`IMP_02`). Build one merged list with three columns: found by
   both, found by Gemini only, found by Fable only. A defect found by both is real and goes straight into
   the board. A defect found by one only gets checked by hand before it is believed.
3. **Section H is the calibration.** If it found few of the eight, the evaluation was shallow and the
   rest of the return is worth less. If it found most of them and added new ones, the new ones are worth
   taking seriously.
4. **Nothing in the return moves a gate, a band, a verdict or a registered definition.** If the return
   argues that one should move, that is a finding to record, not an edit to make.
5. File the return beside this prompt as `RIMP_01_<date>.md`.
