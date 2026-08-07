# Deep-Research Prompt dr_2J-04 — SYNTHESIS: the submission decision, the cover letter, the build checklist

> SCOPE GUARD — READ FIRST. This is the **synthesis and execution** task of the 2J set, and the only
> one that is **not** a research task. Its job is to take the three returned reports (`dr_2J-01`,
> `dr_2J-02`, `dr_2J-03`) and collapse them into four deliverables: a **single named target journal**
> with a stated second and third choice, a **ready-to-paste cover letter**, an **abstract pruning log**
> that hits the target journal's word cap, and a **step-by-step build checklist** for the upload
> package. Do NOT open new lines of research, do NOT re-rank the shortlist from scratch, and do NOT
> introduce a journal that none of the three reports evaluated. See `00_README_journal_targeting.md`
> for the set's shared facts and conventions.

---

## What this document is

An execution brief. By the time this prompt runs, three reports exist and they will not agree
perfectly: `dr_2J-01` ranks on fit and review burden, `dr_2J-02` ranks on framing risk and editor
match, and `dr_2J-03` ranks on how much work the package needs. **A journal can win one and lose
another.** This prompt exists to resolve that, in the open, with the trade-off stated rather than
averaged away.

### Inputs (paste all three below this prompt before running)

1. `RV_2J-01` — the journal fit shortlist report
2. `RV_2J-02` — the rejection diagnosis and positioning report
3. `RV_2J-03` — the submission requirements report

**If any of the three is missing, stop and say so.** Do not synthesise from two.

### The manuscript being placed

- **Title.** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a
  Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*
- **Authors.** O.K. Iseri, C. Hachem-Vermette, Concordia University, Montreal, Canada.
- **Chain.** Four Statistics Canada GSS time-use cycles (64,061 diaries) harmonised and augmented by a
  gate-selected hybrid AR/NAR conditional Transformer to ~192,183 calibrated diary-days; linked to a
  144,507-household 2021 Census PUMF frame; forecast through the COVID / work-from-home break to 2030
  under a True-Future-Test protocol; 6,000 paired EnergyPlus v24.2 runs, four Canadian archetypes, six
  ASHRAE climate zones; end uses calibrated to NRCan SHEU-2019 within ±2.7 % in all 48 cells.
- **Headline.** Occupancy breaks +5.2 pp at COVID and persists to 2030 (+2.2 to +3.9 pp); annual
  electricity moves only +1.4 to +2.6 %; the load *shape* changes structurally (midday share +0.37 pp,
  load factor +0.012, both CIs exclude zero; evening peak fixed at ~17:30; peak shift 0 ± 1 h).
- **Current abstract: 239 words, unstructured, single paragraph.** It must be cut to whatever cap
  `dr_2J-03` reports for the chosen journal.
- **The originality position** is already written into §1.4 and exists standalone at
  `../01_originality_statement.md`: the predecessor asked *how much*, this paper asks *when*.

### Constraints that must survive the synthesis

- 🔴 **Energy and Buildings is author-excluded as the target** (four revision rounds on the group's
  prior paper there). It may appear as the benchmark the decision is measured against; it may not be
  the recommendation.
- The companion paper is **still under review**, so it can only be cited as *under review*.
- This is **paper two of three from one pipeline** — the cover letter must pre-empt the salami
  question.
- A prior submission in this line was **rejected by Building and Environment**; which manuscript that
  was is `[confirm]` and may still be unresolved when this runs. **If it is still unresolved, produce
  the cover letter in both variants** rather than picking one.

## Role

Submission strategist and scientific editor. You are not searching; you are adjudicating between three
reports and drafting. Where the reports conflict, name the conflict, state which report's evidence
class is stronger, and decide. Where they agree, do not re-argue the point. Where they are all silent,
say so rather than filling the gap from general knowledge.

## Why this matters (so you scope correctly)

Three good reports and no decision is a common and expensive outcome: the authors read them, feel
better informed, and still do not upload anything. The deliverable here is not analysis. It is a
journal name, a letter that can be pasted into a submission form, an abstract that fits, and a list of
files to produce. Anything that does not serve those four is out of scope.

The second reason this prompt exists is that the three reports optimise different things and can point
at different journals. Averaging them silently would hide exactly the trade-off the authors need to
see — for example a venue with the best scope evidence but a heavier review burden than the one they
just walked away from, which would defeat the entire point of the exclusion.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Cross-report agreement matrix

| Journal (every journal that appears in the top three of any report) | `dr_2J-01` rank + its basis | `dr_2J-02` verdict (framing risk, editor match) | `dr_2J-03` verdict (package effort, blocking gaps) | Agreement: UNANIMOUS / SPLIT / CONFLICTED | If split, which report's evidence is stronger and why |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 2 — THE DECISION

| Slot | Journal | The single strongest reason (cite which report and which table) | The strongest argument against it, stated fairly | What tips it |
|---|---|---|---|---|
| **Target** |  |  |  |  |
| Second choice, if rejected |  |  |  |  |
| Third choice |  |  |  |  |
| Benchmark not pursued (Energy and Buildings) | Energy and Buildings | How much fit is being given up | — | Author exclusion |

### Table 3 — Abstract pruning log (current: 239 words → target: the cap from `dr_2J-03`)

Work sentence by sentence on the current abstract. Do not rewrite it into new prose from scratch; cut
and compress, so the surviving claims remain exactly the ones the paper proves.

| # | Sentence (first 8 words) | Words | Claim it carries | Load-bearing for the contribution? YES / NO | Action: KEEP / COMPRESS / CUT | Words after |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

Follow the table with the **full rewritten abstract** and its exact word count. If the target journal
requires a structured abstract, give the structured version too, with its headings.

### Table 4 — Package build checklist

Every file the submission system will ask for, in upload order.

| # | File / item | Source (existing file in `writing/submission/`, or must be created) | Journal requirement it satisfies (cite `dr_2J-03`) | Status: READY / NEEDS EDIT / MUST CREATE / BLOCKED ON USER | Action |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Include at minimum: manuscript file in the required format, title page or blinded variant, abstract,
highlights, keywords, figure files at the required resolution, table files, supplementary material,
graphical abstract, cover letter, suggested reviewers list, data availability statement, CRediT
statement, declarations, ORCIDs.

### Table 5 — Blocked on the user

The decisions no report can make. Keep this short and make each one answerable in one line.

| # | Open item | Why it cannot be resolved from the reports | What the user must decide | Blocks upload? YES / NO |
|---|---|---|---|---|
| 1 | Department / institute line and both ORCIDs (`[confirm]` in front matter) |  |  | YES |
| 2 | Which manuscript the Building and Environment rejection applied to |  |  |  |
| 3 | Venue and status of the companion paper cited as *under review* |  |  |  |
| 4 | Which of the three graphical-abstract candidates to use |  |  |  |
| 5 | (add any further items the reports surface) |  |  |  |

---

## Part C — The deliverables

### C1. The decision, in one paragraph

Name the journal. State the two strongest reasons and the one real cost of the choice. Do not hedge
across two journals.

### C2. The cover letter, ready to paste

Addressed to the named handling editor from `dr_2J-02` Table 3 where one was identified. It must
contain, in this order:

1. What the paper does and its single headline result, in two sentences.
2. Why this journal specifically, referencing the kind of work it publishes rather than flattering it.
3. The contribution, stated as the open cell no existing work occupies.
4. **The originality and series paragraph** — the relationship to the companion paper still under
   review, drawn from `../01_originality_statement.md`, and a three-sentence anti-salami argument.
5. The declarations the journal requires in the letter (originality, not under consideration
   elsewhere, all authors approve).
6. Suggested reviewers, if the journal takes them in the letter rather than the form.

Produce **both variants** if the Building and Environment `[confirm]` is still open: one that discloses
a prior rejection at a same-publisher journal, one that does not, each labelled with the condition
under which it applies.

### C3. The submission-day sequence

An ordered, checkable list from "open the submission system" to "click submit", with the Table 4 items
slotted into it and the Table 5 blockers marked at the point where they would stop progress.

### C4. What to do if it is rejected

The three concrete changes to make before sending it to the second-choice journal, ranked by how much
they would have helped at the first, drawn from `dr_2J-02` Table 6.

## Output format (follow exactly)

1. **Lead with Tables 1 to 5 fully populated.**
2. Then Part C, sections C1 to C4 in order.
3. The cover letter must be plain, pasteable text with no placeholders other than the ones the user
   must fill (marked `[ ]`), and no em dashes or en dashes.
4. **"Confidence and caveats":** the one part of the decision most likely to be wrong, and the one
   piece of information that would change it.
5. **No new reference list.** Cite the three input reports by name and table number instead.

## Hard requirements

- **Synthesise only.** Every claim must trace to `dr_2J-01`, `dr_2J-02`, `dr_2J-03`, or the manuscript
  facts stated above. If none of them covers a point, write **NOT COVERED BY THE REPORTS** rather than
  supplying it from general knowledge.
- **Do not average a conflict away.** A journal that wins on fit and loses on review burden must be
  reported as exactly that, with the trade-off named in Table 1.
- **Do not reintroduce Energy and Buildings as the recommendation.**
- **Do not weaken a limitation to strengthen the letter.** The known limitations stay in the paper:
  single country, no measured diurnal validation, a 2030 forecast that cannot yet be falsified.
- **The rewritten abstract must not add a claim the paper does not prove.** Cutting is allowed;
  strengthening is not. Every number in the new abstract must appear in the manuscript unchanged.
- **State the final word count of the abstract and confirm it against the journal's cap.**
- **No em dashes and no en dashes in the returned text.**
