# Editorial pass: make it read as a paper, not as a report

Author instruction, one message, 2026-08-11 (second round of the day). Everything below is
traceable to a sentence in that message; nothing is added on my own initiative. The message is
quoted per item so the scope stays auditable after the fact.

The standing rules of this build are unchanged and constrain every item: no built artefact is
edited by hand, the sources are edited and the document is rebuilt; verification is against the
INSTALLED `.docx`, never the build output; no band, gate verdict or measured number moves; no em
or en dashes enter the sources.

---

## A. One serif font for the whole document

> *"utilise meme type de font 'serif' pour toutes des documents"*

The document currently renders in THREE fonts and the author is seeing all three:

| where | style | font | serif? |
|---|---|---|---|
| body, tables, captions | docDefaults | Times New Roman 12 pt | yes |
| title, headings 1 and 2 | `majorHAnsi` theme font | **Aptos Display** | NO |
| every backticked identifier | `VerbatimChar` | **Consolas 11 pt** | NO |

Two fixes, and both are needed. Changing only the reference document would leave 321 monospace
runs typeset in Times but still reading as code to a reviewer; changing only the sources would
leave the headings sans-serif.

- **A1.** In `submission/extra/build_scripts/ref_submit_single.docx`: pin `Title`, `Heading1`,
  `Heading2` and `Heading3` to Times New Roman instead of the theme font, and repoint
  `VerbatimChar` from Consolas 11 pt to Times New Roman 12 pt. The predecessor is backed up.
- **A2.** Remove the inline code spans themselves from the manuscript sources. An identifier in
  backticks is repository apparatus; in a paper it is either prose or it does not belong. Kept as
  code only where the token IS the subject of the sentence and no prose form exists.

## B. Formulas as Word equations

> *"inserer des forumlaires avec d'option euqation de word
> 'AT_RETAIL = (occPRE == 5) | ((occACT == 4) & occPRE in {5, 9})'"*

The three formulas in the paper currently ship as fenced code blocks, which pandoc renders as
grey monospace paragraphs. Written as TeX display math they are converted by pandoc's docx writer
into native OMML, which is what Word's own equation editor produces and edits.

- **B1.** The AT_RETAIL derivation rule, in Chapter 3 and in Table 2. Set-membership and logical
  OR are written as mathematics rather than as Python operators.
- **B2.** The hotel multiplier, Chapter 3.
- **B3.** The checkpoint composite score, Chapter 3, inline.
- **B4.** Verify by counting `<m:oMath>` elements in the installed `.docx`. A formula that ships
  as a picture or as text would count zero, so the check cannot pass vacuously.

## C. Report apparatus out of the paper

> *"exclure ces notes 'Footnotes' toutes des document, ceci n'est pas un rapport c'est une
> publicaiton"* / *"'The derivation rule, frozen 2026-07-02 before any training run, is:' n'ajute
> pas des dates comme ça"* / *"'step9_scenario_response.csv' ne donne pas des nommes des dossier
> ou directoires"*

- **C1.** The two `## Footnotes` sections (Tables 2 and 3) are removed as sections. Their content
  is either promoted into the table's own note paragraph or dropped where the chapter prose
  already carries it. Every cross-reference that said "Table 2, footnote 1" is re-pointed.
- **C2.** Every internal build date is removed from reader-facing text. A freeze date is a fact
  about our process, not about the science; where the POINT was that the rule preceded training,
  the point is kept in words ("fixed before any training run") and the date goes.
- **C3.** Every repository file, directory and script name is removed from reader-facing text.
  The `## Sources` blocks are already stripped at build time, so this item is about the names that
  survive into `readySubmission.md`: the Step-9 result CSVs in Chapter 5, the weather filenames in
  Table 3, the deliverable paths in Table 5, and the model-card source column in the SI.
- **C4.** Table 5's "The three failing gates, at full strength" block is deleted outright. It
  restates Section 5.2 sentence for sentence, and the author asked twice for repetition to go.
  Section 5.2 keeps every number. Table 5's verification block ("what was confirmed against the
  source files") is internal quality assurance written in file names, and goes with it.
- **C5.** The SI model card loses its "Source in the project repository" column and its four
  disclosure notes, per item G below.

## D. Paragraphs, not bullets

> *"je ne vexu pas des punces dans le texte, ceci n'est pas un rapport, c'est une papier"* /
> *"n'utilise pas des punces, utilise des paragraphs"*

Converted to prose: the fourteen-scenario list (Chapter 4), the Tag-2 dispatch list (Chapter 3),
the axis definitions (Table 1), the threshold-provenance key (Table 4).

NOT converted, and the author should say if this is wrong: the five **Highlights** in the front
matter. Elsevier requires Highlights as a bulleted list of three to five short points and rejects
them as a paragraph, so this one list is a submission-system requirement rather than prose.

## E. Discussion and Limitations: one chapter each, no subsections, shorter

> *"'6 Discussion' '7 Limitations' utilise une chapitre pour de ce chapite, pas de sous-tites, en
> general raccourccir de chapitre"*

- **E1.** Chapter 6 loses its four subsection headings and its roadmap paragraph, and is cut to
  continuous prose.
- **E2.** Chapter 7 loses its six subsection headings and the sixteen L-numbers, and is cut to
  continuous prose. The L-numbers are a register's addressing scheme, not a paper's.
- **E3.** Every argument that survives keeps its deciding number in the same sentence. Nothing is
  softened: the three gates still fail, at full strength, and no band moves.

## F. No table inside Discussion, Limitations or Conclusion

> *"n'ajoute pas de tableau dans des chaptires des disscussion, conclusison limitations"*

Table 7 currently sits at the end of Chapter 7. It moves to the supplementary material and is
condensed (item G). Chapter 7 still cites it, so the citation gate stays satisfied. Chapters 6
and 8 carry no exhibit and gain none.

## G. Appendix carries tables, not essays

> *"n'ajoute pas des textes d'explanation pour des tableux ou des figures dans appendix"*

The supplementary model card is presently a table plus roughly 60 lines of explanation, four
warning notes and a disclosed-deviation essay, all written in repository paths. It is reduced to
the tables themselves plus one short note where a note states a fact a reader needs. The
checkpoint-selection deviation is NOT deleted from the paper: Chapter 3 already states it in
prose, in full, including the 0.0218 F1 gap, so the disclosure survives where a reader meets it.

## H. Shorten, and delete repetition

> *"il ya beaucoup des mots dans le texte, raccourcir en generalement, effacer des repetitions"*

Applied throughout, but only where a sentence repeats a sentence elsewhere or says nothing the
next sentence does not. Rule followed while cutting: before deleting any sentence carrying a
number, confirm the number survives somewhere a reader will meet it. A cut that loses a
measurement is a defect, not a shortening.

## I. Rebuild and verify

1. `py -3 writing/fullSet/assemble_3J.py` and read the whole report, not the exit code.
2. Rebuild the `.docx` through the recorded recipe.
3. `f4_prose_rules_check.py` and its `--falsify` arm. C6 and C7 are the two arms this round can
   plausibly break: C6 because cutting prose can orphan an abstract number, C7 because moving an
   exhibit can orphan its citation.
4. Against the INSTALLED file: count OMML equations, monospace runs, bullet paragraphs, headings,
   media parts, tables, captions, and confirm zero build dates and zero repository paths.
5. `f3` is expected to stay at its pre-existing 3 PASS / 2 FAIL. `f5` and `f6` are not run: they
   are figure gates, this round touches no figure, and `f5` writes to the real figure paths.

## What this pass does NOT do

- No number, band or gate verdict moves. No figure is created, replaced or re-plotted.
- The Highlights list stays bulleted (item D), pending the author's word.
- `f3`'s two failing arms are left as found: the figure registry is stale from this morning's
  replot, and the fix belongs to the registry, not to the gate.
