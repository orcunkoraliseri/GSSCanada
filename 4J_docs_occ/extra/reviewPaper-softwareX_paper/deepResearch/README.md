# P-series deep research prompts — SoftwareX review + 4J literature

Prompts for **external** deep research (Gemini Antigravity). Written here, run outside. Answers come
back into this same directory as `RP<NN>_<topic>.md`.

Prefix is `P` so the series never collides with the 4J `L`-series in
`4J_docs_occ/DeepResearchPrompts/`.

## Why this series exists

Two jobs at once, and they are genuinely the same searches:

1. **Verify the load-bearing claims in the review of SOFTX-D-26-00798R1** before it is submitted on
   2026-09-04. Four of my six review points rest on external facts I asserted from memory or from a
   single search. If any of them is wrong, the review is wrong, and a wrong review is worse than a
   late one.
2. **Fill real gaps in the 4J literature base.** The manuscript under review sits in the same space
   as 4J — time-use microdata plus an LLM, producing occupant behaviour for building energy — and
   reading it surfaced literature we do not have. `P01`, `P03` and `P06` are worth running even if
   the review did not exist.

🔴 **Confidentiality.** The manuscript is under confidential peer review. **No prompt in this series
quotes it, names it, names its author, or reveals that it exists.** Every prompt is written as a
standalone research question that any building-performance group could plausibly ask. Do not edit
that property back out. If a prompt cannot be asked without disclosing the manuscript, it does not
get asked.

## How to run one

1. Paste `00_BRIEF.md` into the external tool.
2. Paste the `P<NN>_*.md` prompt after it.
3. The tool answers using the schema in `../../DeepResearchPrompts/_RESPONSE_TEMPLATE.md`
   (Sections A–H). That template is the house standard and is not restated here.
4. Save the answer here as `RP<NN>_<topic>.md`.

**One prompt per session.**

## The prompts

| # | Topic | Blocks the review? | Value to 4J |
|---|---|---|---|
| `P01` | TUS/ATUS-driven stochastic occupancy models — the lineage, and the right baseline | 🔴 **YES** — review Point 3 | 🟢 High — this is our own literature and we cite little of it |
| `P02` | Divergence metrics for generated activity sequences; the finite-sample floor; duration-sensitive statistics | 🔴 **YES** — review Points 1 and 2 | 🟢 High — bears directly on `G6.*` and on how we report Step 6 |
| `P03` | LLM agents as demographic proxies: "silicon sampling", and what "different personas behave differently" is worth | ⚪ Supporting — review Point 6 framing | 🟢 **Highest** — this is the objection our own reviewers will raise |
| `P04` | Demand-response signal typologies and the actual field efficacy of peer comparison | 🔴 **YES** — review Point 6 | ⚪ Low |
| `P05` | Reproducibility of LLM-in-the-loop simulation studies; what `T=0` does and does not buy | 🔴 **YES** — review Point 5 | ⚪ Medium — we decode from our own weights, so this is a contrast we can claim |
| `P06` | ATUS operationalisation and multi-year weight pooling | ⚪ Supporting — review Point 4 | 🟢 High — the pooling and day-base questions are `FINDING 53` in another survey's clothes |

## Run order

`P01`, `P02`, `P04` and `P05` before 2026-09-04, because the review is only as good as they are.
`P01` first — it is the one most likely to change what the review says.

`P03` and `P06` can run after the review ships; they are 4J work.

## Vetting

Per `feedback_deep_research_is_external`: expect fabricated citations. Every Section B row that the
review will rely on gets **re-derived by us** — resolve the DOI, open the paper, confirm the number
is in it — before a single sentence of the review changes. `FINDING 47` (a "CrossRef-verified" DOI
that resolved to an unrelated paper) is the standing reminder.
