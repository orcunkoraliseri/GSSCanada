# SI Glossary — plain-English meaning of the project's own internal terms

Reviewer R2-1 asked that every self-defined project label either be replaced with plain English
everywhere it appears, or, where the label is kept (for example because it names a specific model
or table cell), be glossed in plain English. Most labels found in the jargon audit (`manuscript/prep/jargon_inventory.md`)
were replaced outright and do not appear anywhere in the paper any more; those terms have **no row**
below on purpose — a term only earns a row here if a reader will still actually meet it, in the main
text or in a supplementary table. This table is the one place a reader can look up every label that
survives.

| Term as it appears | Plain-English meaning | Where it is used in the paper |
|---|---|---|
| J3 | J3 is the project's own internal nickname for the specific generator design that produced the results reported here; the number 3 only means it was the third design tried in a family of related designs, and it carries no other meaning. The main text calls this model "the generator" or "the chosen model" and keeps the nickname only in the supplementary model-card table. | SI Table B1 (Generator Model Card). |
| gate (also "hard gate", "SHEU gate") | A gate is a numeric pass/fail check that the project fixed in advance: a result either clears the fixed line or it does not, with no partial credit. | Supplementary scorecard tables (Table B1, Table C1, Table C2, Appendix D). |
| PASS / WARN / INFO / FAIL | These four words are verdict labels used only in the supplementary scorecards. PASS means the check cleared its line; FAIL means it did not; WARN flags a minor issue that was not serious enough to fail the check; INFO is shown for background only and carries no pass/fail judgement at all. | Supplementary scorecard tables (Table B1, Table C1, Table C2, Appendix D). |
| True-Future-Test | This is the project's name for testing the model on an entire survey year it never saw at all during training, the strictest of the checks used in this paper because nothing about that year was available while the model was being built. The main text calls the same check the held-out-year test. | SI Table C2 (heading and rows); the main text's model-selection discussion, under the name held-out-year test. |
| Tier 1 / Tier 2 / Tier 3 / Tier 4 | These numbered tiers describe a four-step fallback search that gives each simulated person a matching real time-use diary: the search first tries an exact demographic match, and only moves to a looser match, one fixed step at a time, when no match exists at the stricter level. The main text describes this same fallback as a plain, numbered list of match rules, without the tier numbers. | SI Appendix D (deviations write-up) and SI Table C1 (match-coverage row). |
| FailSafe | FailSafe is the name of the last, loosest step in that same four-step matching search, used only when every closer match has already failed. The record shows this last-resort step was never actually triggered: every simulated person was matched at one of the three closer steps. | SI Appendix D and SI Table C1. |
| occACT | occACT is the internal name of the data column holding the activity code assigned to each half-hour diary slot (for example sleeping, working, or eating). | SI Table C1 (harmonisation row). |
| Step-8 / Step-9 | These are internal numbers for two stages of the project's own processing pipeline: Step-8 is the batch of building-energy simulations, and Step-9 is the stage that turns each diary into device-power and lighting schedules. The main text names the action directly rather than the step number. | SI Appendix D (deviation write-ups) and supplementary scorecards. |
| COLLECT_MODE | COLLECT_MODE is the internal name of one survey-design flag: it records whether a respondent's diary was collected by a telephone interviewer or filled in online by the respondent. | SI Table B1 (model conditioning variables). |
| DDAY_STRATA | DDAY_STRATA is the internal name of the flag recording which of the three day types, a weekday, a Saturday, or a Sunday, a given diary belongs to. | SI Table B1 (model conditioning variables). |
| DRIFT_MATRIX | This is the internal name of the table that measures how much each at-home percentage changed from one survey cycle to the next, used to check for the pandemic-era jump in time spent at home. | SI Table C2 (structural-break check). |
| C-VAE | C-VAE stands for conditional variational autoencoder, a type of generative model used in the authors' own earlier published work. It is kept here as a named point of comparison against the model chosen for this paper, not as a label coined for this paper. | Main text, defined at first use, then referenced again when the model search is discussed. |

## Terms considered and deliberately left out

- **forecast** — already replaced everywhere by "scenario-based projection" (decision R2-3); the word
  "forecast" no longer describes the 2030 results anywhere a reader would meet it.
- **calibrated J3** — the same underlying label as **J3** above; not given a second row.
- **paired frozen-frame / frozen frame** — fully replaced by plain language ("matched-household
  comparison" / "paired panel of households"); not found in any of the four working drafts or in any
  supplementary table read for this task.
- **MDLM, SEDD** — each appears exactly once, in one supplementary bullet naming a specific losing
  design, and is glossed in place there ("MDLM-G1 (masked discrete diffusion)"); the decision already
  on record keeps these names SI-only with no main-text mention, so a dedicated glossary row is not
  needed at this table's length.
- **calibration closure** — this exact phrase was never actually written anywhere in the manuscript
  (zero hits); it is the reviewer's own description of a framing problem that is fixed by rewording the
  relevant paragraph itself, not by defining a term.
- **hindcast** — ordinary English, not a project-coined term; no change needed.
- **G3, W_2005** (short codes seen in one supplementary footnote each) — one-off internal shorthand for
  a single gate and a single training run, not on the original jargon audit's list, and too minor to
  add given the "roughly 8 to 14 rows" target for this table.

## Note for whoever assembles the final SI

Two supplementary tables that already ship in this folder, `Table_C1_C2.md` and
`Appendix_D_deviations.md`, still use the raw internal labels above throughout their own prose and
table cells (Tier 1-4, FailSafe, True-Future-Test, occACT, Step-8, Step-9, DRIFT_MATRIX_1522, and the
PASS/WARN/INFO/FAIL verdicts). This glossary is written to match what a reader of those two tables, as
they stand today, will actually meet. Those two tables themselves have not yet been through the same
plain-language pass as the four working drafts and `Table_B1_B2.md`; that is outside this task's scope
but is flagged here so it is not missed later.
