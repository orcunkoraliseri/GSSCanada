# Deep-Research Prompt dr_2J-02 — REJECTION DIAGNOSIS, POSITIONING, AND HANDLING EDITORS

> SCOPE GUARD — READ FIRST. This is the **positioning** task of the 2J set. Its job is to establish
> what the target venues actually reject papers of this type for, what Building and Environment
> publishes and turns away in this exact space, which editor would handle the submission, who could be
> proposed as reviewers, and how the cover letter must pre-empt the series and self-citation questions.
> Do NOT re-derive the journal shortlist (that is `dr_2J-01`, which must be run first and whose top
> three names this prompt operates on), and do NOT compile formatting rules (that is `dr_2J-03`). See
> `00_README_journal_targeting.md` for the set's shared facts and conventions.

---

## What this document is

A positioning brief. The manuscript is finished; the risk is no longer the science but the framing.
Three facts drive this prompt:

1. **A submission in this line was rejected by Building and Environment.** `[confirm]` — the project
   record does not state which manuscript it was, nor whether it was a desk reject or a post-review
   reject. Treat both readings.
2. **The companion paper is still under review** at the Journal of Building Performance Simulation, so
   the manuscript's own predecessor can only be cited as *under review*. The manuscript carries an
   explicit originality statement in §1.4 for this reason.
3. **This is the second of three papers from a single pipeline**, which invites the salami-slicing
   question from any editor who notices.
4. 🔴 **Energy and Buildings, the closest scope match on record, is author-excluded as a target.** The
   group's prior paper there took **four rounds of revision**, and they do not want to repeat it. The
   shortlist `dr_2J-01` returns is therefore a *deliberately second-best-on-fit* list, which means the
   framing has to work harder: the cover letter must make the contribution legible to an editor whose
   journal is not the natural home for a survey-derived occupancy paper.

### The manuscript being positioned

- **Title.** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a
  Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*
- **Chain.** Four Statistics Canada GSS time-use cycles (64,061 diaries) harmonised and augmented by a
  gate-selected hybrid AR/NAR conditional Transformer; linked to a 144,507-household 2021 Census PUMF
  frame; forecast through the COVID / work-from-home break to 2030 under a True-Future-Test protocol;
  6,000 paired EnergyPlus runs, four Canadian archetypes, six ASHRAE climate zones; end uses calibrated
  to NRCan SHEU-2019 within ±2.7 % in all 48 cells.
- **Result.** Occupancy breaks +5.2 pp and persists; annual electricity moves only +1.4 to +2.6 %; the
  load *shape* changes structurally (midday share +0.37 pp, load factor +0.012, evening peak fixed at
  ~17:30, peak shift 0 ± 1 h).
- **The three attack surfaces a reviewer will aim at.** (a) *Single country, single survey* — is this
  generalisable or a national case study? (b) *No measured-energy validation* — end uses are calibrated
  to a national survey, not to metered load curves, so the load-shape claim is validated at the
  aggregate-magnitude level but not against measured diurnal profiles. (c) *A forecast to 2030 that
  cannot yet be falsified* — the True-Future-Test protocol is the answer, but a reviewer must be led to
  it.
- **The originality position, already written into §1.4.** The predecessor asked *how much* (five
  occupancy datasets versus one default schedule, six Montreal neighbourhood units, one climate zone,
  annual magnitude corrections and code factors). This paper asks *when* (cycle versus cycle paired
  within household, carried through the COVID break to 2030, four archetypes across six climate zones,
  end uses anchored to a national survey, diurnal load shape as the primary result).

## Role

Journal-strategy analyst and building-energy peer-review insider. Ground the rejection-pattern analysis
in published editorials, editor-in-chief notes, author guidelines on scope and rejection criteria, and
any journal-published statistics on desk-reject reasons. Ground the editor identification in the
journals' own live editorial-board pages. Ground the reviewer suggestions in real, currently active
researchers with verifiable recent publications in this exact area. Keep what a journal *states* about
rejection separate from what its *published record* implies.

## Why this matters (so you scope correctly)

A well-founded paper rejected on framing is expensive: months lost, and the second submission carries
the first rejection's reasoning invisibly. The authors already paid that cost once in this line. The
specific hazard here is that the paper's real contribution is a *pipeline*, and a pipeline paper reads
as either a major methods contribution or an unfocused system description depending entirely on how the
first two paragraphs of the cover letter and the abstract frame it. On top of that, a series of three
papers from one dataset, with the first still unpublished, is exactly the configuration that triggers
an editorial integrity query. Pre-empting it in the cover letter costs one paragraph; being asked about
it after submission costs a revision cycle or a rejection.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — What Building and Environment publishes and rejects in this space

| Question | Finding | Evidence (quote scope text or name articles) | Citation |
|---|---|---|---|
| Does B&E publish TUS-derived occupancy modelling? Name 2 to 4 articles, 2022 or later, or NONE FOUND |  |  |  |
| Does B&E publish stock- or urban-scale simulation campaigns? |  |  |  |
| Does B&E publish load-shape / peak-demand results, or does it treat those as an energy-systems topic? |  |  |  |
| Published desk-reject criteria or editorial statements on scope |  |  |  |
| Reported desk-reject rate / first-decision statistics, if published |  |  |  |
| Most likely reason a paper of this exact type is turned away there |  |  |  |

### Table 2 — Rejection patterns at the top three venues from `dr_2J-01`

One block per journal. Fill for each of the three names returned by `dr_2J-01`.

| Journal | Published scope-rejection criteria (quote) | Editorials or guidelines naming what they will not consider | Known reviewer complaints in this subfield (from published review-process studies, editorials, or retracted-scope notes) | What this manuscript most likely trips | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 3 — Handling editors

For each of the top three journals, name the specific editor whose portfolio covers occupant behaviour,
building simulation, or demand-side modelling. Use the live editorial-board page.

| Journal | Editor name | Title / role (EiC, Associate Editor, Subject Editor) | Stated subject portfolio | Their own recent work in this area (1 to 2 named papers with DOI) | Editorial-board page link |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 4 — Suggested reviewers (most journals request three to five)

Active researchers, no conflict of interest with Concordia University or with the authors, publishing
in this exact intersection since 2022. Give a mix of occupancy modelling, stock-scale simulation, and
load-shape / flexibility.

| Name | Affiliation | Country | Why they fit (a named recent paper + DOI) | Sub-area covered | Institutional email or profile page |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 5 — Series and self-citation policy

| Journal (top three + B&E) | Policy text on redundant / salami publication (quote) | Policy on citing manuscripts that are under review or unpublished | Does the submission system require declaring related submissions elsewhere? | Practical implication for this manuscript | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 6 — Anticipated reviewer objections and the evidenced rebuttal

| Objection | How likely (H/M/L) | Is it already answered in the manuscript, and where | The strongest published counter-argument or precedent (named paper doing the same thing and getting published) | Citation |
|---|---|---|---|---|
| Single country / single survey, so not generalisable |  |  |  |  |
| No validation against measured diurnal load data |  |  |  |  |
| A 2030 forecast cannot be validated |  |  |  |  |
| Load shape is an energy-systems topic, not a buildings topic |  |  |  |  |
| Incremental relative to the authors' own prior work |  |  |  |  |
| Synthetic / generated diaries are not real occupancy data |  |  |  |  |

---

## Part C — Synthesis (the framing verdict and cover-letter skeleton)

Give: (1) a **rejection post-mortem under both readings** — if the Building and Environment rejection
was this manuscript, what the evidence says the likely cause was and whether it is fixable by framing
alone; if it was a different paper in the line, whether B&E should be reconsidered at all and under what
conditions; (2) a **framing verdict**: the single sentence the cover letter must open with for the
top-ranked journal, and the one contribution that should be foregrounded (occupancy modelling versus
forecasting through a structural break versus load shape and peak); (3) a **cover-letter skeleton**,
paragraph by paragraph, that explicitly includes a paragraph pre-empting the series question and
positioning the under-review companion paper, drawing on the originality statement above; (4) an
**anti-salami argument in three sentences** that an editor could accept at face value; (5) a
recommendation on whether to **disclose the prior rejection** if the new venue shares a publisher with
Building and Environment (both Elsevier), and what the publisher's own policy says about transferred or
resubmitted manuscripts; (6) a **revision-burden mitigation note** — given the authors are avoiding
Energy and Buildings specifically because of a four-round revision process, name the things a cover
letter and a submission package can do to reduce the number of rounds at the chosen venue (for example
pre-empting the three attack surfaces above in a limitations paragraph, supplying the validation
evidence as reviewable supplementary material rather than on request, or answering the generalisability
question in the abstract), each with a reason to believe it helps rather than a guess.

## Output format (follow exactly)

1. **Lead with Tables 1 to 6 fully populated.**
2. Then Part C synthesis.
3. Quote policy text verbatim where a policy is claimed; paraphrase is not evidence of a policy.
4. **"Confidence and caveats":** which claim about a journal's rejection behaviour is least certain,
   given that most rejection data is not published.
5. **Reference list** — full citations, dates, URLs and DOIs. Editorial-board and policy links must be
   live pages.

## Hard requirements

- **Run `dr_2J-01` first.** Tables 2, 3 and 5 operate on the top three journals that prompt returns.
  Do not substitute your own shortlist.
- **A citation is not evidence until opened.** Verify every DOI via
  `https://api.crossref.org/works/<DOI>`; confirm each suggested reviewer's named paper exists and is
  theirs.
- **Never invent an editor, a reviewer, an affiliation, or an email.** A name that cannot be confirmed
  on a live institutional or editorial page is `NOT FOUND`.
- **Do not speculate about the specific rejection decision.** Report what the venue's published record
  and policies support, and label everything else as inference.
- **Do not propose weakening or hiding a limitation** to improve acceptance odds. The task is framing,
  not concealment. The known limitations (single country, no measured diurnal validation,
  unfalsifiable-until-2030 forecast) stay in the paper.
- **Stay on topic** — positioning, editors, reviewers, cover letter. No shortlist re-derivation, no
  formatting checklists.
- **No em dashes and no en dashes in the returned text.**
