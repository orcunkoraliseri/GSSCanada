# IMP-02 - Fable 5.1: inward-facing forensic audit of the 4J manuscript

**Written 2026-09-14. Paste Section 3 and nothing else.** Sections 1 and 2 are for the person running
the prompt, not for the model.

---

## 1. What this prompt is for

Fable is the **inward-facing** evaluator of the pair. It runs with the repository open, so it gets the
jobs that need the files: does every number in the paper trace back to a document on disk, do the tables
and the prose agree with each other, is the cross-referencing sound, does any figure say something the
text does not, and is anything claimed in the abstract that the results never deliver.

The **outward-facing** evaluation - literature coverage, DOI verification, venue fit, the hostile
reviewer read - is `IMP_01_GEMINI_manuscript_evaluation.md` and is deliberately **not** asked for here.
Fable must not search the web for this task, must not verify a DOI, and must not propose a citation.
That work is external by standing rule, and Gemini has it.

Running both and comparing the two returns is the point.

## 2. What to open, and what to say when you paste

Fable reads the repository directly. It needs read access to:

| What | Path |
|---|---|
| Manuscript, markdown master | `4J_docs_occ/writing/submission/4J_manuscript_submission.md` |
| Manuscript, built | `4J_docs_occ/writing/submission/4J_manuscript_submission.docx` |
| Supplementary material | `4J_docs_occ/writing/submission/4J_supplementary_material.md` |
| Figures as installed | `4J_docs_occ/writing/submission/figures/*.png` |
| Figure build scripts | `4J_docs_occ/writing/submission/figures/scripts/` |
| Figure specifications | `4J_docs_occ/writing/submission/figures/Prompts_Images/` |
| The analysis the paper rests on | `4J_docs_occ/writing/4thJ_crossStep_analysis.md` |
| Step documents, the source of every number | `4J_docs_occ/Step0_docs/` to `4J_docs_occ/Step11_docs/` |

🔴 **Read only. This prompt authorises no edit to any file.** The return is a report, not a patch.

🔴 **Do not paste the project's own list of known problems.** The first pass must be blind. The
reconciliation list is inside the prompt and the model is told to answer it last.

---

## 3. PASTE-READY PROMPT

```
You are an objective evaluator with the repository open, not a co-author and not an editor. A manuscript
in this repository is finished in draft and is being prepared for submission. Your job is to audit it
against the files it was built from and report what is wrong. You are not asked to improve the writing,
to rewrite any passage, or to produce a revised version of any part of it. Do not return edited text and
do not modify any file.

This is a read-only task. Make no edit to any file in the repository, including the manuscript, the
figure scripts and the step documents. If you believe a file must change, say which file and what is
wrong with it, and stop there.

Do not search the web. Do not resolve a DOI. Do not propose a reference. Literature work is handled by a
separate evaluator and is out of scope here; if you find yourself wanting to check something outside the
repository, write NOT CHECKABLE FROM THE REPOSITORY and move on.

THE FILES.
  The manuscript master is writing/submission/4J_manuscript_submission.md. The Word file
  writing/submission/4J_manuscript_submission.docx is built from it and must agree with it.
  The supplement is writing/submission/4J_supplementary_material.md.
  The figures as installed are writing/submission/figures/*.png, and the scripts that draw them are in
  writing/submission/figures/scripts/. Figure 1, Figure 2 and the graphical abstract are drawn by
  generate_fig01_pipeline.py, generate_fig02_loco.py and generate_graphical_abstract.py; Figures 3 to 7
  are drawn by generate_fig03.py to generate_fig07.py.
  The analysis the paper rests on is writing/4thJ_crossStep_analysis.md.
  Every number in the paper is supposed to come from a step document under Step0_docs to Step11_docs.

WHAT THE PAPER IS. It reports a pre-registered leave-one-country-out test. Harmonised national time-use
diaries from Spain, Italy and the United Kingdom, 73,254 diaries and 2,024,068 episodes, fine-tune a
7.30 billion parameter open-weight language model with a low-rank adapter. Two countries train it, the
third is held out, and the model must generate 5,200 synthetic diaries for the held-out country from
that country's published census marginals alone. It is scored against that country's published
time-budget tables, in minutes per day, mean absolute error, lower being better. The competitor is a
null: real diaries from the two training countries, raked to the same published marginals. The null wins
nine of nine cells and the closest the model comes is 2.70 minutes per day. The generated diaries are
then pushed through building energy simulation.

The negative result is deliberate and is in the title. It is not a defect for you to correct.

HOW TO WORK. Every finding must be anchored. Write the file path and the line number for every one, as
path:line. Check the line number by reading the file; do not estimate it. A finding you cannot anchor is
not a finding and must not be reported. Where a number is involved, quote the number as it appears in
the manuscript and, separately, the number as it appears in the source document, with that document's
path and line.

Say NOT FOUND rather than guessing. If a number in the paper has no traceable source in the repository,
that is one of the most valuable things you can report, so report it as NO SOURCE FOUND with a note of
where you looked.

RETURN EXACTLY THESE EIGHT SECTIONS, IN THIS ORDER, WITH THESE HEADINGS.

A. VERDICT IN FIVE LINES
   One line: is this internally consistent enough to submit, consistent after specific repairs, or not.
   Then four lines, each naming one thing, no more: the most serious internal inconsistency; the most
   serious number that cannot be traced to a source; the most serious disagreement between a figure and
   the text; the most serious disagreement between the markdown and the built Word file. Write NONE on a
   line if there is nothing to report for it.

B. NUMBER TRACEABILITY
   Extract every quantitative claim in the manuscript body and the supplement. For each: the number as
   written, where it is written as path:line, the source document and line it should come from, and a
   verdict of TRACED, MISMATCH with both values shown, or NO SOURCE FOUND. Sort so that MISMATCH rows
   come first, NO SOURCE FOUND second, TRACED last. If there are many TRACED rows, collapse them into a
   single count line at the end rather than listing them all, but list every MISMATCH and every NO
   SOURCE FOUND individually. Pay particular attention to: the corpus sizes; the parameter count; the
   number of generated diaries; every value in every table; every value quoted in the prose that also
   appears in a table; and the closest-miss figure.

C. INTERNAL CROSS-REFERENCE AUDIT
   1. Every table: does a caption exist, is it numbered, does the numbering run without a gap, and does
      at least one sentence in the body point at it. List any table that is never cited and any citation
      that points at a table that does not exist.
   2. Every figure: the same three checks. List any figure that is never cited in the body.
   3. Every section cross-reference of the form "see Section N": does Section N exist and does it
      contain what the pointer says it contains.
   4. Every caption: count its words. The house rule is ten words or fewer. List any that exceed it.

D. FIGURE AGAINST TEXT
   For each of the eight images, compare what the picture says with what the text says.
   1. Read every string of text in the image and check it against the text inventory in that figure's
      specification file under figures/Prompts_Images/. List any string in the image that is not in the
      inventory, and any inventory entry missing from the image.
   2. For Figures 3 to 7, check the plotted values against the script's own data table and against the
      manuscript table that reports the same series. A figure and a table that disagree is a serious
      finding.
   3. For Figure 1, Figure 2 and the graphical abstract, state whether the picture's structure matches
      what the text claims the pipeline and the design are. In particular: does Figure 2 show both
      methods receiving the same inputs, with the published marginals as a source and never as a
      destination; and does the graphical abstract show the held-out country never reaching the model.
   4. Name anything a figure asserts that the text never states, and anything the text asserts that its
      figure contradicts.

E. THE BUILT FILE AGAINST THE MASTER
   The Word file is built from the markdown. Report any difference that matters: missing section,
   missing table, missing or substituted image, table that lost its structure, caption that moved away
   from its object, or text present in one and not the other. State how you checked. If the two agree,
   say so and say what you compared.

F. INTERNAL CONSISTENCY OF THE ARGUMENT
   Not style, logic. At most ten items.
   1. Does the abstract claim anything the results section does not deliver? Quote both.
   2. Does the conclusion claim anything the discussion did not establish? Quote both.
   3. Does the limitations section admit everything the results section forces it to admit? Name any
      limitation the results imply and the limitations section does not carry.
   4. Is any term used with two different meanings in different sections? Name the term, both meanings
      and both locations. Band vocabulary is the likeliest offender: check whether age bands and
      activity bands are ever confused.
   5. Does any sentence describe a step of the pipeline in a way that another section contradicts?

G. WHAT THE REPOSITORY SAYS THAT THE PAPER DOES NOT
   Read writing/4thJ_crossStep_analysis.md and the step documents. Name at most eight findings, failures,
   caveats or declared exceptions that are recorded in the repository and are not carried anywhere in the
   manuscript or the supplement. For each: what it is, where it is recorded as path:line, and one
   sentence on whether its absence from the paper is a defect or a defensible scoping choice. A paper
   that reports a negative result loses the right to leave its own failures out quietly, so be strict.

H. RECONCILIATION - ANSWER THIS SECTION LAST AND ONLY AFTER A TO G ARE WRITTEN
   Do not revise A to G in the light of this section. The list below is what the authors already know is
   wrong. For each of the eight items, say one of: I FOUND THIS INDEPENDENTLY, and which of my sections
   it is in; I DID NOT FIND THIS, and whether I agree it is a defect now that I see it; or I DISAGREE
   THAT THIS IS A DEFECT, and why. Then add one final line: which of my own findings are NOT on this
   list, by section letter and row.
     1. Tables are numbered 1, 2, 5, 6, 7, 8, 9, 10. There is no Table 3 and no Table 4, and Section 3
        says the complete gate set is given in Table 4.
     2. Thirteen references are formatted and five further works are cited in the text but not
        formatted.
     3. The methodological guidelines behind the harmonisation have not been read by the author, and
        Section 2.1 says so.
     4. Table 9 presents numbers measured at one scale under a caption that names a different scale, and
        one of the three countries has no cell in it at all.
     5. Section 5.1 describes the rows of a table as activity bands where the table's rows are age
        bands.
     6. Three goodness-of-fit values quoted for a steering check come from a smaller pilot model, not
        from the model the paper reports.
     7. Figure 2 has a caption but no sentence in the body points the reader to it.
     8. Two arguments that used to appear inside Figure 2 were removed from the picture and were never
        written into Section 4: that giving the null weaker marginals would turn a null into a handicap,
        and that the raking starts from a flat seed so the donor surveys' own weights are discarded.

RULES THAT BIND THE WHOLE RETURN.
  Edit nothing. This is read-only.
  Do not rewrite the paper. Not one sentence of replacement prose anywhere in your answer.
  Do not change, round, recompute or reinterpret any number. If a number looks wrong, show both values
    and stop there.
  Do not propose loosening any threshold, band, gate or acceptance criterion because the model fails it.
    That the model fails is the finding.
  Do not search the web and do not offer a citation.
  Use no em dash and no en dash anywhere in your reply. Plain hyphens only.
  Every finding carries path:line, verified by reading the file.
  If a section has nothing to report, write the heading and the word NONE under it. Never drop a
    heading.
  No preamble, no summary of what you are about to do, no closing paragraph.

BEFORE YOU REPLY, CHECK THESE SIX AND SAY IN YOUR REPLY WHAT EACH ONE CAME OUT AS.
  1. Did you modify any file in the repository? You must not have. Name any you touched.
  2. How many quantitative claims did you extract in Section B, and how many were TRACED, MISMATCH and
     NO SOURCE FOUND?
  3. Did you read the actual PNG files for Section D, or only the scripts and the specifications? Say
     which.
  4. Did every finding you reported carry a path and a line number that you verified by reading the
     file? Name any that did not.
  5. Did you write Section H only after A to G were complete, without going back to change them?
  6. How many of the eight reconciliation items did you find independently?
Answer all six honestly, including where the answer is wrong. A wrong answer reported is one round trip;
a wrong answer reported as correct is three.
```

---

## 4. What to do with the return

1. **Check the anchors first.** Open three of its `path:line` pointers at random. If any of them is
   wrong, the whole return is suspect and the anchors all have to be checked before anything is
   believed. A wrong line number is the cheapest possible signal that the audit was not actually
   performed.
2. **Section B is the section that earns its keep.** A MISMATCH row is either a real error in the paper
   or a real error in a step document, and both matter. Resolve every one before anything else in the
   return is acted on.
3. **Compare against the Gemini return** (`IMP_01`). One merged list, three columns: found by both,
   Fable only, Gemini only. Found by both is real. Found by one only gets checked by hand.
4. **Section H is the calibration.** Few of the eight found means a shallow pass and the rest is worth
   less.
5. **Nothing in the return moves a gate, a band, a verdict or a registered definition.** If the return
   argues that one should move, record it as a finding; do not make the edit.
6. File the return beside this prompt as `RIMP_02_<date>.md`.
