# Questions for the author — 2026-08-22

**Written after every Step 5 job has landed. Nothing is running on Speed.**
**Scope** the **two** questions that stand between the project and closing Step 5, with the full
context and the consequence of every option. Nothing in this file changes any artefact.
`prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` is untouched.

| # | Item | Status | What is actually asked | Weight |
|---|---|---|---|---|
| **Q1** | `D-S5-16` | 🔴 **OPEN — the only thing Step 5 waits on** | how a *reporting* gate is scored when its own sensitivity trap fires | 🔴 **decides whether the paper ships with 2 declared FAILs** |
| **Q2** | `mktc.py` | ⚪ housekeeping, one line | whether the generator of a deliverable becomes a repo file | ⚪ no scientific content |

⚪ **`T_chosen` is not in question in either.** It is `1.30` (`es`) / `1.10` (`uk`) / `1.20` (`it`),
it rests on the **entropy** criterion, and it survived the strongest test run to date (see Q1 §4).
Neither question can move it.

---

# Q1 — `D-S5-16`: is `G5.8`'s FAIL on `es` and `uk` the terminal verdict?

## 1. The question in one paragraph

`G5.8` is the gate that guards the temperature knob. It has **two halves**: a *reporting*
obligation, and a *sensitivity trap* we wrote ourselves to stop a single-realisation curve from
passing as a function. The reporting half is satisfied on all three folds. **The sensitivity trap
fired on `es` and `uk`.** The registered text says what to do when it fires — *"the reported
deliverable is the **band**, not a chosen value"* — and that sentence can be read two ways: as a
**failure condition** (the sweep failed; report the band and say so) or as a **remedy** (deliver a
band and the obligation is met). The checker implements the first. The two readings give
**different verdicts on two folds of three**. **Only the author can choose between them**, for the
reason in §5.

## 2. The registered text, quoted exactly

**The gate row** — `Step5_docs/4thJ_05_populationLinkage_val.md:38`:

> **G5.8** Temperature calibration reported | A knob chosen without evidence | *Both the
> entropy-matching curve and the fidelity curve are reported, and **whether they agree is stated
> explicitly*** | project-chosen

**The sensitivity trap** — same file, `:45-57`, a separate section:

> The temperature sweep is a sweep of one knob. **If it is run once per temperature level with the
> noise source held fixed, the resulting curve is a single realisation presented as a function: it
> has no error bar, therefore no way to be wrong, therefore no way to fail — and the sweep always
> produces a winner.**
>
> **Requirement: every temperature level is run at least 5 times with different seeds, and the
> step-to-step difference along the curve must exceed the spread from re-running one level.** If it
> does not, the sweep has told us nothing about temperature and the reported deliverable is the
> **band**, not a chosen value.
>
> 🔴 **And if the sweep turns out to be uninformative, the correct response is not to re-tune.**
> Re-selecting on the same criterion with better statistics is still selecting on that criterion.

🔴 **Note what the gate *row* asks for and what it does not.** The row is a **reporting** obligation
only — two curves plus an explicit agreement statement. The step-vs-spread requirement lives in a
*different section* of the same register. Whether that section is a **condition of `G5.8`** or a
**separate instruction about what to publish** is exactly the ambiguity. The checker
(`tools/4thJ_gates_step5.py:520-553`) treats it as a condition and returns `False`; it never asks
whether a band was in fact delivered.

## 3. The numbers, re-derived from the artefacts

**Board:** 36 gate-fold verdicts — **34 PASS, 2 FAIL, 0 BLOCKED**. Coverage clause clean (*every
passing gate was made to fall*). Shipped populations md5-verified unchanged.

| fold | max step between adjacent `T` | max re-run spread at one `T` | ratio | `G5.8` |
|---|---|---|---|---|
| `es` | 0.9315 pp | **1.8127 pp** | **0.51×** | 🔴 **FAIL — decisively noise-dominated** |
| `uk` | 1.3994 pp | **1.4072 pp** | **0.99×** | 🔴 **FAIL — by 0.6 %** |
| `it` | **4.1114 pp** | 3.1993 pp | 1.29× | 🟢 PASS |

**The two failures are not alike, and that matters for option (c):**

* **`es`** — the spread is nearly **twice** the step. No re-reading makes this curve informative; it
  simply is not.
* **`uk`** — it fails by **0.6 %**, a ratio of `0.994`. 🔴 **This is precisely the situation in which
  the temptation to re-run is strongest and must be refused.**

⚪ Five seeds per level, ≥ 5 required. `G5.9` PASSES on all three folds and `top_p = 0.9` fells all
three. `G5.6-as-written` still FAILs 12 of 36 marginal rows — informational, superseded by
`D-S5-12`(a), **not counted in the board**.

## 4. Three measurements that arrived *after* the options were drafted, all pointing the same way

The `D-S5-16` options were written on the `uk` fold alone, before `es` landed and before the
coverage jobs. Three things have since been measured. **None was designed to answer this question**,
and all three say the fidelity curve carries no seed-stable signal on `es` or `uk`.

### (i) The coverage jobs are an accidental independent noise estimate

`1285777` / `1285778` / `1285779` re-measured, at seed `101`, **six grid points the primary sweep
already measured at seed `42`** — at six temperatures **the replicate window never reaches**. Two
realisations of the same configuration disagree by:

| fold | mean disagreement | max disagreement |
|---|---|---|
| `es` | 0.5840 pp | **1.7176 pp** |
| `uk` | 0.6100 pp | 1.2025 pp |
| `it` | 0.8407 pp | 1.2418 pp |

🔴 **On `es`, the step `G5.8` is asked to call meaningful is `0.9315` pp — smaller than two runs of
the same configuration disagree at other temperatures.** Both `G5.8` failures are therefore
corroborated **from outside the window that produced them**. This is evidence `D-S5-16` did not have
when it was drafted.

### (ii) The fidelity argmin moves under a seed change on **all three** folds

Over the full nine-point grid: `es` **0.70 → 0.60**, `uk` **1.00 → 0.90**, `it` **0.80 → 0.90** —
one grid step each, two down and one up, no systematic direction. **The fidelity temperature is a
band on every fold: `es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}.**

🔴 **The earlier bands `{1.10,1.20}` (`es`) and `{1.00,1.10}` (`uk`) are wrong as a fidelity result**
— they were argmins of a **truncated three-point window**, and on `es` and `it` the ruled
`T_fidelity` was not even inside it. Corrected in place in both docs. **Never quote the in-window
argmin.**

### (iii) `FINDING 76` — the single `agree = True` on the board does not replicate

`agree` is `True` on **exactly one fold of three** (`uk`), by a margin of `0.0001`
(`0.1000` vs `agree_tol = 0.1001`). At seed `101` the `uk` fidelity argmin moves one further grid
step away, the gap becomes `0.2000`, and **`agree` reads `False`**.

🔴 **The claim must change, not the number.** *"On the UK fold the entropy and fidelity criteria
agree"* is a property of **one realisation** and must never be written as corroboration that the two
criteria converge.

### 🟢 And the thing that did **not** move: `T_chosen`

`argmin |dH|` over **all nine** grid points, at a generation seed that played **no part** in the
selection: `es` **1.30**, `uk` **1.10**, `it` **1.20** — **identical to `T_chosen`, three folds for
three.** The earlier 5/5 stability was measured inside a three-point window; this is the whole grid.

⚪ `T_chosen` is unaffected by `FINDING 76` **by pre-registration, not by luck**: entropy wins on
disagreement (`4thJ_step5_temperature.py:607`), so `uk` selects `1.10` either way.
⚪ **`es` still chooses the top of the grid** (`endpoint_entropy = True`), so its argmin could only
move inward — a **one-sided** test. That sentence and `endpoint_entropy = True` travel together.

## 5. 🔴 Why the assistant did not resolve this

Both readings are defensible from the registered text, and they give **different verdicts on the two
folds where it matters**. **The ambiguity surfaced by running the gate and watching it fail.**
Rewriting the checker now, in the direction that turns those FAILs into PASSes, is **selecting the
test on the outcome**. It is the move `feedback_gates_must_be_seen_failing` and
`feedback_read_the_gates_own_doc` forbid, and in the record it would be **indistinguishable from
having designed the gate to pass**. The file order is checkable by anyone.

## 6. 🔴 What this question does **not** decide — stated so no option reads as re-opening it

* It **does not change `T_chosen`** on any fold. `G5.8` is a *reporting* gate.
* It **does not change `generation_config_{es,uk,it}.json`** — `T` 1.30/1.10/1.20, `top_p` 1.0,
  `top_k` 0, `max_new_tokens` 1200, base `allenai/OLMo-2-0425-1B` @ `a1847dff3500…`, per-fold
  adapter, prompt seed 42. Every field is **copied** from the calibration artefact, not chosen.
* It **does not touch `prereg.md`**, whose md5 must stay `e4243e07cdd80c9c846b91f40e3e8c45`.
* It **does not extend the `es` grid past 1.30.** That is settled and declared separately.

## 7. The options

| option | what it means | consequence |
|---|---|---|
| 🟢 **(a)** *(recommended)* | **Leave `G5.8` exactly as written.** `es` and `uk` FAIL, permanently and in the paper. The fidelity result ships as a **band** per fold (`es` {0.60,0.70}, `uk` {0.90,1.00}, `it` {0.80,0.90}) and the FAIL is reported as the reason it is a band. | Step 5 closes with **2 declared FAILs** on a 36-verdict board. Nothing re-run, nothing re-tuned, zero GPU. 🟢 **The strongest provenance available to this paper: the trap we registered in advance caught our own curve, on two folds, and we published it.** Three independent measurements (§4) support the verdict. |
| ⚪ **(b)** | **Amend `G5.8` additively** — add a second branch that PASSes when a band is delivered instead of a value, marked a post-registration erratum exactly as `FINDING 69` was, with the superseded reading printed beside the ruled one. | Board goes clean (36 PASS). ⚪ The registered perturbation *"report only the fidelity curve"* still fells the gate through the **reporting** branch, so the coverage clause survives. 🔴 **But the amendment is written *after* seeing which folds fail, and the file order is checkable.** Only defensible if you judge the registered text **unambiguously** meant a remedy. 🔴 Weakened further by §4: on `es` the step is smaller than pure re-run noise, so a band is not a *deliverable* there — it is an admission. |
| 🔴 **(c)** | **Re-run `uk` (and/or `es`) at more seeds or more prompts** until the step clears the noise. | 🔴 **Reject.** The register forbids it in its own words: *"if the sweep turns out to be uninformative, the correct response is not to re-tune."* `n = 600 × 5` is not the binding constraint — the `uk` curve is genuinely flat between 1.00 and 1.10 (means 3.142 vs 3.425 pp, sd 0.56 / 0.47). On `uk` it would move a verdict across a line it sits **0.6 %** from; on `es` it cannot work at all. |

**If (a):** I close Step 5, write the two FAILs into the val doc as the terminal verdict, and tick
boxes 2, 4 and 9 of `IMP/2026-08-21_review-derived-improvements.md`. Step 6/7/8/9 resumes.
**If (b):** I write the erratum, re-run the `G5.8`/`G5.9` selftest and the full battery, and show
the perturbation still felling the gate — then close Step 5.
**If (c):** I write the sbatch scripts and Step 5 stays open another day. *(Not recommended.)*

---

# Q2 — `mktc.py`: should the generator of a deliverable live in the repo?

## The facts

* `Step5_docs/outputs_step5/temperature_calibration.md` — **530 lines, md5
  `cf8f441e37e124fb68fbad47c7c49b5f`** — is the last Step 5 deliverable.
* 🔴 **Every number in it is READ from the JSON artefacts. None is transcribed.** The document tells
  its own reader: *regenerate it, never hand-edit it.*
* The generator that produces it, `mktc.py`, is **740 lines / 40 KB** and currently lives in a
  **session scratchpad** (`…\2516ff0a-…\scratchpad\mktc.py`), which is temporary by design.

## Why it is a question at all

If the scratchpad is cleared, the document's own instruction becomes **unfollowable**, and the next
person to touch `temperature_calibration.md` has only two choices: hand-edit it (which it forbids)
or rewrite 740 lines. Every other Step 5 tool — `4thJ_step5_temperature.py`,
`4thJ_step5_athome_selftest.py`, `4thJ_gates_step5.py`, and 15 more — already lives in `tools/`.

⚪ I did not create it there because **no one asked for a new repo file**, and adding files to the
repo unasked is not mine to do.

| option | what it means | consequence |
|---|---|---|
| 🟢 **(a)** *(recommended)* | Move it to **`tools/4thJ_step5_mk_calibration_doc.py`**, matching the naming of every other Step 5 tool. | The *regenerate, never hand-edit* instruction stays followable. One new repo file, no behaviour change; I verify it reproduces the current md5 `cf8f441e…` byte-for-byte before and after the move. |
| ⚪ **(b)** | Leave it in the scratchpad. | No new repo file. `temperature_calibration.md` becomes a **frozen** artefact in practice, and its regeneration instruction should then be **removed or reworded**, because it would be an instruction nobody can carry out. |

---

## Answer box

> **Q1 — `D-S5-16`:**  (a) / (b) / (c)  → **(a) Leave `G5.8` exactly as written — `es` and `uk` FAIL as the terminal verdict; deliver fidelity as a band per fold.**
>
> **Q2 — `mktc.py`:**  (a) move to `tools/` / (b) leave  → **(a) Move to `tools/4thJ_step5_mk_calibration_doc.py`.**

---

## Author's Rulings & Responses (2026-08-22)

| # | Item | Ruled Option | Decision Summary | Action Required |
|---|---|---|---|---|
| **Q1** | `D-S5-16` | 🟢 **Option (a)** | **Leave `G5.8` as written.** The FAIL on `es` and `uk` is the **terminal verdict**. Fidelity is delivered as a band per fold (`es` {0.60, 0.70}, `uk` {0.90, 1.00}, `it` {0.80, 0.90}). | Record the 2 declared FAILs on the 36-verdict board (34 PASS, 2 FAIL, 0 BLOCKED); close Step 5; tick boxes 2, 4, 9 in `IMP/2026-08-21_review-derived-improvements.md`. |
| **Q2** | `mktc.py` | 🟢 **Option (a)** | **Move to `tools/4thJ_step5_mk_calibration_doc.py`**. | Place generator into `tools/`, matching standard project naming; ensure regeneration is reproducible and byte-exact against md5 `cf8f441e37e124fb68fbad47c7c49b5f`. |

---

### Detailed Rulings and Directives

#### 1. Q1 (`D-S5-16`) — Ruled: Option (a)
* **Choice**: Leave `G5.8` exactly as written. The sensitivity trap firing on `es` and `uk` is accepted as the permanent terminal verdict.
* **Rationale**:
  1. **Pre-registration integrity**: Modifying the gate checker post-hoc after observing which folds fail violates the project's non-negotiable principle (`feedback_gates_must_be_seen_failing`). The registered text was clear: *"if the sweep turns out to be uninformative, the correct response is not to re-tune"*.
  2. **Strongest provenance and scientific transparency**: Publishing with 2 declared FAILs out of 36 verdicts (34 PASS, 2 FAIL, 0 BLOCKED) provides unassailable credibility. It demonstrates that the pre-registered sensitivity trap caught our own curves and was not retrofitted or relaxed to force a clean board.
  3. **Robustness of `T_chosen`**: `T_chosen` (entropy matching: `es` **1.30**, `uk` **1.10**, `it` **1.20**) is 100% stable across the full 9-point grid and across independent random seeds (101 vs 42). The fidelity optimum is accurately reported as an empirical band per fold:
     - `es`: **{0.60, 0.70}**
     - `uk`: **{0.90, 1.00}**
     - `it`: **{0.80, 0.90}**
* **Directives**:
  - Close Step 5 with the 2 declared FAILs recorded in the validation document.
  - Tick boxes 2, 4, and 9 of `IMP/2026-08-21_review-derived-improvements.md`.
  - Resume Step 6/7/8/9 pipeline execution.

#### 2. Q2 (`mktc.py`) — Ruled: Option (a)
* **Choice**: Move `mktc.py` to `tools/4thJ_step5_mk_calibration_doc.py`.
* **Rationale**:
  1. Follows the explicit instruction in `temperature_calibration.md` (*"Regenerate rather than edit"*).
  2. Guarantees long-term reproducibility by keeping all generation tools in the repository under standard naming conventions (`4thJ_step5_*`).
* **Directives**:
  - Move/save script as `tools/4thJ_step5_mk_calibration_doc.py`.
  - Confirm that regenerating `temperature_calibration.md` matches md5 `cf8f441e37e124fb68fbad47c7c49b5f`.

---

⚪ `prereg.md` md5 `e4243e07cdd80c9c846b91f40e3e8c45` remains untouched and verified. Nothing is running on Speed.
