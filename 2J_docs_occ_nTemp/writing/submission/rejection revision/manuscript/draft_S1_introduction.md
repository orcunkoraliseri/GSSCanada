# Title options

**Title (the revision plan's candidate):**
From "how much" to "when": occupancy-driven change in the Canadian residential load shape after
COVID-19, with work-from-home scenarios to 2030

**Alternative 1:**
From "how much" to "when": a scenario-based projection of the Canadian residential load shape
through the COVID-19 work-from-home break

**Alternative 2:**
When occupants come home: scenario-based projections of the Canadian residential electricity load
shape to 2030

(Author to choose one; see "Open for the author" below.)

---

# Section 1. Introduction

## 1.1 The performance gap and static occupancy schedules

The persistent gap between predicted and measured building energy use, the performance gap, remains a
central credibility problem for building performance simulation (de Wilde 2014); occupant behaviour is
now the largest identified unexplained driver (Yan et al. 2015; Hong et al. 2017), taken up directly by
IEA EBC Annex 66 and its successor Annex 79 (Yan et al. 2017; O'Brien et al. 2020). Routine practice
still relies on static, deterministic occupancy schedules drawn from reference standards, a poor fit
for residential buildings, where daily life follows individual routines rather than regulated
operation (Mahdavi et al. 2021). Fixed schedules miss day-to-day behavioural variability (Wilke, Haldi
and Robinson 2011; Elsayed et al. 2023): survey-derived occupancy profiles differ from standard
schedules by up to 41 percent at individual hours, a timing discrepancy, not an annual-energy one
(Mitra et al. 2020). Static schedules therefore carry a timing error an annual-total comparison cannot
reveal.

Timing matters because a home's daily load shape, not only its yearly sum, sets its contribution to
grid peak demand, the evening ramp, and demand-response suitability [CITATION NEEDED: source on why
residential load timing, not only annual energy, matters for grid peak, evening ramp and demand
response]. This study uses 2030 as its scenario horizon because it sits beyond the latest available
survey data, requiring an explicit assumption about how far the pandemic-era change has settled or
receded, and because 2030 is a commonly used planning horizon [CITATION NEEDED: source establishing
2030 as a recognized planning horizon, and the timing of the next comparable time-use survey cycle].

## 1.2 Two research tracks and the gap they leave open

Two research traditions address occupancy in building energy modelling and rarely meet. The first
builds high-fidelity stochastic occupant models, applied mostly to single buildings and already-elapsed
periods (Richardson, Thomson and Infield 2008; Widén and Wäckelgård 2010; Wilke et al. 2013; Aerts et
al. 2014), including a growing Canadian strand (Armstrong et al. 2009; Osman and Ouf 2021; Osman et
al. 2023; Ferreira et al. 2024). The second runs stock- and urban-scale energy engines across
thousands of dwellings but feeds them simplified, single-period schedules (Reinhart and Cerezo Davila
2016); Chen et al. (2022)'s paired stock-scale design is the closest precedent to this study.

Table 1 scores nine external studies and the authors' own prior work against six framework dimensions
(C1 to C6), present, absent or partial, by the written criterion given below the table, not an
unstated judgement call.

**Table 1. Framework dimensions: external competitors, the authors' own prior work, and this study.**

| Study | C1 Time-series occupancy | C2 Calibrated model | C3 Future-year scenario (pandemic break) | C4 Activity/end-use resolved | C5 Stock-scale | C6 Load-shape/peak |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Chiou et al. (2011) | check | cross | cross | check | cross | check |
| Widén and Wäckelgård (2010) | check | check | cross | check | cross | check |
| Reinhart and Cerezo Davila (2016) | cross | cross | cross | cross | check | cross |
| Fischer et al. (2020) | check | check | cross | check | cross | check |
| Motuzienė et al. (2022) | check | check | cross (footnote c) | cross | cross | cross |
| Chen et al. (2022, ResStock) | check | check | cross | check | check | check |
| Osman et al. (2023, Canada) | check | check | cross | check | cross | check |
| Yin et al. (2024) | check | check | cross | cross | cross | cross |
| Jalilian and Kamel (2025) | cross | cross | check | cross | check | cross |
| Authors' own prior line: companion journal manuscript, under review [STATUS TO CONFIRM BY AUTHOR], and companion conference study (Iseri and Hachem-Vermette 2026) | check | check | cross | cross | P | P |
| **This study** | **check** | **check** | **check** | **check** | **check** | **check** |

Column criteria (one footnote per column):

a. **C1.** Present when occupancy varies within the day, not only as one daily or annual value.
b. **C2.** Present when parameters are fitted or checked against measured or surveyed data. Chiou et
   al. (2011) derives loads directly from diaries with no fitted model (absent); Yin et al. (2024) fits
   trend statistics to four decades of survey cycles (present, despite no simulation), resolving a
   reviewer-flagged scoring inconsistency.
c. **C3.** Present only when the study projects to a stated year beyond its own data window. Motuzienė
   et al. (2022) predicts short-horizon pandemic occupancy, not a future year, so C3 is absent here
   (corrected from present in the archived table).
d. **C4.** Present when the model distinguishes specific activities, or the equipment and lighting
   loads they imply, not one presence indicator or total.
e. **C5.** Present when the study aggregates across many dwellings, not one or a few.
f. **C6.** Present when the study reports the sub-daily load curve or its peak, not only totals.

Chen et al. (2022) is the strongest external precedent, sharing five of six dimensions; the one it
lacks is C3, since it evaluates an already-elapsed period rather than carrying occupancy through the
pandemic break to a future year. That is the one axis of difference; no wider novelty claim is made.

The authors' own prior line would already score present on most dimensions, since it uses time-series,
calibrated occupancy at stock scale. It scores partial on stock-scale and load-shape focus (fewer
typologies, only a first look at peak timing) and absent on C3 and C4 (a same-period synthetic year,
presence-filtered end uses). The delta from that line is the pipeline-stage advances in Section 1.5,
not one more column; its publication status is unconfirmed and marked for the author.

## 1.3 Occupant behaviour is non-stationary

The assumption that occupant behaviour is stationary did not hold through the COVID-19 pandemic. Work
from home rose sharply, to roughly four times its pre-pandemic level: about 20 percent of full
workdays afterward, against 5 percent before (Barrero, Bloom and Davis 2021). Weekday electricity
profiles show a change associated with the pandemic and the shift to more work from home, the loss of
bimodal commuting peaks and a weekend-like weekday shape (Abdeen et al. 2021), with a weather-adjusted
increase of about 7.9 percent in electricity use associated with the pandemic period (Cicala 2023).
Occupancy-prediction models trained only on pre-pandemic data degrade sharply once this period is
crossed (Motuzienė et al. 2022), the problem a pre-pandemic-anchored projection would inherit.

What happens to work from home after 2022 is not settled by the material available here. This study
does not assume the pandemic-era at-home level holds unchanged to 2030; instead, the share of that
shift retained in 2030 is treated as an explicit, stated assumption tested across more than one value,
not a single predicted number [CITATION NEEDED: source on the post-2022 trajectory of work-from-home
prevalence in Canada or comparable economies, to justify the persistence range carried into the 2030
scenarios]. A pre-pandemic-anchored projection would instead carry the structural break as a
systematic bias, misjudging not only how much energy is used but when.

## 1.4 Departure from the authors' prior line

The present study departs from a specific prior line by the authors: a conditional variational
autoencoder, a generative model referred to here as a C-VAE, paired with a cluster-based scheme, used
to synthesize longitudinally consistent Canadian residential occupancy schedules from successive
General Social Survey cycles and carry them into building energy simulation. That line spans a journal
treatment across several Montreal neighbourhood-unit typologies (companion manuscript, under review), a
companion conference study across three climate-zone cities (Iseri and Hachem-Vermette 2026), and a
related population-statistics and machine-learning occupancy framework (Iseri, Dino and Kalkan 2026).

That line established what this paper does not re-claim: that survey-grounded, time-series occupancy
can be built for Canadian building energy models and moves predicted heating and cooling demand
relative to default assumptions, with a first look at diurnal and peak timing. The predecessor asked
how much, comparing period-specific occupancy datasets against one default schedule in one climate
zone, ending at a same-period synthetic year. This paper asks when: cycle-versus-cycle and
within-household rather than default-versus-cycle; occupancy carried through the pandemic break to a
stated future year, 2030; scope widened to several Canadian dwelling archetypes across multiple
climate zones; end uses anchored to a national household-energy survey rather than filtered from
default profiles; and the primary result is the diurnal load shape, not annual totals.

## 1.5 Aim and contributions of the present study

This paper asks whether, and how, occupancy-driven change reshapes the residential load curve at
stock scale, under explicit work-from-home scenarios carried to 2030.

The paper makes three scientific contributions: a generative occupancy model chosen from a broader
architecture search against distributional checks the prior C-VAE line did not apply, preserving
sharper within-day activity timing ([NUMBER FROM RESULTS] architectures searched); occupancy carried
through the pandemic break to 2030 under explicit scenarios, with the generator checked on a held-out
year (trained through 2015, tested on the unseen 2022 cycle) rather than on a same-period synthetic year; and attribution
from a paired, within-household stock-scale design holding the same households fixed across each
compared year pair, across multiple Canadian archetypes and climate zones ([NUMBER FROM RESULTS]
households per panel, [NUMBER FROM RESULTS] simulation runs).

It also makes two practical contributions: activity-resolved equipment and lighting loads checked
against a national end-use energy survey by dwelling type, a fitted-target check rather than an
independent validation of the sub-daily shape ([NUMBER FROM RESULTS] agreement across dwelling-by-year
cells); and diurnal load-shape metrics, load factor, midday energy share, and daily peak timing,
reported directly for grid ramping and demand-response planning rather than only annual totals.

None of these advances is specific to Canada: the pipeline needs a repeated national time-use survey,
a census-type household frame linking diaries to a dwelling stock, and a national end-use benchmark, a
trio supplied elsewhere by the American Time Use Survey (Chiou et al. 2011) and the Harmonised
European Time Use Survey (Eurostat 2018), whose guidelines the activity vocabulary here already
follows. What is country-specific is the calibration data and its magnitudes; the generator, the
held-out-year evaluation, and the paired design carry over unchanged.

The framework operationalizing this aim is in Section 2 (Sections 2.1 to 2.12); its limitations,
including scope, the scenario treatment of 2030, and the 2022 survey's collection-mode confound with
the pandemic-era shift, are stated in full in Section 7.

---

## Reviewer-item closure

| Item | Status | Paragraph that closes it |
|---|---|---|
| R2-5 (delete the "funnel" meta-paragraph; no self-description of structure) | CLOSED | No such paragraph exists anywhere in this draft; the section opens directly at 1.1. |
| R2-3 / R3-2 (no "forecast" anywhere; say "scenario-based projection") | CLOSED | The word "forecast" does not appear anywhere in this draft. Section 1.5 states the paper's own framing as "explicit scenarios"; the title options avoid the word by design. |
| R3-3 (no causal wording for the pandemic/WFH effect) | CLOSED | 1.3, paragraph 1: "a change associated with the pandemic," "an increase ... associated with the pandemic period"; no "caused by" construction is used anywhere. |
| R1-D3 (define C-VAE at first use) | CLOSED | 1.4, paragraph 1: "a conditional variational autoencoder, a type of generative model referred to here as a C-VAE." |
| R1-D4 (define "activity and end-use resolved" in one plain sentence at first use) | CLOSED | Table 1 column footnote d, and restated in Section 1.5's first practical contribution. |
| R1-D6 (one paragraph on why timing matters and why 2030) | CLOSED | 1.1, paragraph 2. Both the grid/demand-response claim and the 2030-horizon claim carry `[CITATION NEEDED]` tags since neither source is already cited in the archive. |
| R1-D5 and plan item 18 (Chen et al. 2022 differentiation, one axis only) | CLOSED | 1.2, paragraph 3 ("Chen et al. (2022) is the strongest external precedent, sharing five of six dimensions... the one it lacks is C3..."). |
| R1-D2 (Table 1 gains a row for the authors' own prior work; JBPS status unknown) | CLOSED | Table 1 gains one combined row (companion journal manuscript and companion conference study), marked `[STATUS TO CONFIRM BY AUTHOR]` for the journal manuscript; 1.2 paragraph 4 explains the scoring. |
| Plan item 10 / Q10 (Motuzienė row must not tick "forecast to future year," or the citing sentence softened) | CLOSED | Both done: Table 1's Motuzienė row scores C3 as cross (footnote c explains the correction), and 1.3's citing sentence ("Occupancy-prediction models trained only on pre-pandemic data...") already avoided over-claiming a future-year forecast. |
| Plan item 16 / Q17 (explicit scoring criteria per column; score Chiou 2011 and Yin 2024 by that rule) | CLOSED | Table 1 footnotes a to f give one criterion per column; footnote b applies the C2 criterion explicitly to Chiou et al. (2011) and Yin et al. (2024) and explains why they score differently. |
| Plan item 17 / Q18 (no 2030 number in the Introduction; qualitative aims only) | CLOSED | No numeric 2030 result appears anywhere in this draft. Section 1.5's aim sentence and contributions are stated qualitatively, with `[NUMBER FROM RESULTS]` placeholders standing in for every magnitude. |
| Plan item 19 / Q20 (do not state WFH persists unchanged; no "7.1%" figure; if decline is mentioned, use only dr_2J-11's quoted figures) | CLOSED | 1.3, paragraph 2, states explicitly that persistence is not assumed and is treated as a scenario question. The "7.1%" figure is not used anywhere. The specific post-2022 decline percentages found in `dr_2J-11_VETTING.md` are deliberately NOT quoted (see "Open for the author" below for why), so a `[CITATION NEEDED]` tag stands in their place instead of an unsourced or improperly-attributed number. |
| R1-D7 (contributions rewritten as 2 to 3 scientific and 2 practical statements, plain words, no un-re-derived numbers) | CLOSED | 1.5, paragraphs 2 to 3: three scientific and two practical statements, each in plain language with `[NUMBER FROM RESULTS]` placeholders in place of every magnitude carried over from the archive. |
| Plan item 13/14 spirit (never call the SHEU comparison "validation") | CLOSED | 1.5, first practical contribution: "a fitted-target check rather than an independent validation of the sub-daily shape," matching the wording already used in `draft_S2_framework.md:216`. |

## Number trace table

| Number | Where used | Source file:line |
|---|---|---|
| "up to 41 percent" (hourly discrepancy vs. reference schedules, Mitra et al. 2020) | 1.1, paragraph 1 | `archive/2J_manuscript_submission.md:65` |
| "roughly four times its pre-pandemic level: about 20 percent... against 5 percent before" (Barrero, Bloom and Davis 2021) | 1.3, paragraph 1 | `archive/2J_manuscript_submission.md:99` |
| "about 7.9 percent" weather-adjusted increase (Cicala 2023) | 1.3, paragraph 1 | `archive/2J_manuscript_submission.md:99` |
| "sharing five of six dimensions" (Chen et al. 2022 vs. this study) | 1.2, paragraph 3 | `archive/2J_manuscript_submission.md:84` (Table 1 row, as it stood) and `deepResearch/dr_2J-10_VETTING.md:146-150` (independent re-derivation of the 5-Y-1-N count) |
| "Sections 2.1 to 2.12" | 1.5, closing paragraph | `manuscript/draft_S2_framework.md:5-13` (framework's own eleven-stage description) |
| "Section 7" (limitations) | 1.5, closing paragraph | `manuscript/draft_S7_limitations.md:1` |
| `[NUMBER FROM RESULTS]` placeholders (4 instances: candidate architectures searched, households per panel, simulation runs, dwelling-by-year cell agreement) | 1.5, paragraphs 2 to 3 | Not sourced; deliberately left as placeholders per R1-D7, since this task does not re-derive campaign or search-scale numbers |

## Citations used

Already cited in the archive and reused here: de Wilde 2014; Yan et al. 2015; Hong et al. 2017; Yan
et al. 2017; O'Brien et al. 2020; Mahdavi et al. 2021; Wilke, Haldi and Robinson 2011; Elsayed et al.
2023; Mitra et al. 2020; Richardson, Thomson and Infield 2008; Widén and Wäckelgård 2010; Wilke et al.
2013; Aerts et al. 2014; Armstrong et al. 2009; Osman and Ouf 2021; Osman et al. 2023; Ferreira et al.
2024; Reinhart and Cerezo Davila 2016; Chen et al. 2022; Chiou et al. 2011; Fischer et al. 2020;
Motuzienė et al. 2022; Yin et al. 2024; Jalilian and Kamel 2025; Barrero, Bloom and Davis 2021; Abdeen
et al. 2021; Cicala 2023; Eurostat 2018; Iseri and Hachem-Vermette 2026; Iseri, Dino and Kalkan 2026.

**Deliberately dropped from the archive's set:** Guo et al. 2026 (archive line 99, cited there for
"shows every sign of persisting at a new hybrid-work equilibrium"). The Fable/Gemini vetting in
`dr_2J-10_dr2J-11_FABLE_VETTING.md` and `dr_2J-11_VETTING.md` §8 found this persistence framing
unsupported by the trajectory data both reports independently checked. Rather than keep the citation
attached to a claim the vetting found unsupported, or silently re-word what that source says without
re-reading it (out of scope for this task, no literature search), it is left out of this draft and the
persistence question is instead flagged `[CITATION NEEDED]` in 1.3. Flagged for the author below.

## CITATION NEEDED list

1. 1.1, paragraph 2: source establishing that residential load timing, not only annual energy, is
   material to grid peak demand, evening ramp and demand response.
2. 1.1, paragraph 2: source establishing 2030 as a recognized grid- or climate-planning horizon, and
   the timing of the next comparable time-use survey cycle.
3. 1.3, paragraph 2: source on the post-2022 trajectory of work-from-home prevalence in Canada or
   comparable economies, to justify the range of persistence assumptions carried into the 2030
   scenarios.

Total: 3.

## Open for the author

1. **Title choice.** Three options given above; none uses "forecast." Pick one or request a further
   alternative.
2. **JBPS companion manuscript's publication status.** Table 1's row for it is marked
   `[STATUS TO CONFIRM BY AUTHOR]`. If it has since been accepted, the row and its in-text description
   ("currently under review") both need updating together.
3. **The post-2022 work-from-home decline figures.** `dr_2J-11_VETTING.md` §8 quotes specific,
   already-Crossref-checked figures for both Canada (a series declining from 22.4 percent in May 2022
   to 18.7 percent in May 2024) and the United States (a comparable multi-year SWAA-survey decline
   series through 2026). This task deliberately did NOT insert those exact figures into the draft,
   because (a) the task's own citation rule only allows citations the archive already carries, and
   these specific data points are not yet attached to a properly formatted reference the archive
   cites, and (b) picking which of the two national series, or both, belongs in this Introduction
   versus the Discussion is a manuscript-design decision, not a text-drafting one. A `[CITATION
   NEEDED]` tag stands in their place. If the author wants these numbers in Section 1 rather than
   later, the manager should supply the properly formatted citation and confirm placement.
4. **`[NUMBER FROM RESULTS]` placeholders (4 total in Section 1.5).** These need the manuscript's own,
   already re-derived numbers substituted once WP10 or a later work package has them in hand; they
   were deliberately not filled from the archive per R1-D7's "no un-re-derived numbers" rule.
5. **Section numbering assumption.** This draft assumes the new manuscript's Section 2 is the
   framework (matching `draft_S2_framework.md`'s own header, "2. Proposed modelling and simulation
   framework") and Section 7 is limitations (matching `draft_S7_limitations.md`'s own header, "S7.
   Limitations"). No file was available in this task's scope confirming the numbering of the sections
   in between (results, discussion, etc.), so Section 1.5's closing paragraph only names Sections 2
   and 7, not any section in between. If that numbering is wrong, only the closing paragraph's two
   section references need correcting.

## WHAT I DID NOT VERIFY

- Did not re-open or re-read the full text of any external paper cited (Chen et al. 2022, Chiou et al.
  2011, Yin et al. 2024, Motuzienė et al. 2022, or any other). All descriptions of what these papers do
  are carried over from the archive's own existing text (lines 57-132) and from the two deep-research
  vetting files named in the task doc (`dr_2J-10_VETTING.md`, `dr_2J-12_VETTING.md`,
  `dr_2J-11_VETTING.md`), per the "text only, no literature search" instruction.
- Did not verify that the new, combined Table 1 row (companion journal manuscript and companion
  conference study) is scored correctly against the C1-C6 criteria beyond what the archive's own
  paragraph (lines 90, 105-107) states; the "P" marks on stock-scale and load-shape focus are a
  plain-language reading of "several Montreal neighbourhood-unit typologies" and "a first look at...
  peak consequences," not a re-check of either companion manuscript's own text.
- Did not confirm the exact manuscript-wide section numbering beyond what `draft_S2_framework.md` and
  `draft_S7_limitations.md`'s own headers state; see "Open for the author," item 5.
- Did not check this draft's wording for consistency against `draft_S7_limitations.md`'s own
  discussion of the 2030 scenario framing, the collection-mode confound, or the companion manuscript's
  status beyond what is already quoted above; a full cross-section consistency pass was out of this
  task's scope.
- Section 1's word count (title block plus Section 1 body, including Table 1 and its footnotes) is
  about 1,750 words, somewhat above the task's stated 1,300 to 1,700 aim, though well short of the
  archived Introduction's roughly 1,960 words. Cutting further risked losing required content (the
  six column-criteria footnotes, the JBPS row, or a reviewer-item closure), so this was left as is
  rather than cut blindly; flagged for the author or manager to accept or ask for a further pass.
- Confirmed by automated search (not just a manual read) that the word "forecast" does not appear
  anywhere in Section 1's body text, and that no em or en dash, no banned symbol (+, ±, ~, Δ), and none
  of the listed internal labels (J3, True-Future-Test, frozen frame, Tier-1/2/3, FailSafe,
  COLLECT_MODE, DDAY_STRATA, Step-8/9, occACT, "gate"/"gates") appear anywhere in Section 1's body
  text.
