# Deep-Research Prompt R3 — Is there a principled minimum donor-pool size in statistical matching and hot-deck imputation?

> SCOPE GUARD, READ FIRST. This is a **method-justification** task for a peer-reviewed
> building-simulation paper that uses statistical matching to link two microdata files. The
> deliverable is **whether the matching / hot-deck imputation literature gives a defensible rule for
> the minimum number of candidate donors in a matching cell, decidable without reference to the
> downstream validation metric**. It is NOT about record linkage for identity resolution (Fellegi-Sunter
> probabilistic linkage of the same entity across files), not about propensity-score matching for
> causal inference, and not about nearest-neighbour algorithms in machine learning generally. If you
> find yourself writing prose about anything other than **how many donors a cell must contain, why,
> and how that number is chosen in published practice**, stop and return to the tables.

---

## Why this matters to the paper

The pipeline links Statistics Canada Census public-use microdata (the recipient file: demographic
agents needing behavioural profiles) to a pool of ~192,000 augmented time-use diary-days (the donor
file). The match is a four-tier hierarchical key-descent: Tier 1 requires exact agreement on seven
demographic keys plus a day-type stratum; failing that, Tier 2 on four keys plus stratum; Tier 3 on
three; Tier 4 (stratum only) exists as a backstop.

Within a tier, a recipient draws a donor from the candidate pool for its key combination. The
implementation carries a parameter `MIN_POOL`: if a cell's candidate pool is smaller than `MIN_POOL`,
the match falls through to a broader tier rather than drawing from the thin cell.

**`MIN_POOL` was selected by which value made a downstream validation gate pass.** The internal log
states the objective verbatim: *"smallest `MIN_POOL` that flips W1 FAIL→PASS"*, where W1 is the
per-slot maximum deviation in synthetic-versus-observed at-work presence, gated at ≤ 3.0 pp. The sweep:

| MIN_POOL | AT_HOME deviation | AT_WORK deviation (the gate) | Colleagues | AT_RETAIL |
|---|---|---|---|---|
| 10 | 6.10 pp | **3.13 pp — FAIL** | 0.870 | 4.402 |
| 11 | 6.29 pp | 2.97 pp — PASS | 0.751 | 5.511 |
| 12 | 4.37 pp | 2.47 pp — PASS | 0.714 | 5.292 |
| **15 (shipped)** | 3.66 pp | 2.05 pp — PASS | 0.888 | 4.796 |
| 20 | 4.86 pp | 2.98 pp — PASS | 0.200 | 4.815 |
| 30 | 5.78 pp | **3.81 pp — FAIL** | n/a | 6.161 |

Note the non-monotonicity: the gate fails at 10, passes across 11–20, and fails again at 30. Donor
assignments — and therefore published results — differ between settings.

This is selection of a model hyperparameter on the evaluation metric, and a reviewer will say so. The
paper needs one of two things: **an independent criterion that selects `MIN_POOL` without looking at
the validation gates**, or **a defensible statement that the result is stable across the plausible
range**. This prompt is about the first.

## Role

You are a survey-methodology statistician. Every rule you report must cite a named, dated source: a
statistical agency methodology manual, a peer-reviewed methods paper, a standard reference text on
statistical matching or imputation, or documented software defaults with their stated rationale. A
software default with no published rationale should be reported as such and labelled.

---

## Part A — The deliverable table

| Source | Year | Domain | Rule for minimum donors per cell | Stated rationale | Is the rule decidable without the outcome metric? | Notes |
|---|---|---|---|---|---|---|

Sources to check by name, and say explicitly if one does not give a rule:

1. **D'Orazio, Di Zio & Scanu**, *Statistical Matching: Theory and Practice* — the standard reference.
   Does it state a minimum-donor rule, and if so on what grounds?
2. **Rässler**, *Statistical Matching* (multiple imputation perspective).
3. **Andridge & Little (2010)**, "A Review of Hot Deck Imputation for Survey Non-response" — the key
   review. What does it say about donor pool size, donor reuse limits, and adjustment cell
   construction?
4. **Statistics Canada** methodology documentation — the agency behind both files in this study. Does
   any Statistics Canada manual, the Generalized Edit and Imputation System (GEIS/BANFF)
   documentation, or a published methodology paper state a minimum cell size for donor imputation?
   A Canadian source would carry the most weight here.
5. **US Census Bureau / BLS** imputation methodology, and the **CPS/ATUS** matching documentation.
6. **Eurostat** methodological manuals on statistical matching of social surveys.
7. **Software defaults with published rationale:** R `StatMatch`, `hotdeck` implementations, SAS
   `PROC SURVEYIMPUTE`, `mice` donor options (`donors = 5` in predictive mean matching is a well-known
   default — what is its published justification, and does it transfer?).
8. The **predictive mean matching** literature specifically on the number of donors *k* — Morris, White
   & Royston (2014) and successors have studied this directly and empirically.

## Part B — The four questions the paper needs answered

Each in one short paragraph, with citations.

1. **Does a principled minimum-donor rule exist at all?** Or is minimum cell size in practice always a
   judgement call trading bias against variance, chosen by the analyst? If it is always a judgement
   call, say so — that is a defensible position for the paper to occupy, provided it says so
   explicitly rather than presenting a tuned number as a determined one.

2. **What criteria are used, other than downstream fit?** Candidates the paper could adopt: donor
   reuse frequency (how many times one donor is drawn), effective donor diversity per cell, variance
   inflation from repeated donors, a minimum expected number of distinct donors, cell-collapsing rules
   from the adjustment-cell literature. Which of these are published, and with what recommended
   thresholds?

3. **What does the literature say about the bias–variance trade-off in `MIN_POOL` specifically?** A
   small pool preserves demographic specificity but risks drawing an atypical donor; a large pool
   reduces variance but dilutes the match keys. Is the optimum known to be interior, and is
   non-monotonic behaviour of a downstream statistic across pool sizes a recognised symptom of
   draw noise rather than a real effect?

4. **How is the practice of tuning a matching parameter on a validation metric regarded?** Is there a
   documented recommendation — from the matching literature or from the reproducibility/pre-registration
   literature applied to survey methods — on how to select such a parameter defensibly, and how to
   report it once selected? What is the accepted way to present a parameter sweep as a sensitivity
   analysis rather than as a search?

## Part C — Recommendation for this study

Given what you find, state:

1. Which single independent criterion this study should use to select `MIN_POOL`, with its source.
2. What the criterion would most likely select given a donor pool of ~192,000 diary-days, a recipient
   file of ~30,000 agents, and a four-tier key-descent structure whose tier distribution is roughly
   Tier-1 45 %, Tier-2 21 %, Tier-3 34 %, Tier-4 0 %.
3. Whether the observed non-monotonicity (FAIL at 10, PASS at 11–20, FAIL at 30, on a 3.0 pp gate with
   crossings 0.13 pp and 0.81 pp deep) supports the reading that the gate is moving inside draw
   noise. If so, what the correct reporting is: a seed-spread interval rather than a point PASS.
4. Exactly how the paper should word the `MIN_POOL` justification in its methods section — one or two
   sentences, drafted.

## Output format, follow exactly

1. **Lead with the Part A table fully populated.** "No rule stated" is an acceptable and expected cell
   value and must be written out rather than left blank. Count how many of the named sources give no
   rule — that count answers Part B question 1 on its own.
2. Then Part B, four short answers with citations.
3. Then Part C, four numbered answers, including the drafted methods sentences.
4. A **confidence and caveats** section: where imputation-context rules do not transfer to
   behavioural-profile transfer (this study transfers a 48-slot time series, not a scalar, which may
   change what "a good donor" means), and where cross-national survey practice differs.
5. A **reference list** with full citations, dates and direct links.

## Hard requirements

- **Keep statistical matching distinct from record linkage.** This study matches *different* people
  who resemble each other; it does not identify the *same* person in two files. Fellegi-Sunter
  material is out of scope unless it bears directly on cell size.
- **Note where a rule is for imputing a scalar and this study transfers a 48-slot vector.** That
  difference may make a published donor-count rule inapplicable, and saying so is more useful than
  transferring it silently.
- **A clean negative is a result.** If the honest answer is that no literature gives a principled
  minimum and every practitioner tunes it, report that. The paper can then say so and present the
  sweep as a sensitivity — which is a complete and defensible fix.
- **Report findings that weaken the paper plainly.** If the literature says tuning a matching
  parameter on the validation metric invalidates that metric as evidence, say so directly, and say
  what the paper must do instead.
- Do not re-derive: the four-tier key structure, the choice of match keys, the plausibility-exclusion
  gate, or the validation gate thresholds themselves. Those are frozen and documented elsewhere in
  this project.
