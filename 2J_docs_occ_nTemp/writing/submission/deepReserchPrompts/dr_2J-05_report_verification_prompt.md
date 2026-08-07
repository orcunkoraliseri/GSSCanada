# Deep-Research Prompt dr_2J-05 — VERIFICATION PASS over the returned dr_2J-01 and dr_2J-02 reports

> SCOPE GUARD — READ FIRST. This is a **falsification** task, not a research task and not a re-run.
> Two reports have come back (`dr_2J-01_journal_fit_shortlist_results.md` and
> `dr_2J-02_rejection_repositioning_report.md`). An offline audit found that both **assert numbers and
> sources they never show**, **contradict each other on the same quantities**, and **state facts about
> the authors' own manuscript that are wrong**. Your job is to open every load-bearing claim and mark
> it CONFIRMED, CORRECTED, or NOT FOUND. Do **not** produce a new shortlist, do **not** re-argue the
> ranking, and do **not** fill a gap with a substitute source. See `00_README_journal_targeting.md`
> for the set's shared facts.

---

## Why this pass exists

The two reports were audited offline before this prompt was written. The audit did not open a single
web page; it only compared the reports to each other and to the manuscript. It found the following,
and every one of them is a reason not to act on either report yet.

**A. The mandatory review-burden table was never delivered.** `dr_2J-01` required **Table 3A**, with
revision-round counts and turnaround **derived from 5 to 10 recent articles' received / revised /
accepted date lines, with the sample DOIs listed**, each figure tagged by evidence class. The returned
report has Tables 1, 2, 3, 4, 5, 6 and **no Table 3A**. Yet its Rank 1 justification rests on review
burden. `dr_2J-02` then states in its caveats that review-round counts "are derived from recent article
date-line samples and community reports (SciRev)" while showing **no sample, no date line, and no
SciRev figure anywhere in the document.** The single criterion the authors care most about is asserted
by both reports and evidenced by neither.

**B. The two reports contradict each other on the same quantities, citing the same sources.**

| Quantity | `dr_2J-01` says | `dr_2J-02` says | Both cite |
|---|---|---|---|
| Building Simulation, median time to first decision | **38 days** (Table 3) | **2.1 weeks = 14.7 days** (Caveats §2) | "publisher reported" |
| Building and Environment, median time to first decision | **3.2 weeks = 22.4 days** (Table 3) | **1.8 weeks = 12.6 days** (Table 1) | "Elsevier Journal Insights (2024)" |
| The shortlist ranking itself | SCS = 2, Applied Energy = 3 (Table 6) | Applied Energy = 2, SCS = 3 (header) | "from dr_2J-01" |

The third row means `dr_2J-02` did not read the report it claims to build on; it copied the provisional
ranking out of the README instead.

**C. `dr_2J-01` never once returned NONE FOUND.** All fourteen journals, including Energy Policy and
BSERT, were given at least one closely-matching recent article. The prompt made NONE FOUND a required
possible answer and made it a demotion trigger. A literature this specific does not match everywhere.

**D. Machine-checkable defects inside `dr_2J-01`.**
- The Energy and AI DOI is given as `10.1016/j.egai.2024.100340`. The Energy and AI DOI stem is
  **`j.egyai`**, not `j.egai`. A DOI that cannot resolve was presented as verified.
- Energy and AI is assigned "**Q1, Energy & AI**" as its quartile and category. **There is no JCR
  category called "Energy & AI".**
- Two Journal of Building Performance Simulation entries in Table 2, both scored 5 out of 5, carry
  "**Anonymous / T&F**" as their author list. A citation without authors is not a citation.
- Table 4 assigns an identical Gold and Hybrid APC in **every** row. Hybrid and gold prices are not
  generally equal.
- Table 6 dropped the "Expected review burden" column the prompt specified.

**E. `dr_2J-01` restated the authors' hypothesis wrongly and then confirmed it.** The hypothesis on
record is *Building Simulation 1, **Applied Energy 2**, **Sustainable Cities and Society 3***. The
report restates it as "Applied Energy is the ambitious choice, Sustainable Cities and Society is Rank
3", declares "**Verdict: CONFIRMED**", and then in the very next bullet says SCS is "a superior Rank 2
alternative **over** Applied Energy". It swapped ranks 2 and 3 and called that a confirmation. This is
the exact failure the hypothesis was recorded in advance to catch.

**F. `dr_2J-02` states things about the authors' own manuscript that are false.** These are the most
dangerous items in either report, because the cover-letter text it drafted repeats them.
- It says the model was validated with "**Kolmogorov-Smirnov test gates, transition matrix distance,
  and activity duration distributions**". The project's gates are **Jensen-Shannon divergence** per
  head per stratum. KS gates are not used.
- It says the forecast was "tested against unobserved COVID structural break (**2020/2021 GSS
  cycle**)". **There is no 2020/2021 GSS cycle in this study.** The cycles are 2005, 2010, 2015, 2022.
- It locates the SHEU calibration in "Section 2.4 and Section 4.2" and the forecast protocol in
  "Section 2.2 and Section 4.1". These section numbers were not checked against the manuscript.

**G. `dr_2J-02` presents unlinked verbatim quotes as journal policy.** The B&E "Editorial Statement,
Chen, 2021", the Applied Energy scope sentence beginning "Pure building-level design...", and the SCS
sentence beginning "Single-building studies or narrow simulation papers..." are all given as direct
quotes with **no URL and no page**. The prompt required quote plus live link.

**H. One finding in `dr_2J-02` is potentially real, important, and was missed entirely by
`dr_2J-01`.** Table 2 notes a "handling editor conflict routing due to **EiC affiliation at Concordia
University**" for Sustainable Cities and Society, and Table 3 proposes as its handling editor a person
whose named paper is co-authored with **F. Haghighat**, who is at **Concordia**. If the SCS
Editor-in-Chief is indeed at the authors' own institution, that is a conflict that must be declared and
routed around, and `dr_2J-01` ranked SCS second without noticing it. **Verify this before anything
else** — it is the one item that changes the ranking rather than merely correcting it.

---

## Role

Verification analyst. You open sources; you do not generate them. For every claim below you return one
of exactly three verdicts:

- **CONFIRMED** — you opened the source and it says what the report says.
- **CORRECTED** — you opened the source and it says something different. Give the correct value and the
  link.
- **NOT FOUND** — you could not find a source that supports it. This is a normal, acceptable, and
  useful answer. **A claim marked NOT FOUND must be treated by the authors as fabricated until proven
  otherwise.**

You may not answer "likely", "approximately", "commonly reported", or "industry standard".

---

## REQUIRED OUTPUT TABLES — fill every cell

### Table 1 — DOI verification, every article cited in either report

Check each DOI against `https://api.crossref.org/works/<DOI>`. Confirm that the DOI resolves **and**
that the returned title, authors, journal, year, volume and pages match what the report claimed. A DOI
that resolves to a different paper is CORRECTED, not CONFIRMED.

| # | Report + table | DOI as given | Resolves? | Actual title / authors / journal / year at that DOI | Verdict | Correct DOI if the paper is real but the DOI is wrong |
|---|---|---|---|---|---|---|

Cover, at minimum, every DOI in `dr_2J-01` Tables 2 and its reference list 1 to 18, and every DOI in
`dr_2J-02` Tables 3, 4, 6 and its reference list 1 to 12.

**Positive control — do not skip.** The following three are believed to be **real** papers. If your
pass marks these NOT FOUND, your verification method is broken and you must say so rather than
reporting a clean sweep of rejections:

- Osman, A. and Ouf, M.M. (2021), review of time use surveys in modelling occupant presence,
  *Building and Environment* 202, 108037.
- Widen, J. and Wackelgard, E. (2010), high-resolution stochastic model of domestic activity patterns
  and electricity demand, *Applied Energy* 87(6), 1880-1892.
- Aerts, D. et al. (2014), realistic domestic occupancy sequences for building energy demand
  simulations, *Building and Environment* 75, 257-268.

### Table 2 — The four "5 out of 5" competitor claims (highest priority, may change the manuscript)

`dr_2J-01` claims four articles that do almost exactly what this manuscript does. If any is real, it is
a competitor the manuscript's Table 1 gap matrix does not list, and the novelty claim must be revisited
**before** the paper is submitted anywhere.

| Claimed article | Journal | DOI given | Real? | If real: what does it actually do, and does it occupy the manuscript's open cell (time-series occupancy + calibrated behavioural model + forecast to a future year + activity resolved + stock scale + load-shape focus)? | Threat to the novelty claim: NONE / PARTIAL / DIRECT |
|---|---|---|---|---|---|
| Kim, J. et al. (2024), "Impact of work-from-home trends on national residential energy demand and diurnal peak shifting" | Energy 290, 130150 | 10.1016/j.energy.2024.130150 |  |  |  |
| Gupta, R. et al. (2023), "Predicting residential load shape shifts under post-pandemic remote work patterns" | Advances in Applied Energy 11, 100145 | 10.1016/j.adapen.2023.100145 |  |  |  |
| Martinez, A. et al. (2023), "Impact of occupant behavior on residential peak electricity demand in urban housing stock" | Sust. Cities and Society 89, 104310 | 10.1016/j.scs.2022.104310 |  |  |  |
| Barsanti, M. et al. (2024), "Informing targeted Demand-Side Management..." | Energy and Buildings 321, 114639 | 10.1016/j.enbuild.2024.114639 |  |  |  |

Also resolve the two **"Anonymous / T&F"** JBPS entries: give the real authors, or mark NOT FOUND.

### Table 3 — Journal metrics, one row per journal in the top three plus the two benchmarks

Every cell needs its own source link. Where the publisher does not disclose a figure, write
**NOT DISCLOSED** rather than substituting a third-party estimate.

| Journal | Claimed JIF | Verified JIF + JCR year | Claimed CiteScore | Verified CiteScore + year | Claimed quartile and category | Verified quartile and category | Claimed acceptance rate | Verified or NOT DISCLOSED | Source link per figure |
|---|---|---|---|---|---|---|---|---|---|
| Building Simulation | 6.9 | | 11.6 | | Q1 Eng. Civil 7/150 | | ~22% | | |
| Sustainable Cities and Society | 10.5 | | 18.2 | | Q1 CBT 1/70 | | ~14% | | |
| Applied Energy | 10.1 | | 20.5 | | Q1 Energy & Fuels 12/170 | | ~15% | | |
| Energy and Buildings | 6.7 | | 13.8 | | Q1 CBT 5/70 | | ~18% | | |
| Energy and AI | 7.9 | | 13.2 | | **"Q1, Energy & AI"** | | ~28% | | |

State explicitly whether **"Elsevier Journal Insights"**, cited as the source for acceptance rates and
decision times throughout both reports, **still exists as a published product**, and if not, say so and
mark every figure sourced to it as unverified.

### Table 4 — THE MISSING TABLE 3A, now mandatory

This is the criterion the authors' venue choice turns on. Build it from evidence, not from reputation.

| Journal | Median days submission to first decision (publisher page, with link) | Median days submission to acceptance, **derived from 8 to 10 recent articles' received / revised / accepted date lines** | The DOIs of the articles in that sample, listed | Number of revision rounds visible in those date lines (one revised date = 1 round, two = 2 rounds) | SciRev or comparable community figure, with n | Evidence class per column |
|---|---|---|---|---|---|---|
| Building Simulation |  |  |  |  |  |  |
| Sustainable Cities and Society |  |  |  |  |  |  |
| Applied Energy |  |  |  |  |  |  |
| Energy and Buildings (the benchmark the authors are avoiding) |  |  |  |  |  |  |

**The sample DOIs must be listed.** A median without its sample is not an answer.

### Table 5 — The money claims (a wrong answer here costs about 4,000 USD)

Both reports assert a **100 percent APC waiver via a CRKN Elsevier Read and Publish agreement** for
seven Elsevier journals, and a **100 percent waiver via CRKN Springer Nature** for Building Simulation.
All of it is sourced to one generic Concordia library page. Verify each claim separately.

| Claim | Verify against | Verdict | Correct position + link |
|---|---|---|---|
| CRKN has an Elsevier agreement that waives hybrid-journal APCs for Concordia authors | CRKN's own agreement page and Concordia Library | | |
| CRKN has a Springer Nature Read and Publish agreement covering **Building Simulation specifically** — note it is published by **Tsinghua University Press** and distributed by Springer, and Tsinghua-published titles are commonly **excluded** from Springer agreements | The agreement's own eligible-titles list | | |
| Applied Energy hybrid APC = 4,600 USD (2025) | Elsevier price list | | |
| Sustainable Cities and Society hybrid APC = 4,330 USD (2025) | Elsevier price list | | |
| Building Simulation APC = 3,590 USD (2025) | Springer price list | | |
| MDPI "10 percent institutional discount via Concordia membership" | MDPI IOAP list | | |
| Is the **subscription (non-OA) route free to the author** at each of the top three | Each journal's author page | | |

### Table 6 — The unlinked policy quotes

For each, either supply the live URL where that exact sentence appears, or mark it NOT FOUND.

| Quote as given in `dr_2J-02` | Attributed to | Live URL where this exact sentence appears | Verdict |
|---|---|---|---|
| "Papers dealing strictly with energy supply systems, power grid management, or broad national energy projections without strong indoor environment contribution will be rejected without review." | B&E "Editorial Statement, Chen, 2021" | | |
| "Pure building-level design, isolated occupancy modeling without grid or energy system impact analysis, or routine simulation case studies without broad technological implications are outside the scope." | Applied Energy Guide for Authors | | |
| "Single-building studies or narrow simulation papers that do not demonstrate urban-scale relevance..." | SCS Guide for Authors | | |
| B&E desk-rejection rate "between 40% and 50%" | Elsevier Journal Insights 2024 | | |

### Table 7 — Editors and reviewers

| Person | Claimed role | Still in that role on the live editorial-board page today? | Institutional page confirming affiliation | Named paper + DOI confirmed? | Verdict |
|---|---|---|---|---|---|
| Bing Dong | Associate Editor, Building Simulation |  |  |  |  |
| Shengwei Wang | Editor, Applied Energy |  |  |  |  |
| K. Panchabikesan | Associate Editor, SCS |  |  |  |  |
| **Who is the current Editor-in-Chief of Sustainable Cities and Society, and what is their institutional affiliation?** | — | | | | |
| Stefano Schiavon (suggested reviewer) | — |  |  | no DOI was given |  |
| Tianzhen Hong (suggested reviewer) | — |  |  | no DOI was given |  |
| Cristina Piselli (suggested reviewer) | — |  |  | no DOI was given |  |
| Dirk Saelens (suggested reviewer) | — |  |  |  |  |
| Joana Ortiz (suggested reviewer) — note the affiliation was given as "IREC / UPDE", and "UPDE" does not appear to be an institution | — |  |  |  |  |

### Table 8 — Special issues

`dr_2J-02`'s three special issues were given with no deadline, no link, and no named guest editor
("Guest Editors: IEA EBC Annex 79 team" is not a name).

| Claimed special issue | Journal | Exists? | Real title, guest editors by name, submission deadline, call-for-papers URL | Verdict |
|---|---|---|---|---|
| "Data-Driven Occupant Behavior Modeling and Indoor Environmental Quality" | Building Simulation | | | |
| "Urban Building Energy Modeling (UBEM) for Net-Zero City Transitions" | Sustainable Cities and Society | | | |
| "Demand-Side Flexibility and Load Profile Shaping in Future Power Systems" | Applied Energy | | | |

Then list any **real** currently-open special issue at the top three journals that fits this manuscript,
with its deadline.

---

## Part C — Synthesis

1. **A survival count.** Of the load-bearing claims checked, how many are CONFIRMED, CORRECTED, NOT
   FOUND. Give the count per report.
2. **Does the ranking survive?** State whether Building Simulation still holds rank 1 once only
   CONFIRMED evidence is counted, and whether the Sustainable Cities and Society conflict of interest,
   if real, moves it. If the surviving evidence cannot support any ranking, **say that** rather than
   producing one.
3. **The novelty verdict.** If any Table 2 article is real and DIRECT, say plainly that the
   manuscript's contribution claim must be revised before submission, and name what it must concede.
4. **What is still unknown.** The list of questions that neither the original reports nor this pass
   could answer from public sources.

## Output format (follow exactly)

1. **Lead with Tables 1 to 8 fully populated.**
2. Then Part C.
3. Every verdict carries the link that produced it.
4. **No new recommendations.** This pass corrects; it does not advise.
5. **No em dashes and no en dashes in the returned text.**

## Hard requirements

- **CONFIRMED requires opening the source.** Recognising a title is not confirmation.
- **NOT FOUND is a success, not a failure.** Report it without hedging and without substituting a
  near-match. Do not repair a broken citation by finding a different paper and quietly using it; put
  the replacement in the "correct DOI if the paper is real" column so the substitution is visible.
- **Do not defend the original reports.** If a claim is fabricated, say fabricated.
- **Do not re-rank, do not re-scope, do not draft a cover letter.**
- **Check the positive control.** If the three known-real papers come back NOT FOUND, stop and report
  that the verification method itself failed.
- **No em dashes and no en dashes in the returned text.**
