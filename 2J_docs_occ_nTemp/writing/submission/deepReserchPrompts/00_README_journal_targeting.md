# Deep-Research Prompt Set — 2J JOURNAL TARGETING

### README — roster, shared facts, and run conventions for the `dr_2J-*` prompt files

**Purpose.** Decide **where to submit the 2nd journal paper**, and submit it in the form that journal
expects. Each prompt is a **standalone document** written to be fed whole into an external
deep-research tool (Gemini Antigravity / Deep Research). Format follows the `dr_L3-*` convention:
SCOPE GUARD → What / Role / Why → required output tables (fill every cell) → Part C synthesis →
exact output format → hard requirements.

**The manuscript under discussion** is
`2J_docs_occ_nTemp/writing/submission/2J_manuscript_submission.docx` (and its `.md` twin).

---

## Roster

| # | Prompt file | Question it answers | Blocks |
|---|---|---|---|
| dr_2J-01 | `dr_2J-01_journal_fit_shortlist_prompt.md` | Which journals actually publish this kind of paper, ranked by evidenced scope fit, with the acceptance-relevant metrics per journal | The submission decision itself |
| dr_2J-02 | `dr_2J-02_rejection_repositioning_prompt.md` | Why the Building and Environment attempt failed, what the top venues reject on, how to frame the cover letter and pick handling editors / suggested reviewers | Cover letter, framing, resubmission risk |
| dr_2J-03 | `dr_2J-03_submission_requirements_prompt.md` | The mechanical requirements of the top three venues (abstract cap, highlights, reference style, figures, data statement, preprint and self-citation policy) | Final file preparation before upload |
| dr_2J-04 | `dr_2J-04_results_synthesis_prompt.md` | Synthesize outputs from 01, 02, and 03 into a definitive submission decision, ready-to-use cover letter, abstract pruning log, and step-by-step submission build checklist | Execution and file package build |

**Run order: 01 → 02 → 03 → 04.** `dr_2J-01` produces the shortlist; `02` and `03` operate on the top three names that `01` returns, and `04` synthesizes all findings into the final submittable package.

---

## Shared facts every prompt assumes (embedded inline in each, repeated here for the record)

### The manuscript

- **Title.** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a
  Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*
- **Authors.** O.K. Iseri, C. Hachem-Vermette, Concordia University, Montreal, Canada.
- **Keywords.** Occupancy modelling; building performance simulation; time-use survey; load shape;
  peak demand; longitudinal forecasting; COVID-19 / work-from-home.
- **What it does.** Harmonises four Statistics Canada General Social Survey time-use cycles
  (64,061 diaries), augments them with a gate-selected hybrid AR/NAR conditional Transformer to
  ~192,183 calibrated diary-days, links them to a 144,507-household 2021 Census PUMF frame, forecasts
  the occupancy series **through** the COVID / work-from-home structural break to 2030 under a
  True-Future-Test protocol, and runs 6,000 paired EnergyPlus v24.2 simulations (fixed 50-household
  panels, archetypes and weather frozen) across four Canadian code archetypes and six ASHRAE climate
  zones. End uses are activity-resolved and calibrated to NRCan SHEU-2019 within ±2.7 % in all 48
  dwelling-by-year cells.
- **Headline results.** Weekday at-home occupancy breaks +5.2 pp at COVID and persists to 2030
  (+2.2 to +3.9 pp), while annual electricity moves only +1.4 to +2.6 % across the break. The load
  *shape* changes structurally: midday share +0.37 pp, load factor +0.012 (both CIs exclude zero),
  evening peak fixed at ~17:30, building-level peak shift 0 ± 1 h.
- **Character.** Methods-and-campaign paper with a national forecasting claim and grid-relevant
  load-shape metrics. It stops at load metrics: it does **not** simulate a grid, a tariff, a
  demand-response program, or a cost. That boundary matters for venue choice.
- **Length and format state.** Abstract 239 words; 5 main tables; 7 main figures; 9 supplementary
  figures; appendix tables A1 to A3, B1 to B2, C1 to C2, plus a deviations list. Three
  graphical-abstract candidates exist, none chosen.

### The publication line (this paper is the second of three)

| Paper | Title | Venue | Status |
|---|---|---|---|
| Journal Zero | (earlier occupancy work, see Google Scholar record) | **Energy and Buildings** (Elsevier) | Published |
| Journal One | *Longitudinal Analysis of Occupancy-Driven Energy Demand in Canadian Residentials* | **Journal of Building Performance Simulation** (Taylor and Francis) | Under review |
| **Journal Two** | **the manuscript above** | **to be decided — this prompt set** | Ready to submit |
| Journal Three | 4-channel mixed-use extension (residential + office + retail + hotel) | not yet | In progress |

**A prior submission to Building and Environment (Elsevier) was rejected.**
`[confirm]` — it is not recorded in this project which manuscript that rejection applied to (this one,
Journal One, or Journal Zero), nor whether it was a desk reject or a post-review reject. `dr_2J-02`
treats both readings; the user must confirm which before the cover letter is written.

### Constraints that shape the answer

- The predecessor (Journal One) is **still under review**, so it can only be cited as *under review*.
  Any venue that is uncomfortable with load-bearing citations to unpublished companion work is a
  higher-risk target. The manuscript already carries an explicit originality statement in §1.4 and a
  standalone version in `../01_originality_statement.md`.
- Three papers from one pipeline in adjacent venues invites a **salami-slicing** question. The venue
  choice and cover letter must pre-empt it.
- The authors are at a Canadian university; **APC affordability is a real constraint** and must be
  reported, not glossed.
- 🔴 **AUTHOR-STATED CONSTRAINT (2026-08-07): Energy and Buildings is NOT the preferred target.** The
  Journal Zero submission there required **four rounds of revision** before acceptance, and the authors
  do not want to repeat that process. Energy and Buildings must still be **scored and reported** as a
  benchmark, because it is the closest scope match on record, but it may not be ranked first unless the
  evidence is overwhelming, and the ranking must state explicitly what it would cost in fit to avoid
  it. **Review burden — number of revision rounds, review-cycle length, and reviewer-count practice —
  is therefore a first-class selection criterion in this set, not a footnote.**

---

## My own offline shortlist (NOT research, do not treat as evidence)

Written from prior knowledge before any search, recorded here so the returned report can be checked
against it rather than silently agreeing with it. Every line below is a **hypothesis for the research
to confirm or overturn**.

Revised 2026-08-07 after the author ruled Energy and Buildings out as first choice.

| Rank | Venue | Why | Main risk |
|---|---|---|---|
| 1 | **Building Simulation** (Springer / Tsinghua) | BPS-native; a 6,000-run EnergyPlus campaign with validation gates is its core readership; typically a tighter review cycle than the large Elsevier energy titles | Lower reach; may treat the forecasting claim as secondary |
| 2 | **Applied Energy** (Elsevier) | The load-shape, ramping and demand-response framing is exactly its language; national forecast to 2030 fits its scale | Selective, and it usually wants an energy-system or economic consequence the paper does not compute; revision burden could equal or exceed the one being avoided |
| 3 | **Sustainable Cities and Society** (Elsevier) | Stock-scale, urban, scenario-to-2030 | Broad scope can read as a poor fit for a single-country methods paper |
| 4 | **Journal of Building Engineering** (Elsevier) | Broad building-domain scope that comfortably holds a simulation-campaign methods paper | Less load-shape and demand-side readership; contribution may land as a case study |
| 5 | **Energy** (Elsevier) | National forecast plus demand-side framing | Building-simulation detail can read as out of scope |
| — | **Energy and Buildings** (Elsevier) | Closest scope match on record, and the group has published there | 🔴 **Author-excluded as first choice — four revision rounds on the prior submission.** Keep as a scored benchmark only |
| — | **Journal of Building Performance Simulation** | Strong methodological fit | Journal One is already there and under review — reviewer overlap plus salami perception |
| — | **Building and Environment** | — | Already rejected once in this line; avoid until `dr_2J-02` establishes which paper was rejected and why |

**My provisional recommendation, pending the report: Building Simulation as the primary target on fit
plus review burden, Applied Energy as the ambitious alternative if the paper is willing to add an
explicit grid-consequence framing, and Sustainable Cities and Society as the third. Energy and
Buildings is carried only as the benchmark the others must be measured against.**

---

## Conventions restated in every prompt

- A citation is not evidence until opened. Verify DOIs via `https://api.crossref.org/works/<DOI>`.
- `NOT FOUND` beats an invented number. Never guess an impact factor, an APC, or a decision time.
- Journal metrics must carry the **year and the source** (Clarivate JCR, Scopus CiteScore, or the
  publisher's own page) — never a number floating free.
- Keep **publisher-stated policy** and **observed practice** strictly separate.
- No em dashes and no en dashes in the returned text.
