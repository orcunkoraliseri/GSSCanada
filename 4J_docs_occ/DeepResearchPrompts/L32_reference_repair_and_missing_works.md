# L32. Fix the manuscript's reference list: five candidate missing works, one suspect entry, one suspect sentence, and four uncited external sources

Paste `00_MASTER_BRIEF.md` first. Answer with the schema in `_RESPONSE_TEMPLATE.md`.

---

## Why this prompt exists

An external evaluator (Gemini, tasked separately with an outward-facing read of the manuscript,
`writing/IMP/IMP_01_GEMINI_manuscript_evaluation.md`) returned five candidate missing citations, one
suspect existing citation, and one suspect sentence in the reference-list preamble
(`writing/IMP/RIMP_01_2026-09-14.md`, section D). 🔴 **Deep research is external: none of that
evaluator's supplied metadata enters the manuscript until it has been independently resolved under
this project's own seven-step vetting protocol** (`DeepResearchPrompts/README.md`, "Vetting a
returned report"). This prompt is that independent resolution, not a rubber stamp of the evaluator's
claims. Treat every item below as a hypothesis to check, not a fact to format.

The manuscript's current reference list lives in `writing/submission/4J_manuscript_submission.md`,
section "# References" (13 entries, each already carrying a CrossRef DOI). Do not touch, reformat, or
re-verify those 13; they are out of scope for this prompt.

## Part A — five candidate missing works (verify each independently, do not trust the DOIs as given)

The evaluator named these five as works the paper's own claims depend on but does not cite. For each,
independently confirm (a) the work exists, (b) the DOI/identifier the evaluator gave actually resolves
to it via CrossRef (or the correct registration agency if not CrossRef), and (c) the paper's specific
claim near where it would be cited is what the work actually supports — do not just confirm the work
exists and stop there.

1. Loga, T., Stein, B., and Diefenbach, N. (2016). TABULA building typologies in 20 European
   countries — making energy-related features of residential building stocks comparable. *Energy and
   Buildings*, 132, 4-12. Evaluator-supplied DOI: `10.1016/j.enbuild.2016.06.094`. **This may be the
   same source as the "TABULA typology documentation" already named as uncited in the manuscript's own
   ⚠ block** (References section, final paragraph) — if so, say so explicitly; if it is a different
   TABULA document (e.g. the EPISCOPE/TABULA project's own synthesis report rather than this journal
   article), say that instead and give both.
2. Crawley, D. B., Lawrie, L. K., Winkelmann, F. C., Buhl, W. F., Huang, Y. J., Pedersen, C. O.,
   Strand, R. K., Liesen, R. J., Fisher, D. E., Witte, M. J., and Glazer, J. (2001). EnergyPlus:
   creating a new-generation building energy simulation program. *Energy and Buildings*, 33(4),
   319-331. Evaluator-supplied DOI: `10.1016/s0378-7788(00)00114-6`.
3. Shokri, R., Stronati, M., Song, C., and Shmatikov, V. (2017). Membership inference attacks against
   machine learning models. *2017 IEEE Symposium on Security and Privacy (SP)*, 3-18.
   Evaluator-supplied DOI: `10.1109/sp.2017.41`. The manuscript runs a loss-based membership-inference
   privacy audit (`G6.10`) — confirm this is the correct foundational citation for that method, not
   merely a plausible-sounding one.
4. Wilke, U., Haldi, F., Scartezzini, J.-L., and Robinson, D. (2013). A bottom-up stochastic model to
   predict building occupants' time-dependent activities. *Building and Environment*, 60, 254-264.
   Evaluator-supplied DOI: `10.1016/j.buildenv.2012.10.021`. Check specifically whether this
   duplicates or overlaps the already-cited Richardson et al. (2008/2010) and Widén and Wäckelgård
   (2010) stochastic-occupancy lineage already in the reference list — if it is redundant with what is
   already cited and adds nothing the paper needs, say so and recommend leaving it out.
5. Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., and Chen, W. (2021).
   LoRA: low-rank adaptation of large language models. *arXiv preprint*, arXiv:2106.09685.
   Evaluator-supplied identifier: `10.48550/arXiv.2106.09685`, flagged by the evaluator itself as
   resolving via DataCite, **not** CrossRef. This is the adapter method the manuscript's fine-tuning
   pipeline actually uses — confirm the identifier resolves via DataCite (arXiv DOIs do not carry
   CrossRef records) and give the correct registration agency in your answer rather than reporting
   CrossRef failure as if it were a defect in the citation.

For each of the five: report `RESOLVED` with the verified metadata and the URL you opened, or
`NOT FOUND` if you cannot independently confirm it. An unverified DOI copied from the evaluator's
report is worse than no citation — it would be a fabricated-looking reference in a paper that has
already had one citation-integrity problem (Part B below).

## Part B — the suspect existing citation

The current reference list carries:

> Vosoughkhosravi, S., Dixon-Grasso, L., and Jafari, A. (2023). The impact of occupancy on building
> energy performance: a review. *Energy and Buildings*. DOI: 10.1016/j.enbuild.2023.113245

The same external evaluator reported this entry as **a blend of two real papers** rather than one real
paper (`writing/IMP/IMP_PLAN_2026-09-14.md`, item E5). Independently determine:

1. Does DOI `10.1016/j.enbuild.2023.113245` resolve via CrossRef, and if so, to what title, authors,
   journal, volume/issue/pages, and year?
2. Does that resolved record match the citation exactly as printed in the manuscript (title, author
   list, journal)? Name every field that differs.
3. If it does not match, is there a real paper by an overlapping author set on this subject that the
   citation was likely meant to be, and does a second real paper exist that the manuscript's citation
   may have been merged with? Name both candidate papers with their own verified DOIs if you can find
   them, and say plainly if you cannot.
4. This citation supports a specific claim in the manuscript body — find where it is used (search
   "Vosoughkhosravi" in `4J_manuscript_submission.md`) and state whether the claim needs a citation at
   all, or whether it is better supported by one of the other twelve already-verified entries.

Do not repair this entry yourself in this report — report only what you can independently verify, and
mark unresolved which parts. The correction to the manuscript file happens after this report is vetted
under the seven-step protocol, not inside this prompt.

## Part C — the suspect preamble sentence

The reference list preamble currently reads: *"Every DOI below was resolved against CrossRef during
the pipeline's citation checks; four such checks are reported in this paper as not performed offline
and resolve online."* The evaluator flagged this sentence as false or unsupported. This part does NOT
need external search — it needs you to read two on-disk files and report a fact, so answer it from
what is enclosed with this prompt if the pipeline's citations.csv is provided to you, or say plainly
that you were not given it and cannot check this part.

Only `Step9_docs/outputs_step9/citations.csv` exists as an on-disk CrossRef-verification artefact
project-wide (four rows: CREST-2010, CREST-ACTIVITY-CODES, JORDAN-VAJEN-2001, FUENTES-2018 — the last
explicitly marked "CHECKED 2026-08-27 AGAINST CROSSREF"). No equivalent artefact was found on disk for
the other nine of the thirteen references currently in the manuscript's list (Beckman, Deville,
Lombardi, Lovelace, Osman and Ouf, Pflugradt, both Richardson entries, Widén and Wäckelgård). If that
remains true, the preamble sentence overclaims and should be corrected to name only what is actually
verifiable on disk, rather than asserting blanket CrossRef verification. State this plainly as your
finding for Part C; it does not need a search of the outside literature.

## Part D — closing the ⚠ block (four uncited sources already used in the text)

The reference list's final paragraph names four sources cited in the manuscript body but never
formatted in the reference list: the TABULA typology documentation, the three national time-use survey
user guides (Spain, UK, Italy), the Eurostat HETUS methodological guidelines (2000/2008/2018 rounds),
and the author's own prior published work in this series. For each:

1. **TABULA typology documentation** — likely resolved by Part A item 1 above (Loga et al. 2016) or by
   the IWU Darmstadt EPISCOPE/TABULA project's own published workbook (already used as a data source
   per `RL27`/`VETTING_RL27.md`, Wave 11's TABULA licence finding) — confirm which, or both, are the
   correct citation(s) and give full formatted references for both if they are distinct works.
2. **Three national survey user guides** — Spain's *Encuesta de Empleo del Tiempo*, the UK Time Use
   Survey documentation, and Italy's ISTAT *Uso del Tempo* survey documentation. Find the specific
   methodological/user guide document each national statistical institute publishes for the exact
   survey wave this project uses (ES 2009-10, UK 2014-15, IT 2013-14 — confirmed in `RL27`), not a
   different wave. Give a full formatted reference and URL for each of the three.
3. **Eurostat HETUS methodological guidelines** — the 2000, 2008 and 2018 guideline documents that
   `RL27` already found and used to establish the weighting mandate (`D-S6-4`). Give full formatted
   references for whichever of the three rounds the manuscript actually cites (check
   `4J_manuscript_submission.md` for which round(s) are named in text) — this may already be
   substantially answered by `RL27`'s own sourcing; if so, say so and just format it, rather than
   re-searching from scratch.
4. **The author's own prior published work in this series** — confirm with the author (this is the one
   item in this prompt that a deep-research tool cannot resolve on its own: name the exact prior
   paper(s) in the 2J/3J/4J house style this manuscript's introduction or discussion refers to, and
   supply the citation) if the master brief or its corrections do not already name it.

## What NOT to do

- Do not invent a DOI, a page range, or an author name for anything in this prompt. `NOT FOUND` beats
  a plausible guess, every time.
- Do not recommend changing any registered gate, band, or threshold — nothing here touches the
  pre-registered experiment.
- Do not draw conclusions about the paper's headline result; this prompt is reference hygiene only.
- No em dashes or en dashes anywhere in your answer.

---

## Registration

Written 2026-09-16, Wave 13. Not yet sent externally. When it returns, vet it under the seven-step
protocol before any of its metadata enters `4J_manuscript_submission.md`, and record the vetting
verdict as `VETTING_RL32.md`, same convention as `VETTING_RL27.md` / `VETTING_RL28_RL29.md` /
`VETTING_RL30_RL31.md`.
