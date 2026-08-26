# 2026-08-26 — `D-S2-20`: the two Step 2 questions standing since 2026-08-16, re-measured

**Written while Speed was in scheduled maintenance (6:30–9:00). No compute was needed for any of it —
every number below is re-derived from `Step2_docs/outputs_step2/harmonised.parquet` and from the
gate's own source, not quoted from a progress log.**

`Step2_docs/4thJ_02_harmonisation.md:2021` has carried this line since 2026-08-16:

> **Still open on Step 2 and awaiting the author, neither of them a blocker to Step 3:** whether
> `G2.18`'s escalation clause should carry a whole-gate FAIL when `leak_bands = 0` (and whether
> D-S2-19's quoted 6.3 % / 13.5 % should be corrected to **0.519 % / 4.243 %**), and whether to
> repair the `scale_duration` → `G2.4` clean violation.

Both are still open. Re-measuring the first one changed what it *is*.

---

## Question 1 — `G2.18`'s escalation clause

### 1a. The correction is confirmed; the figures on record are wrong by 12× and 3×

Re-derived from the parquet, one row per diary (73,254 diaries: ES 19,140 / UK 15,854 / IT 38,260),
weighted by `weight_dia`:

| `unknown` weighted share | `ES` | `UK` | `IT` |
|---|---|---|---|
| `strat_econ_status` — **measured** | **0.0000 %** | **0.5192 %** | **4.2435 %** |
| `strat_econ_status` — as quoted in `D-S2-19` | 0.0 % | 6.3 % | 13.5 % |
| `strat_hh_type` — **measured** | **0.0000 %** | **3.5141 %** | **0.0000 %** |
| `strat_hh_type` — as quoted in `D-S2-19` | 0.0 % | 3.6 % | 0.0 % |

⚪ Robust to the weight choice: unweighted reads 0.0000 / 0.4289 / 4.2969 and 0.0000 / 3.4755 /
0.0000; `weight_dia_cal` reads 0.0000 / 0.5192 / 4.2435 and 0.0000 / 3.5145 / 0.0000. The gap to
6.3 / 13.5 is not a weighting convention. **`0.519 % / 4.243 %` is correct**, and `6.3 % / 13.5 %`
should be struck from `D-S2-19`, from `4thJ_02_harmonisation.md:1894` and `:2125`, and from
`4thJ_02_harmonisation_val.md:62` and `:1112`.

### 1b. 🔴 `FINDING 151` — the "ten times" threshold cannot bind, and that, not the share, is why the gate FAILs

`tools/4thJ_gates_step2.py:1067-1068` implements the registered rule literally:

    smallest_other = min(others)
    if shares[country] > smallest_other * 10.0:

In **both** strata one country's `unknown` share is **exactly 0.0000 %**, so `smallest_other` is
`0.0`, so the bar is `0.0`, so **every strictly positive share escalates**. The `10.0` multiplier is
inert. Worked through on the measured shares, reproducing the reported count of 3 exactly:

| stratum | country | its share | smallest of other two | bar = 10× | escalates? |
|---|---|---|---|---|---|
| `strat_hh_type` | `UK` | 3.5141 % | **0.0000 %** | **0.0000 %** | **yes** |
| `strat_econ_status` | `UK` | 0.5192 % | **0.0000 %** | **0.0000 %** | **yes** |
| `strat_econ_status` | `IT` | 4.2435 % | **0.0000 %** | **0.0000 %** | **yes** |
| `strat_econ_status` | `ES` | 0.0000 % | 0.5192 % | 5.1920 % | no |

**3 escalations, `leak_bands = 0`, whole-gate FAIL** — as reported. But the reason on file is wrong.
🔴 **The gate is not saying that 0.52 % is a large imbalance. It is saying that a ratio test was
registered against a denominator that is zero**, and it would fire identically on a share of
0.0001 %. The question the author was asked — *"should an escalation driven by `unknown`'s own share
carry a whole-gate FAIL?"* — presumes the threshold discriminated. It did not.

🔴 This is `feedback_gates_must_be_seen_failing` in its exact registered form: the clause **was** seen
firing, the count **does** match the arithmetic, and the firing still carries no information.

### 1c. What is actually being asked, restated

`leak_bands = 0` is the substantive result: **no band is emitted by exactly one country**, so the
leave-one-country-out design has no declared country marker in the prefix.

* **(a)** Keep the whole-gate FAIL and publish it with `FINDING 151` attached — the gate ships FAIL
  and the limitation says *why*: a zero-denominator ratio test. Nothing is edited. 🔴 **Recommended.**
  It costs nothing, moves no threshold, and is honest about a clause that does not discriminate.
* **(b)** Split the verdict: leak clause PASS, escalation reported as a labelled note, whole gate not
  FAILed on the escalation alone. 🔴 A **band change**, not an additive fix — it changes what `G2.18`
  means, after the fact, in the direction of passing. `feedback_read_the_gates_own_doc` forbids doing
  that silently; it needs this ruling in writing if taken.
* **(c)** Re-specify the escalation on a basis that can bind (an absolute percentage-point floor, or
  `max(smallest_other, ε)`). 🔴 **A new rule** — it would have to be registered and then seen failing
  before it could be trusted, late in the project.

⚪ Under (a) and (b) alike the correction in **1a** should be made regardless: a wrong number in a
decision record is wrong whichever way the verdict goes.

---

## Question 2 — the `scale_duration` → `G2.4` clean violation

### 2a. Re-confirmed, and not repairable by tuning

`Step2_docs/outputs_step2/proglog_step2_gates.md:125` states the mechanism, and it is arithmetic
rather than an observation: a diary summing to 1,440 minutes with every episode scaled by ×1.01
necessarily sums to 1,454.4. Mass conservation (`G2.3`) and day closure (`G2.4`) **cannot be pulled
apart by a uniform duration scale, in principle, on any data**. So:

* `scale_duration` fells `G2.3` — as its row intends — **and** `G2.4`, which its row lists as
  must-stay-clean. Acceptance test 3: `clean violations = 1`.
* 🔴 **`G2.3`'s detection power has never been demonstrated independently of `G2.4`'s.** No
  perturbation in the seventeen-row table exercises `G2.3` alone.

### 2b. What is actually being asked

The runner already recorded the repair that would work and deliberately did not implement it: corrupt
**weights** rather than durations — scale `weight_dia` by 1.01 for one country. Total weighted minutes
move (`G2.3` FAILs) while every diary still sums to 1,440 exactly (`G2.4` stays clean).

* **(a)** Add that one row to the pre-registered perturbation table, run it, and require it to be
  **seen felling `G2.3` with `G2.4` clean**. 🔴 **Recommended, and cheap** — Step 2's battery is
  CPU-only and local; no Speed, no GPU. If it does not separate them, that is a finding too.
  ⚪ It is an **addition to a pre-registered table**, which is the author's call and not a runner's —
  which is why it is here and not already done.
* **(b)** Leave it, and carry *"`G2.3` is not demonstrated independently of `G2.4`"* as a declared
  limitation in the methods. Costs nothing, and leaves one gate in the paper whose detection power is
  asserted rather than shown.
* **(c)** Drop `scale_duration`'s must-stay-clean entry for `G2.4`. 🔴 **Refused as a recommendation** —
  it makes the violation disappear by editing the expectation to match the outcome, the one move the
  acceptance test exists to prevent.

---

## Status

* Nothing was edited, no threshold moved, no gate silenced, no perturbation added or adjusted.
* Neither item blocks anything: Step 2 shipped, Steps 3–9 are built on it, and both were already
  carried as declared limitations.
* 🔴 What changed today is **item 1's reason**, not its verdict. `FINDING 151` means the standing
  note's own framing of question 1 was wrong, and the author should be asked the corrected question.

---

## Author's Rulings & Directives (`D-S2-20`)

| # | Question / Item | Ruling | Core Action & Methodology | Impact / Invariants |
|---|---|---|---|---|
| **Q1** | `G2.18` (Escalation clause & number correction) | 🟢 **Option (a)** | **Keep whole-gate FAIL with `FINDING 151` declared as a zero-denominator ratio limitation; confirm `leak_bands = 0`. Correct recorded numbers to `0.519 % / 4.243 %` (and `3.514 %`).** | Zero threshold modification; updates erroneous documentation numbers (`D-S2-19`, `4thJ_02_harmonisation.md`, `val.md`). |
| **Q2** | `scale_duration` $\to$ `G2.4` (Clean violation) | 🟢 **Option (a)** | **Add weight-scaling perturbation (`scale_weight` $\times 1.01$ for one country) to pre-registered battery; execute local CPU test; verify `G2.3` falls while `G2.4` stays clean.** | Demonstrates independent detection power of `G2.3` (weighted minutes) vs `G2.4` (1,440-min closure) without touching thresholds. |

### Detailed Directives:
1. **`G2.18` Escalation & Errata**:
   - The substantive LOCO invariant is fully respected: `leak_bands = 0` (no stratum is leaked by a single country).
   - In accordance with `FINDING 151`, document that the 10× ratio test escalated vacuously against Spain's exact 0.0000% denominator, not because 0.52% / 4.24% represent substantial imbalances.
   - Update all instances of the misquoted 6.3% / 13.5% figures to the verified values `0.5192 % (UK)` and `4.2435 % (IT)` in `D-S2-19`, `4thJ_02_harmonisation.md`, and `val.md`.
2. **`G2.3` vs `G2.4` Perturbation Disambiguation**:
   - Implement `scale_weight` perturbation in `tools/4thJ_step2_gates.py` (scale `weight_dia` by 1.01 on one country).
   - Run the local CPU battery to confirm `G2.3` (total mass conservation) is felled cleanly while `G2.4` (diary 1,440-minute day closure) remains strictly clean, resolving the clean-set violation rigorously.

⚪ `prereg.md` (md5 `e4243e07cdd80c9c846b91f40e3e8c45`) remains strictly frozen. Both standing Step 2 items are formally resolved and closed.

---

## EXECUTION RECORD — 2026-08-26, same morning as the ruling

🟢 **Both rulings are discharged. Full record in the Step 2 val doc's Progress Log.**

**Q1 (a).** `G2.18` keeps its whole-gate FAIL with `FINDING 151` declared beside it; `leak_bands = 0`
confirmed. Five normative statements corrected to `0.5192 % (UK)` / `4.2435 % (IT)` / `3.5141 %
(UK, hh_type)`, each carrying a dated `D-S2-20 Q1(a)` marker: `4thJ_02_harmonisation.md` ×2 and
`4thJ_02_harmonisation_val.md` ×3. 🔴 The impl/progress-log entries that quote the wrong figures **in
order to flag them** were deliberately left untouched — they are the audit trail that caught it.

**Q2 (a).** `scale_weight` added to the pre-registered table (`weight_dia` × 1.01 on Italy — same
country, same factor as `scale_duration`, so exactly one thing differs). Run on the **real**
`harmonised.parquet`:

| gate | baseline | `scale_weight` | required | result |
|---|---|---|---|---|
| `G2.3` | PASS, rel diff 1.3042e-16 | **FAIL, rel diff 0.0100** | must fail | ✅ |
| `G2.4` | PASS, 0 / 0 | **PASS, 0 off 1,440, 0 tiling failures** | must stay clean | ✅ |
| all others | — | identical to baseline | — | ✅ zero blast radius |

🟢 The standing limitation *"`G2.3` is not demonstrated independently of `G2.4`"* is **discharged**.
🔴 The clean violation itself is **not** — `scale_duration` still fells `G2.4` and acceptance test 3
still counts 1. The ruling added a row; it did not delete the entangled one.

**Also found, and reported rather than repaired: 🔴 `FINDING 152`.** The `--selftest` driver **crashes**
(`KeyError: 'strat_day_type'`, line 1517) rather than reporting the missing-column FAIL that
`impl/2026-08-17_step2-gates18.md:114` predicted. Confirmed pre-existing on the unpatched backup.
Consequence: every perturbation after `strat_day_type_wrong_grain` and **all three sweep-level
acceptance tests** are unreachable under `--selftest`. Extending the fixture is additive, CPU-only and
local, and is scoped as its own task.

⚪ Files changed: `tools/4thJ_gates_step2.py` (3 additive edits, `py_compile` clean),
`4thJ_02_harmonisation.md`, `4thJ_02_harmonisation_val.md`. Backups `*.bak_ds220*` verified non-empty
before every write. `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` untouched.
