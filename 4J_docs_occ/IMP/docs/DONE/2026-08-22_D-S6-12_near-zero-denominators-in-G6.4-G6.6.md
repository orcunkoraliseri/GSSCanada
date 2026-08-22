# `D-S6-12` — the worst-band rule selects on denominator smallness, not on fit

**Raised** 2026-08-22, from the `G6.6` generated arm (six batches, jobs 1286254–1286259).
**Status** OPEN — 🔴 this is a **BAND** question. Additive fixes only; I have changed nothing.
**Blocks** any quotation of a `G6.4` or `G6.6` headline number, in the paper or anywhere else.

---

## 1. What was found

`G6.4` reports, per fold, **the worst scoreable age band's MAPE**. Those three numbers are the
headline transfer result:

| fold | reported | which band | that band's **MAE** | the cell that drove it |
|---|---|---|---|---|
| `es` | **363.44 %** | `Y_GE65` | 42.13 min | `AC1_TR` published **5** min/day, model 106.1 |
| `uk` | **215.13 %** | `Y_GE65` | 36.37 min | `AC2` published **1** min/day, model 7.3 |
| `it` | **176.87 %** | `Y_GE65` | 21.21 min | `AC2` published **1** min/day, model 6.3 |

In every fold the worst band is `Y_GE65`, and in every fold it is driven by a published value of
**1 to 5 minutes per day**.

🔴 **`Y_GE65` is not the worst-fitting band. In minutes it is among the best.** Italy's `Y_GE65`
MAE of 21.21 min is the **second-lowest of all twelve** rows in the artefact; its `Y25-44` MAE is
77.75, nearly four times larger, and is reported at 39.76 %. Re-running the selection on MAE
instead of MAPE changes the answer in two folds of three:

| fold | worst by MAPE | worst by MAE |
|---|---|---|
| `es` | `Y_GE65` 363.44 % (MAE 42.13) | `Y25-44` MAE 69.50 (MAPE 42.57 %) |
| `it` | `Y_GE65` 176.87 % (MAE 21.21) | `Y25-44` MAE 77.75 (MAPE 39.76 %) |
| `uk` | `Y_GE65` 215.13 % | `Y_GE65` — agrees |

Across the eighteen `(pair, band)` cells of the `G6.6` generated arm the two metrics are
**negatively rank-correlated: Spearman = −0.5604.** The gate's own statistic runs *against*
absolute error.

## 2. Why it happens, and why it is not the model's fault

Eurostat publishes ~1 min/day of employment time (`AC2`) for the over-65s. That is
**substantively correct** — retired people do not work — and it is the correct number to publish.
It is simply not a legitimate denominator. `D-S6-3` item 1 ruled MAPE on **non-zero** cells with a
zero-cell hit/miss rule at `< 1.0 %`. These cells are non-zero, so they fall in the MAPE arm; the
ruling anticipated **zero**, not **near-zero**, and near-zero is where all three headlines live.

🔴 It compounds with `FINDING 39`: the published tables carry a country-dependent rounding floor.
A cell printed as `1` is some true value in `[0.5, 1.5]`, so its APE is **not identified**:

| cell | printed APE | span from rounding **alone** |
|---|---|---|
| `uk` `Y_GE65` `AC2` (pub 1, model 7.3) | 630 % | **387 % … 1360 %** |
| `it` `Y_GE65` `AC2` (pub 1, model 6.3) | 530 % | **320 % … 1160 %** |
| `es` `Y_GE65` `AC1_TR` (pub 5, model 106.1) | 2022 % | 1829 % … 2258 % |

🟢 **Not all three are artefacts, and the document must not claim they are.** The `es` cell spans
1829–2258 %: 106 minutes of daily travel against a published 5 is a genuine ~20× model error and
survives any rounding assumption. The two `uk`/`it` cells at `pub = 1` do not survive it — their
APE moves by a factor of 3.5 on the rounding convention alone.

## 3. Scope

Reaches `G6.4` (held-out, the reported gate), `G6.6` clause 1, and `G6.6` clause 2 — clause 2
differences two MAPEs and inherits the defect from both sides. Does **not** reach `G6.9`, which
`D-S6-10` put on a dimensionless MAE ratio, nor `G6.1`/`G6.2`/`G6.3`, which are in pp.

## 4. The question

Which basis should the worst-scoreable-band rule use?

**(a)** Keep MAPE, but make a cell **scoreable only when its published value clears a floor**, by
analogy with the `SIGN_FLOOR_MIN = 2.0` min/day already confirmed for `G6.5` under `D-S6-10`
item 2. Cells below the floor move to a **hit/miss** test like the zero-cell rule. Additive; keeps
the existing bar; needs the floor pre-registered.

**(b)** Report the worst band **by MAE in minutes/day**, with MAPE retained and printed as
secondary. Directly measures what the claim is about (time use in minutes) and is immune to the
denominator; but it is a **new bar** — `15.0 %` has no minutes equivalent and one must be chosen.

**(c)** Report **both**, and require both to pass. Strictest; guarantees no band escapes on either
metric; makes the pilot's failure list longer, not shorter.

**(d)** Change nothing, and declare the near-zero denominators as a limitation in the paper.
Honest and zero-risk to the frozen artefacts, but leaves a headline number that is negatively
correlated with fit.

> ### Answer — Question 1 (Worst-scoreable-band basis)
>
> **Option (a) + MAE Dual Reporting:**
> 1. Set a scoreability floor for relative MAPE at **`PUBLISHED_FLOOR_MIN = 10.0` min/day**.
> 2. Cells with published values $< 10.0$ min/day (e.g. `AC2` = 1 min for retirees) move to an absolute tolerance check ($\text{MAE} < 15.0$ min/day) by direct analogy with `SIGN_FLOOR_MIN` (`D-S6-10`) and the zero-cell hit/miss rule (`D-S6-3`).
> 3. Concurrently, report **MAE in minutes/day alongside MAPE across all bands** (`D-S6-8` Item 4).

## 5. Second question — `G6.6`'s clause-2 tolerance, which is a band and has never been set

Clause 2 asks that **held-in MAPE − held-out MAPE ≤ `--tolerance-pp`**. It currently runs at
**0.0 pp**, which is the strict reading: being a training donor must never make the fit worse, by
any margin at all. That number was a placeholder I chose to make the gate runnable; it is a band and
it is the author's.

The generated arm shows why it matters. Clause 2 passes 5 of 6 pairs, and the single failure —
`es`/`it` at **+29.32 pp** — is far outside any plausible tolerance, so at pilot scale the ruling
does not change the board. But the six pairs disagree with each other by **60 pp** on the same
target country with the same held-in status (`es`/`it` 206.19 % vs `uk`/`it` 145.96 %). 🔴 **The
pair-to-pair spread is larger than the effect clause 2 is trying to detect**, which is the real
reason a tolerance is needed and the reason it cannot be set by looking at these numbers.

**(a)** Keep **0.0 pp** — the strict reading, and declare that clause 2 is a directional check
rather than a calibrated one.
**(b)** Set the tolerance from the **observed pair-to-pair spread** at Leg 5, pre-registered before
that run is scored. Principled, but it cannot be written down today.
**(c)** Set a fixed pre-registered value now on the same reasoning as `MAPE_MAX = 15.0` was reused
from `G6.4` — i.e. borrow an existing project number rather than invent a second one.

> ### Answer — Question 2 (`G6.6` Clause 2 Tolerance)
>
> **Option (a) — Keep `0.0 pp` (Strict Directional Check):**
> Maintain `--tolerance-pp 0.0` as a strict directional requirement: training inclusion must not degrade transfer fidelity relative to held-out evaluation in expectation. Declare in the methods that Clause 2 operates as a directional guard rather than an empirical tolerance band.

---

## Author's Rulings & Directives (2026-08-22)

| # | Item / Decision | Ruled Option | Summary of Decision | Action Required |
|---|---|---|---|---|
| **1** | Worst-Band Metric Basis (`G6.4`/`G6.6`) | 🟢 **Option (a)** | **Published denominator floor `PUBLISHED_FLOOR_MIN = 10.0` min/day for MAPE**; cells $< 10.0$ min/day evaluated on absolute tolerance ($\text{MAE} < 15$ min/day); **MAE reported alongside MAPE everywhere**. | Update `tools/4thJ_step6_level1.py` and `tools/4thJ_step6_g66.py`; prevents 1-minute retired work categories from artificially dominating headline transfer metrics. |
| **2** | `G6.6` Clause 2 Tolerance Band | 🟢 **Option (a)** | **Maintain strict directional threshold `--tolerance-pp 0.0`** (`held_in_MAPE - held_out_MAPE <= 0.0 pp`). | Preserve 0.0 pp in `tools/4thJ_step6_g66.py`; document in methods as a directional non-inferiority invariant. |

---

### Detailed Rulings and Directives

#### 1. Question 1: Eliminating Near-Zero Denominator Distortion in `G6.4` / `G6.6`
* **Choice**: Introduce a minimum published denominator threshold (`PUBLISHED_FLOOR_MIN = 10.0` min/day) for relative percentage error calculation, routing sub-10-minute categories to an absolute error check ($\text{MAE} < 15.0$ min/day), while reporting absolute MAE across all categories.
* **Scientific Rationale**:
  1. **Removes negative rank-correlation artefact**: In the uncorrected calculation, MAPE is negatively correlated with absolute error ($\rho = -0.5604$) because a 5-minute published baseline with a 6-minute model output yields a $500\%$ error, while a 200-minute baseline with a 70-minute deviation yields only $35\%$.
  2. **Immunises against rounding jitter**: Eurostat's 1-minute rounding floor produces an unidentified APE span of $387\% - 1360\%$ on rounding noise alone for categories printed as `1` min/day (`AC2` for seniors).
  3. **Preserves pre-registered $15.0\%$ MAPE bar**: The $15.0\%$ threshold remains fully binding on all substantive daily activities ($\ge 10.0$ min/day).

#### 2. Question 2: `G6.6` Clause 2 Held-In vs Held-Out Tolerance
* **Choice**: Retain the strict directional bound `0.0 pp`.
* **Scientific Rationale**:
  1. The core theoretical property evaluated by `G6.6` Clause 2 is that seeing a country during training should improve or maintain—never systematically degrade—generalisation to that country.
  2. Maintaining `0.0 pp` avoids post-hoc parameter tuning and treats the clause as a strict non-inferiority test.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
