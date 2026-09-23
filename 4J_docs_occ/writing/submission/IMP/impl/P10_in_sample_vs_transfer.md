# P10 — In-sample against out-of-sample (2026-09-23)

**Status:** read done; no compute. Proposed route (b)+(context), author to see in the next reply.

## What exists on disk (re-read 2026-09-23, not carried from the agent)

Source: `Step6_docs/outputs_step6/g66_leg5_generated.json` (held-in check `G6.6`, reported model, Leg-5).
Bar: worst-band MAPE <= 15.0 % (reuses `G6.4`'s absolute bar; `Step6_docs/4thJ_06_transfer.md:2187-2189`).

| Pair in file (block) | worst-band in-sample MAPE | line | worst-band MAE (min/day) |
|---|---|---|---|
| es / it | 158.07 % | 240 | 49.06 |
| es / uk | 33.10 % | 463 | 45.79 |
| it / es | 53.94 % | 696 | 88.10 |
| it / uk | 48.93 % | 919 | 51.28 |
| uk / es | 45.88 % | 1151 | 71.36 |
| uk / it | 151.49 % | 1374 | 44.27 |

All six `passes: false` (matches manuscript Table 4, "FAIL, 6 of 6").
MAE column and block labels as reported by the read agent; MAPE values and pass flags re-checked by grep.
Before quoting, confirm which of the two labels is the fold and which the training country (the
`held_out_mape` values repeat per label: 111.93 at lines 234 and 1368, 82.75 at 457 and 913, 32.05 at 690 and 1145).

Real-data control on the same bar (`g66_corpus_calibration.json`, `4thJ_06_transfer.md:2199-2206`):
the real corpus scores es 4.64 %, uk 5.96 %, it 11.50 %, so the bar can be met.

## What does NOT exist

No raked-donor in-sample MAE for the six training-country cells. It was deliberately not built
(`4thJ_06_transfer.md:2208-2211`, `FINDING 86`): the donor pool for a training country contains that
country's own diaries, so a donor in-sample score is close to self-against-self and would pass trivially.
Building it now would be a comparison with no information in it. Do not build it.

## Consequence for the paper (route)

Option (a) from the plan (model in-sample MAE beside donor in-sample MAE) is not honest to build.
Route taken: plan option (b) plus context. The Results section (new 3.1) says in two sentences:
the model also misses the absolute bar on the countries it was trained on (in-sample worst-band MAPE
33-158 % against a 15 % bar that real diaries meet at 5-12 %), so the shortfall is not only a transfer
effect. The claim then narrows to "a fine-tuned model does not beat reweighting real diaries, and it
does not reproduce its training countries to the same bar either". The title chosen under D2 already
fits this wording. Transfer verdict (Table 3) unchanged.

**Test before writing:** confirm the fold / training-country order in the JSON (see note above) and
re-read the MAE values at the six lines before any number enters the manuscript.

## Label order confirmed (2026-09-23, manager)

In `g66_leg5_generated.json` a pair "a/b" = model of fold a (country a held out) scored IN-SAMPLE on
training country b: block "es/it" has `published_country: "it"` (line ~36). So the six cells are
es-fold on it and uk, it-fold on es and uk, uk-fold on es and it. `worst_mape` and `worst_mae_min_day`
per pair are the numbers to quote. (`held_out_mape` repeats per training country, e.g. 111.93 for both
es/it and uk/it: it is clause 2's comparator keyed by b, not the held-out score of fold a; do not quote it
without re-reading `tools/4thJ_step6_g66_heldin.py`.) Status: P10 DONE; numbers enter Results 3.1 at the
rewrite.
