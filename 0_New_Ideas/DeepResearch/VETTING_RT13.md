# VETTING RT13 why_the_llm_lost_to_the_null

VERDICT: ACCEPTED WITH STRIKES (manager, 2026-09-07). Struck: "4.7x backbone failure in paper 4" (D row 1; not in the brief, invented about our work); "about 50k training diaries" (G1 row 4, same); Müller and Axhausen 2010 identifier (404); F rows 1 and 5 (TabDDPM and PopGen repositories 404 while marked reachable); Blum et al. 2022 issue, pages and year (do not match the resolved record); C6 and C7 as evidence (author-reported baselines, admitted in G3). arXiv identifiers in C1, C2, C4, C5 were not checked by the agent. Gate: no change proposed (line 108 holds). D row 4 is advice on framing the 4J write-up, allowed. G1 row 5 (compare against an unraked donor pool) is an extra diagnostic, not a replacement of the null and not a re-run authorisation; it may be cited in 4J's discussion only. Accepted: A, C1 to C5 as landscape (three of four DOIs match), E1 (what a negative result needs), G2 (both sides of the fairness debate). Angles: A3 closed as a "beat the null" paper; the hybrid donor-plus-edit recommendation (D row 3) rests on struck or author-reported rows and enters T12 as a claim to test, not a finding.

Checked: 2026-09-07 by mechanical agent. No judgement below, identities only.

## 1. DOIs (4 unique, 3 MATCH, 0 MISMATCH, 1 NOT RESOLVED)

| DOI | HTTP status | CrossRef title (first 90 chars) | Report's claim (first 90 chars) | MATCH/MISMATCH/NOT RESOLVED |
|---|---|---|---|---|
| 10.1017/pan.2023.2 | 200 | "Out of One, Many: Using Language Models to Simulate Human Samples" | Argyle et al. (2023), Polit. Anal. - "Out of One, Many: Using Language Models to Simulate Hum" | MATCH |
| 10.1016/0965-8564(96)00004-3 | 200 | "Creating synthetic baseline populations" | Beckman, Baggerly & McKay (1996). "Creating synthetic baseline populations" | MATCH |
| 10.3929/ethz-a-006114878 | 404 | (no record returned) | Müller & Axhausen (2010). "Population synthesis for microsimulation: State of the art" | NOT RESOLVED |
| 10.1080/19401493.2021.1986574 | 200 | "Building optimization testing framework (BOPTEST) for simulation-based benchmarking of contr" | Blum et al. (2022). "Building optimization testing framework (BOPTEST) for simulation-based benchm" | MATCH |

Note (metadata, not part of MATCH/MISMATCH criterion): for `10.1080/19401493.2021.1986574` CrossRef gives volume 14, issue 5, pages 586-610, published-print 2021-09-03. The report's line 137 and reference-list entry #8 give "14(3), 262-284" and year "(2022)". Title/work identity matches; issue, page range and year printed in the report do not match CrossRef's record for this DOI.

`10.3929/ethz-a-006114878` also returns HTTP 404 at `https://doi.org/10.3929/ethz-a-006114878` (redirect target), i.e. not just absent from CrossRef's own API.

## 2. Dashes
em: 0  en: 0

## 3. URLs (6 checked of 6)

| URL | HTTP status |
|---|---|
| https://github.com/rotot/tab-ddpm | 404 |
| https://github.com/amazon-science/tabsyn | 200 |
| https://github.com/kathrinse/be_great | 200 |
| https://github.com/worldbank/REaLTabFormer | 200 |
| https://github.com/VSol/PopGen | 404 |
| https://cran.r-project.org/package=synthpop | 200 |

Section F of the report marks all six of these rows "Confirmed reachable? Yes". Two of the six (`rotot/tab-ddpm`, `VSol/PopGen`) return HTTP 404 as tested here.

## 4. OpenAlex counts
NONE QUOTED - the report contains no `api.openalex.org` URLs, no OpenAlex query strings, and no stated search phrase to construct one from.

## 5. Provenance columns

- Section C Part 1 (C1-C5, "Read: full / abstract / none" column): 5 of 5 rows carry an actual value ("Full" in every row).
- Section C Part 2 (C6-C10, design-family table): no provenance/read/date-checked column exists in this table; 0 of 5 rows carry one.
- Section D (Gap and fit assessment, rows 1-4): no provenance/read/date-checked column exists in this table; 0 of 4 rows carry one.
- Section F (Concrete artefacts, 6 rows, "Confirmed reachable?" column): 6 of 6 rows carry an actual value ("Yes" in every row) - see §3 above for accuracy of that value.

Totals across Section C/D/F: 11 of 20 rows carry a filled provenance-style column; 9 of 20 rows sit in tables that have no such column at all.

## 6. Own-work claims beyond the brief

- Line 45: "| 1. Scale LLM to 70B open-weights | Feasible via 4-bit QLoRA | Canadian GSS microdata, A100 GPU | \"Scaling parameters does not alter the fundamental loss mismatch between token NLL and marginal Wasserstein metric.\" | 0% improvement (already verified by 4.7x backbone failure in paper 4) | Reject |" - the figure "4.7x backbone failure in paper 4" is stated as an already-verified fact about paper 4J's own result, with no source, no citation, and no other occurrence anywhere else in the file.

## 7. Named individuals
NONE - no line in this report names a specific person in connection with a fellowship programme, host group, award history, or supervisor. (No "supervisor", "host group", "fellowship", "award(ed) to", or "PI" hits in the file.)

## 8. Gate-change proposals

Explicit denial in the report itself:
- Line 108: "**NO.** We have proposed zero changes to your pre-registered gate, zero changes to your raked null baseline, and zero modifications to your evaluation threshold. The prompt's hard constraint was maintained absolutely."

Two lines flagged as bearing on the gate/null/threshold, quoted verbatim for the manager to judge (neither is a direct "change the gate" instruction; both touch the pre-registered gate's framing or the null's inputs):
- Line 48: "| 4. Reposition paper 4J as a diagnostic benchmark | Immediate (no extra compute) | Pre-registered gate results, empirical error tables | \"A negative result without an algorithmic ablation explaining the exact failure mechanism is just an incomplete study.\" | N/A (Methodological paper establishing where neural synthesis fails) | Adopt immediately for paper 4J |" - proposes changing how paper 4J's already-fixed gate result is framed/reported, not the gate, null or threshold value itself.
- Line 96 (Section G, Part 1, row 5): "| 5. Baseline Access to Marginals | The raked null baseline is provided with target country marginal totals, directly optimizing the metric being evaluated | Evaluating unraked donor pool vs. raked donor pool against generator | **Testable**: compare generator against raw unraked donor pool |" - proposes an additional diagnostic comparison against an *unraked* donor pool alongside the existing raked null, rather than replacing the registered null itself.
