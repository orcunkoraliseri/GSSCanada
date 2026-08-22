# `D-S6-9` — the pre-registered bar is not the strongest null. What `G6.1` is now.

**Date:** 2026-08-22 (evening)
**Raised by:** scoring `G6.1`, `G6.2` and `G6.3` on the same metric for the first time.
**Status:** OPEN. Nothing changed. `prereg.md` untouched, md5 `e4243e07cdd80c9c846b91f40e3e8c45`.

Evidence: `Step6_docs/4thJ_06_transfer.md`, entry of 2026-08-22 (evening, third entry), and
`outputs_step6/g61_leg4_scored.json` + `g62_g63_leg4_scored.json`.

---

## The fact

`prereg.md` §5 registers the **raked-donor null** as *"the strongest"* and *"🔴 THE PRE-REGISTERED
BAR"*, and calls the pooled all-country average *"weak"*. `D-S6-7` demoted `G6.3` further, to
*"Reported, **secondary**"*.

Scored on the level-1 time budget — the quantity prereg §6 FAIL criterion 1 names, *"MAE ≥ the
raked-donor null"* — **the ordering is reversed in six of nine cells.**

NULL MAE, minutes/day. **Lower = stronger null = harder bar.**

| fold | band | `G6.1` raked | `G6.3` pooled | `G6.2` per donor |
|---|---|---|---|---|
| `es` | `Y25-44` | 9.93 | **5.81** | `it` **5.01** · `uk` 10.91 |
| `es` | `Y45-64` | **8.82** | 9.79 | `it` 11.23 · `uk` 15.26 |
| `es` | `Y_GE65` | 11.81 | 15.71 | `it` **11.27** · `uk` 20.84 |
| `uk` | `Y25-44` | 21.79 | 11.69 | `es` 12.41 · `it` **10.80** |
| `uk` | `Y45-64` | 19.21 | 17.62 | `es` **17.18** · `it` 19.25 |
| `uk` | `Y_GE65` | 18.54 | **18.43** | `es` 24.98 · `it` 18.99 |
| `it` | `Y25-44` | 19.51 | 13.81 | `es` **13.26** · `uk` 15.27 |
| `it` | `Y45-64` | **13.85** | 14.07 | `es` 14.40 · `uk` 19.37 |
| `it` | `Y_GE65` | 15.51 | **14.54** | `es` 16.82 · `uk` 18.31 |

On the `uk` fold at working age the gap is a factor of two: 21.79 against 10.80.

**Two candidate mechanisms, neither checked.** The rake starts from a **uniform seed** (`D-S5-10` (a))
and so **discards the survey weights**, while `G6.2`/`G6.3` carry `weight_dia_cal`; and a raked null
can converge on a small effective sample, which `FINDING 62` already showed for `uk`. It is **not** the
day mix — the synthetic populations are 71.43 / 14.29 / 14.29, the calendar week to two decimals.

🟢 **This was found on a Leg-4 rehearsal, before any reportable model existed.** It is the only moment
at which it could be found without looking like a reaction to a result.

---

## The decision

| | option | consequence |
|---|---|---|
| **(a)** | 🟢 **Recommended. `G6.1` stays exactly as pre-registered — the raked-donor null is the bar — and this table is reported as a finding.** | The pre-registration is honoured to the letter, which is the whole value of having frozen it. The paper states that the null we called strongest was not, and shows the table. Costs nothing except an honest paragraph |
| **(b)** | Take the minimum null MAE across all three as the operative bar. | Strictly harder, and therefore tempting. But it is **choosing the bar after seeing the numbers**, which prereg §6 exists to prevent, and it makes the bar's identity vary cell by cell |
| **(c)** | Re-seed the rake from `weight_dia_cal` instead of uniform, and re-measure. | 🔴 A basis change to `D-S5-10` (a), already ruled. It may well restore the expected ordering — which is exactly why it must be the author's call and not a repair applied because a result was surprising |

Under **(a)** nothing is rebuilt and nothing is re-run; the finding is a paragraph and a table.

---

## One thing that does not need a ruling

`G6.2` is **six nulls**, two per fold, and neither member of a pair is the result — `D-S6-6` (a)
dropped the word *nearest*. `tools/4thJ_step6_secondary_score.py` prints both and emits no aggregate.
On `es Y_GE65` the pair differs by a factor of **1.85** (`it` 11.27 against `uk` 20.84), which is the
size of the gate-shopping opportunity the ruling closed.
