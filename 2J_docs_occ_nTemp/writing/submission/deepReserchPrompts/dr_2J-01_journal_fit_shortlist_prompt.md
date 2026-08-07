# Deep-Research Prompt dr_2J-01 — TARGET-JOURNAL SHORTLIST for the 2nd journal paper (evidenced scope fit)

> SCOPE GUARD — READ FIRST. This is the **venue-selection** task of the 2J set. Its job is to return a
> ranked, evidence-backed shortlist of journals that demonstrably publish papers of this exact type,
> each with the metrics that decide a submission (scope fit shown by named recent articles, impact and
> CiteScore with year and source, APC and open-access route, time to first decision, and desk-reject
> risk). Do NOT diagnose the earlier Building and Environment rejection or draft cover-letter framing
> (that is `dr_2J-02`), and do NOT compile per-journal formatting rules (that is `dr_2J-03`). See
> `00_README_journal_targeting.md` for the set's shared facts and conventions.

---

## What this document is

A venue-fit brief. A completed manuscript is ready to submit and the target journal is the last open
decision. The authors have three prior data points in the same line: a published paper in **Energy and
Buildings**, a paper **under review at the Journal of Building Performance Simulation**, and a
**rejection from Building and Environment**.

> 🔴 **AUTHOR-STATED CONSTRAINT — READ BEFORE RANKING.** The Energy and Buildings paper required
> **four rounds of revision** before acceptance, and the authors do not want to repeat that process.
> **Energy and Buildings must still be fully scored in every table as the benchmark**, since it is the
> closest scope match on record, but it may **not** be placed at rank 1 unless the fit evidence is
> overwhelming and you say so explicitly. Consequently, **review burden is a first-class ranking
> criterion in this prompt** (Table 3A), alongside scope fit. Where avoiding Energy and Buildings costs
> fit, quantify that cost rather than hiding it.

The question is not "which journals exist in building
energy" — it is **which journals have actually published, in the last three to four years, papers that
combine time-use-survey-derived occupancy, a learned generative occupancy model, stock-scale building
energy simulation, and a diurnal load-shape or peak-demand result.** A journal that publishes three of
those four is a different risk from one that publishes all four.

### The manuscript being placed

- **Title.** *From "How Much" to "When": Forecasting the Residential Energy Load Shape from a
  Calibrated Behavioural Occupancy Time-Series (Canada, 2005 to 2030)*
- **Method chain.** Four Statistics Canada General Social Survey time-use cycles (64,061 diaries),
  harmonised and augmented by a gate-selected hybrid AR/NAR conditional Transformer to ~192,183
  calibrated diary-days; linked to a 144,507-household 2021 Census PUMF frame; forecast **through** the
  COVID / work-from-home structural break to 2030 under a True-Future-Test protocol; then 6,000 paired
  EnergyPlus v24.2 runs on fixed 50-household panels with archetypes and weather frozen, across four
  Canadian code archetypes and six ASHRAE climate zones. End uses are activity-resolved and calibrated
  to NRCan SHEU-2019 within ±2.7 % in all 48 dwelling-by-year cells.
- **Headline.** At-home weekday occupancy breaks +5.2 pp at COVID and persists to 2030, while annual
  electricity moves only +1.4 to +2.6 %. The load *shape* changes structurally: midday share +0.37 pp,
  load factor +0.012 (both CIs exclude zero), evening peak fixed at ~17:30, peak shift 0 ± 1 h.
- **What it deliberately does not do.** It does not simulate a grid, a tariff, a demand-response
  program, a retrofit economics case, or an emissions consequence. It stops at load-shape metrics and
  argues their relevance to ramping and demand response.
- **Keywords.** Occupancy modelling; building performance simulation; time-use survey; load shape;
  peak demand; longitudinal forecasting; COVID-19 / work-from-home.
- **Scale of the artefact.** Abstract 239 words; 5 main tables; 7 main figures; 9 supplementary
  figures; four appendix table groups.

## Role

Scholarly-publishing analyst with building-energy domain depth. Work from the journals' own aims and
scope pages and from their **actual recent contents** (not reputation), then from Scopus / Clarivate
metrics with the year stated, then from the publishers' author pages for APC and open-access route,
then from journal-reported or community-reported turnaround data. Treat "a journal that publishes
occupancy papers" and "a journal that publishes *this* paper" as different claims requiring different
evidence.

## Why this matters (so you scope correctly)

The authors have already spent one rejection in this line, and the manuscript sits in an awkward
middle: it is too simulation-heavy for a pure data-science venue, too behavioural for a pure
energy-systems venue, and too national-scale for a single-building BPS venue. A shortlist built on
reputation alone would repeat the rejection. What decides the outcome is whether a journal's recent
volumes contain **named articles** doing something structurally similar, and whether the editor
handling that section reads a national occupancy forecast as in-scope or as "not an energy-systems
contribution". Additionally, this is the **second of three papers from one pipeline**, with the first
still under review, so a venue's tolerance for companion papers and for load-bearing citations to
unpublished work is a selection criterion, not a footnote.

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — Candidate journals, aims-and-scope fit

At least ten candidates. Include, and explicitly score, all of: Energy and Buildings, Applied Energy,
Building Simulation, Journal of Building Performance Simulation, Sustainable Cities and Society,
Energy, Building and Environment, Energy Policy, Applied Energy Letters or equivalent short-format
outlets, Journal of Building Engineering, Buildings (MDPI), Energies (MDPI), Energy and AI, plus any
venue your search surfaces that the list misses.

| Journal | Publisher | Stated scope sentence that covers this paper (quote it) | Scope fit High / Med / Low + one-line reason | Does it publish stock- or urban-scale simulation? | Does it publish occupant-behaviour modelling? | Does it publish forecasting to a future year? | Source link |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

### Table 2 — Evidence of fit from actual recent contents (the decisive table)

For each journal scored High or Medium in Table 1, name **two to four real articles published in
2022 or later** that are structurally closest to this manuscript. If a journal has none, write
**NONE FOUND** — that is a finding, not a gap to be filled with a loose match.

| Journal | Article (authors, year, title) | DOI (verify via Crossref) | Which of the four elements it shares: TUS-derived occupancy / learned generative model / stock-scale simulation / load-shape or peak result | How close to this manuscript (1 to 5) | Citation |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 3 — Decision-relevant metrics

| Journal | JIF (year + Clarivate JCR edition) | CiteScore (year + Scopus) | Quartile / rank in its category | Acceptance rate if published | Median or reported time to first decision | Time to publication | Source for each figure |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

### Table 3A — REVIEW BURDEN (elevated to a ranking criterion by the author constraint)

The authors are trying to avoid a repeat of a four-revision-round process. Report what is knowable and
mark clearly what is not: most journals do not publish revision-round statistics, so distinguish
**publisher-reported figures**, **figures derivable from published articles' received / revised /
accepted date lines**, and **community-reported experience** (SciRev, Web of Science Reviewer Locator
data, author surveys, published editorials).

| Journal | Typical number of revision rounds (source + basis) | Median days submission to first decision | Median days submission to acceptance (derive from 5 to 10 recent articles' date lines and give the sample) | Typical reviewer count | Does it use "major revision" as a routine first outcome? | Any published editorial on review process or turnaround | Evidence class: publisher-reported / date-line-derived / community-reported |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

For the date-line derivation, list the articles used with their DOIs so the sample can be checked.

### Table 4 — Cost and access

| Journal | Subscription route available at no cost to author? | Gold OA APC (currency + year) | Hybrid OA APC | Any Canadian consortium / Concordia University read-and-publish agreement that waives or discounts the APC | Preprint policy (which servers, which version) | Source link |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

### Table 5 — Risk profile specific to this manuscript

| Journal | Desk-reject risk for a single-country methods paper (H/M/L) + why | Tolerance for citing a companion paper that is still under review | Attitude to companion / series papers from one pipeline (any published editorial or policy on salami slicing) | Expected reviewer complaint most likely to sink it | Source or basis |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

### Table 6 — RECOMMENDED RANKING (the deliverable)

Rank on **evidenced scope fit (Table 2) first, then review burden (Table 3A), then reach (Table 3)**.

| Rank | Journal | Role | Why it is at this rank (one paragraph each, below the table) | What the manuscript would have to change to fit it | Expected review burden |
|---|---|---|---|---|---|
| 1 |  | Primary target |  |  |  |
| 2 |  | Second choice if rejected |  |  |  |
| 3 |  | Third choice / methodological fallback |  |  |  |
| — | Energy and Buildings | **Benchmark only — author-excluded as first choice** | State how much fit is given up by not submitting here, in terms of Table 2 evidence |  |  |
| — |  | **Explicitly not recommended** and why |  |  |  |

---

## Part C — Synthesis (the placement verdict)

Give: (1) the ranked shortlist restated with justifications, each justification resting on **Table 2
named articles**, not on scope prose alone; (2) a **framing verdict** — for the top-ranked journal,
should the paper lead with the *occupancy-modelling* contribution, the *forecasting through a
structural break* contribution, or the *load-shape and peak* contribution, and what does that imply for
the title and abstract emphasis; (3) an **explicit test of the authors' own hypothesis**, which after the
Energy and Buildings exclusion is: *Building Simulation is the best combination of fit and review
burden, Applied Energy is the ambitious alternative if a grid-consequence framing is added, and
Sustainable Cities and Society is third.* Confirm or overturn it and say which evidence decides;
(3b) a **cost-of-exclusion statement** — how much evidenced fit is surrendered by keeping Energy and
Buildings off the target list, and whether any shortlisted venue matches it on Table 2 evidence while
carrying a lighter review burden; (4) a judgement on whether submitting to the **Journal of Building
Performance Simulation**, where the companion paper is currently under review, helps (topical fit,
editors already know the line) or hurts (reviewer overlap, salami perception), with any journal policy
you can find on the point; (5) whether any journal currently has an **open special issue** on occupant
behaviour, load flexibility, demand response, post-pandemic building operation, or urban building
energy modelling that this paper could target, with deadline and guest editors.

## Output format (follow exactly)

1. **Lead with Tables 1 to 6 fully populated.**
2. Then Part C synthesis.
3. Every metric carries its year and its source in the same cell.
4. **"Confidence and caveats":** which ranking position is least certain and what single piece of
   evidence would change it.
5. **Reference list** — full citations, dates, URLs and DOIs. Journal links must point to the live
   aims-and-scope or author-information page, not to a search page.

## Hard requirements

- **Table 2 is mandatory and decides the ranking.** A journal ranked High in Table 1 with `NONE FOUND`
  in Table 2 must be demoted, and the demotion stated.
- **A citation is not evidence until opened.** Verify every DOI via
  `https://api.crossref.org/works/<DOI>` and confirm the article is what the title suggests.
- **No fabricated precision.** Never invent an impact factor, an APC, an acceptance rate, or a decision
  time. `NOT FOUND` is the correct answer when the publisher does not disclose it, and a
  community-sourced estimate must be labelled as such.
- **Keep publisher-stated policy separate from observed practice** (for example a stated 30-day first
  decision versus reported author experience).
- **Do not recommend a venue on prestige.** Rank on evidenced fit first, then review burden, then reach.
- **Respect the author exclusion.** Energy and Buildings is scored everywhere but ranked first only
  against explicit, stated evidence. Do not quietly drop it from the tables either — the benchmark is
  what makes the other rankings meaningful.
- **Never present a revision-round or turnaround figure without its evidence class** (publisher-
  reported, derived from article date lines with the sample listed, or community-reported).
- **Stay on topic** — venue selection only. No cover-letter drafting, no rejection post-mortem, no
  formatting checklists.
- **No em dashes and no en dashes in the returned text.**
