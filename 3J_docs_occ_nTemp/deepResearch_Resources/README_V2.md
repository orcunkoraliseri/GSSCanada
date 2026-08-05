# V-series deep research prompts (3J Leg-3 v2 finalisation)

Prompts for **external** deep research (Gemini Antigravity). Written in-repo, run outside it. The
returned reports come back into **this same directory**, beside the prompt that produced them.

## How to run one

1. Paste `00_MASTER_BRIEF_V2.md` into the external tool.
2. Paste the `V<NN>_*.md` prompt after it.
3. The tool answers using the schema in `_RESPONSE_TEMPLATE.md` (Sections A to H).
4. Save the answer here as `RV<NN>_<topic>.md`.

One prompt per session. Do not paste two prompts together: the master brief tells the assistant to
answer only what follows it, and the response template is per-prompt.

## The prompts

| # | File | Question | What it unblocks |
|---|---|---|---|
| **V01** | `V01_prototype_eui_by_climate_zone.md` | DOE-PNNL prototype site EUI by climate zone and code vintage, 2004 to 2019 | Both blocking EUI gates. Tests whether our bands are mismatched to the model on **code vintage** |
| **V02** | `V02_necb_office_reference_eui.md` | NECB 2017/2020 office reference EUI, CZ6 and CZ7, split by heating fuel | `S9-EUI-office`, which fails at a floor of 100 while its own source document says 80 to 140 and 85 to 115 elsewhere |
| **V03** | `V03_household_occupancy_aggregation.md` | Household occupancy aggregation conventions, references rebuilt from zero | Replaces a report where **9 of 15 DOIs resolved to unrelated papers** |
| **V04** | `V04_hotel_eui_band_sources.md` | Hotel as-modelled EUI band, CZ6A and CZ7 | `S9-EUI-hotel`. The 300 ceiling is correctly sourced but its written justification cites a nuclear-materials report |
| **V05** | `V05_prototype_scorecard_retrieval.md` | **Retrieval only**: per climate zone prototype EUI with a direct file URL for every number | Re-run of the one question `RV01`, `RV02` and `RV04` all failed. Settles whether the per zone data is retrievable at all |

`V01` and `V04` overlap deliberately: `V01` builds the whole prototype matrix, `V04` goes deep on
hotels and on the Canadian side. Run `V01` first if you are running both.

**`V05` supersedes `V01` for the prototype matrix.** Run it instead, not as well. It is deliberately
narrow: retrieval, no analysis, no band recommendations, and every number must resolve to a file.

## Round 1 outcome (2026-08-04)

`RV01`, `RV02` and `RV04` **must not be used for band decisions.** Verified against our own results:

* They filled the "our model's comparable output" column with figures they could not have had. Only
  the four-cell median (85.4) was supplied in the brief; the rest were invented, the reports disagreed
  with each other, and both inverted the real relationship between our two cities (our Calgary office
  cells are **lower** than Montreal, not higher).
* They disagree on the load-bearing report numbers (`PNNL-31488` against `PNNL-29780`; `DOE/EE-1614`
  against `PNNL-26348`), and returned two different titles for `PNNL-28543`.
* `RV01` says the per zone data is not in the narrative reports; `RV02` and `RV04` then quote per zone
  values from those reports, all under one landing page URL, all marked "read full text".
* Every band recommendation moved in the direction that makes our failing gate pass. `RV02`'s heating
  row is openly circular: our own `85.4 x 17%` tabled as an external Tier 1 finding.

**What survives and is worth keeping:** `RV03`'s DOI corrections (independently reproduced by a second
blind pass), and two clean negatives that were asked for as negatives, the CanmetENERGY study
`NOT FOUND` and the 441 to 521 hotel figures `NOT FOUND`. The 90.1-2004 provenance is confirmed:
Deru et al. (2011) / PNNL-19590, whose conversions reproduce our local CSV cells exactly.

**No band was changed.**

## Why these exist

Three EUI gates have blocked this leg through eight simulation campaigns. The failures have been traced
**out of the occupancy model**: an uninjected control, with no schedules applied at all, already sits
below the office floor. So the open question is whether the reference bands are correctly derived, and
that is a literature question, not a simulation question.

Two defects motivate the whole series:

* **A vintage mismatch.** The reference tables behind the office and hotel bands are the ASHRAE
  **90.1-2004** baseline prototype set. The building being judged is **90.1-2019 / NECB 2017**. Codes
  tightened across the intervening cycles, so a 2019-code building should sit below a 2004-derived
  figure by construction.
* **Citation rot.** Across two internal reports we have found a cited PNNL report number that is
  actually a nuclear-materials study, a second that does not resolve, a CanmetENERGY study nobody can
  locate, and a reference list where 9 of 15 DOIs point at the wrong papers. Every prompt therefore
  requires DOIs to be checked through CrossRef and report numbers to be checked by opening the PDF.

## Standing rules carried in every prompt

* A citation is not evidence until opened. `COULD NOT OPEN` is never a confirmation.
* Verify DOIs at `https://api.crossref.org/works/<DOI>` and report the returned title.
* `NOT FOUND` with the search terms beats an invented number.
* **Never propose relaxing a band because our model fails it.** Each endpoint needs its own external
  citation. Reasoning of the form "our value is X, so the limit should be below X" is the failure mode
  this project keeps repeating.
* Keep as-modelled and empirical figures strictly separate. Our gates score as-modelled values.
* Convert every EUI to kWh/m2.yr and show the arithmetic.
* No em dashes and no en dashes in the returned text.

## Conventions

* `00_MASTER_BRIEF_V2.md` shared context, pasted first, never restated in an answer
* `_RESPONSE_TEMPLATE.md` the response schema
* `V<NN>_<topic>.md` prompt
* `RV<NN>_<topic>.md` returned report, saved here

The older monolithic `00_deep_research_prompts.md` and the loose topic reports in this directory are
the **previous** round and are kept for provenance. They do not follow this schema.
